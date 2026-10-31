#!/usr/bin/env python3
"""Durable, local, bidirectional messages between independently running agents."""
import argparse
import array
import ctypes
import fcntl
import json
import os
from pathlib import Path
import re
import shlex
import sqlite3
import sys
import time
import uuid


def emit(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def process_identity(pid):
    root = Path('/proc') / str(pid)
    if root.stat().st_uid != os.getuid():
        raise ValueError('Target process belongs to a different user')
    fields = (root / 'stat').read_text().rsplit(')', 1)[1].split()
    name = (root / 'comm').read_text().strip()
    if name != 'agy':
        raise ValueError('Target is not an agy process')
    tty = os.readlink(root / 'fd/0')
    if not re.fullmatch(r'/dev/pts/\d+', tty):
        raise ValueError('Target does not have an interactive PTY')
    conversations = []
    for fd in (root / 'fd').iterdir():
        try:
            target = Path(os.readlink(fd))
        except OSError:
            continue
        if target.parent.name == 'presence' and target.suffix == '.lock':
            conversations.append(target.stem)
    if len(conversations) != 1:
        raise ValueError('Cannot identify exactly one active conversation')
    return {'pid': pid, 'start_time': fields[19], 'conversation_id': conversations[0],
            'tty': tty, 'cwd': os.readlink(root / 'cwd'),
            'foreground': fields[2] == fields[5]}


def secure_dir(path, create=False):
    path = Path(path).absolute()
    if path.is_symlink():
        raise ValueError('State directory must not be a symlink')
    if create:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
    st = path.stat()
    if st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise ValueError('State directory must be owned by this user with mode 0700')
    return path


def open_db(state):
    state = secure_dir(state)
    dbpath = state / 'mailbox.db'
    if dbpath.is_symlink():
        raise ValueError('Mailbox database must not be a symlink')
    fd = os.open(dbpath, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    st = os.fstat(fd)
    os.close(fd)
    if st.st_uid != os.getuid() or st.st_mode & 0o077:
        raise ValueError('Mailbox database must be private to this user')
    db = sqlite3.connect(dbpath, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    db.executescript('''
      CREATE TABLE IF NOT EXISTS messages (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        id TEXT UNIQUE NOT NULL, sender TEXT NOT NULL, recipient TEXT NOT NULL,
        kind TEXT NOT NULL, body TEXT NOT NULL, reply_to TEXT,
        created_at REAL NOT NULL, received_at REAL, ack_at REAL,
        FOREIGN KEY(reply_to) REFERENCES messages(id));
      CREATE TABLE IF NOT EXISTS events (
        seq INTEGER PRIMARY KEY AUTOINCREMENT, at REAL NOT NULL,
        event TEXT NOT NULL, message_id TEXT NOT NULL, actor TEXT NOT NULL);
    ''')
    db.execute('PRAGMA foreign_keys=ON')
    return db


def event(db, action, mid, actor):
    db.execute('INSERT INTO events(at,event,message_id,actor) VALUES(?,?,?,?)',
               (time.time(), action, mid, actor))


def post(db, sender, recipient, body, kind='message', mid=None, reply_to=None):
    if sender == recipient or {sender, recipient} != {'codex', 'agy'}:
        raise ValueError('Messages must cross between codex and agy')
    if not body.strip():
        raise ValueError('Message body is empty')
    mid = mid or str(uuid.uuid4())
    if not re.fullmatch(r'[a-zA-Z0-9_.-]{1,120}', mid):
        raise ValueError('Invalid message id')
    db.execute('BEGIN IMMEDIATE')
    try:
        old = db.execute('SELECT * FROM messages WHERE id=?', (mid,)).fetchone()
        values = (sender, recipient, kind, body, reply_to)
        if old:
            if tuple(old[k] for k in ('sender', 'recipient', 'kind', 'body', 'reply_to')) != values:
                raise ValueError('Message id already exists with different content')
            db.commit()
            return dict(old), False
        if reply_to:
            parent = db.execute('SELECT * FROM messages WHERE id=?', (reply_to,)).fetchone()
            if not parent or parent['sender'] != recipient or parent['recipient'] != sender:
                raise ValueError('Reply must address the sender of an existing incoming message')
        db.execute('INSERT INTO messages(id,sender,recipient,kind,body,reply_to,created_at) '
                   'VALUES(?,?,?,?,?,?,?)', (mid, *values, time.time()))
        event(db, 'posted', mid, sender)
        db.commit()
        return dict(db.execute('SELECT * FROM messages WHERE id=?', (mid,)).fetchone()), True
    except BaseException:
        db.rollback()
        raise


def receive(db, recipient, timeout=0, limit=10):
    deadline = time.monotonic() + timeout
    while True:
        db.execute('BEGIN IMMEDIATE')
        rows = db.execute('SELECT * FROM messages WHERE recipient=? AND ack_at IS NULL '
                          'ORDER BY seq LIMIT ?', (recipient, limit)).fetchall()
        for row in rows:
            if row['received_at'] is None:
                db.execute('UPDATE messages SET received_at=? WHERE id=?', (time.time(), row['id']))
                event(db, 'received', row['id'], recipient)
        db.commit()
        if rows:
            return [dict(db.execute('SELECT * FROM messages WHERE id=?', (r['id'],)).fetchone()) for r in rows]
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return []
        time.sleep(min(0.25, remaining))


def acknowledge(db, mid, actor):
    db.execute('BEGIN IMMEDIATE')
    try:
        row = db.execute('SELECT * FROM messages WHERE id=?', (mid,)).fetchone()
        if not row or row['recipient'] != actor:
            raise ValueError('Only the named recipient may acknowledge this message')
        if row['ack_at'] is None:
            now = time.time()
            db.execute('UPDATE messages SET received_at=COALESCE(received_at,?),ack_at=? WHERE id=?',
                       (now, now, mid))
            event(db, 'acknowledged', mid, actor)
        db.commit()
    except BaseException:
        db.rollback()
        raise


def validate_binding(state):
    binding = json.loads((secure_dir(state) / 'binding.json').read_text())
    now = process_identity(binding['pid'])
    for key in ('pid', 'start_time', 'conversation_id', 'tty', 'cwd'):
        if binding[key] != now[key]:
            raise ValueError('Stale session binding: ' + key + ' changed; rediscover and attach explicitly')
    if not now['foreground']:
        raise ValueError('agy is not in the foreground of its terminal')
    return binding


def pty_master(index):
    # pidfd_getfd duplicates an existing descriptor. Opening /proc/PID/fd/FD for
    # /dev/ptmx would allocate a different PTY and must never be used here.
    if not hasattr(os, 'pidfd_open') or os.uname().machine not in ('aarch64', 'x86_64'):
        raise ValueError('Automatic attachment supports Linux arm64/x86-64 with pidfd_open')
    libc = ctypes.CDLL(None, use_errno=True)
    denied = False
    for process in Path('/proc').iterdir():
        if not process.name.isdigit():
            continue
        try:
            if process.stat().st_uid != os.getuid():
                continue
            fds = list((process / 'fdinfo').iterdir())
        except OSError:
            continue
        for info in fds:
            try:
                if not re.search(r'^tty-index:\s*' + str(index) + r'\s*$', info.read_text(), re.M):
                    continue
                pfd = os.pidfd_open(int(process.name))
                try:
                    fd = libc.syscall(438, pfd, int(info.name), 0)
                finally:
                    os.close(pfd)
                if fd < 0:
                    denied = True
                    continue
                number = array.array('I', [0])
                try:
                    fcntl.ioctl(fd, 0x80045430, number, True)
                    if number[0] == index:
                        return fd
                except OSError:
                    pass
                os.close(fd)
            except OSError:
                continue
    reason = 'permission denied' if denied else 'PTY master not found'
    raise ValueError(reason + '; use manual terminal attachment; do not change ptrace or system permissions')


def wake(state, script):
    binding = validate_binding(state)
    command = ('Codex peer message: run ' + shlex.join([sys.executable, str(script), 'receive',
               '--state', str(Path(state).absolute()), '--to', 'agy', '--timeout', '1']) +
               ' and follow the received task. Reply through this mailbox, then acknowledge the task.')
    if not command.isascii() or any(ord(c) < 32 for c in command):
        raise ValueError('Automatic wake requires ASCII paths; paste the receive command manually instead')
    lock_path = Path(state) / 'wake.lock'
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fd = pty_master(int(binding['tty'].rsplit('/', 1)[1]))
        try:
            validate_binding(state)
            payload = command.encode()
            if os.write(fd, payload) != len(payload):
                raise ValueError('Partial terminal write; inspect the draft, do not retry automatically')
            time.sleep(0.3)
            if os.write(fd, b'\r') != 1:
                raise ValueError('Enter key was not written; inspect terminal before retrying')
        finally:
            os.close(fd)
    return {'wake_sent': True, 'pid': binding['pid'], 'conversation_id': binding['conversation_id'],
            'delivery_confirmed': False}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('discover')
    init = sub.add_parser('init'); init.add_argument('--state', required=True); init.add_argument('--pid', type=int, required=True)
    for name in ('post', 'receive', 'ack', 'history', 'events', 'status', 'wake'):
        s = sub.add_parser(name); s.add_argument('--state', required=True)
        if name == 'post':
            s.add_argument('--from', dest='sender', choices=['codex','agy'], required=True)
            s.add_argument('--to', dest='recipient', choices=['codex','agy'], required=True)
            g = s.add_mutually_exclusive_group(required=True); g.add_argument('--text'); g.add_argument('--file')
            s.add_argument('--kind', choices=['message','task','question','answer','result','stop'], default='message')
            s.add_argument('--id'); s.add_argument('--reply-to')
        elif name == 'receive':
            s.add_argument('--to', dest='recipient', choices=['codex','agy'], required=True)
            s.add_argument('--timeout', type=float, default=30); s.add_argument('--limit', type=int, default=10)
        elif name == 'ack':
            s.add_argument('--id', required=True); s.add_argument('--by', dest='actor', choices=['codex','agy'], required=True)
        elif name in ('history','events'):
            s.add_argument('--after', type=int, default=0)
        elif name == 'wake':
            s.add_argument('--idle-confirmed', action='store_true', help='Assert that the terminal is idle with an empty prompt, not being typed into')
    return p


def main():
    args = parser().parse_args()
    if args.command == 'discover':
        peers = []
        for p in Path('/proc').iterdir():
            if p.name.isdigit():
                try:
                    peers.append(process_identity(int(p.name)))
                except (OSError, ValueError, IndexError):
                    pass
        emit(peers); return
    if args.command == 'init':
        state = secure_dir(args.state, create=True)
        binding = process_identity(args.pid)
        path = state / 'binding.json'
        if path.exists():
            if json.loads(path.read_text()) != binding:
                raise ValueError('Existing state is bound to a different session; use a new state directory')
        else:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w') as out:
                json.dump(binding, out, ensure_ascii=False, indent=2)
        open_db(state).close(); emit(binding); return
    if args.command == 'wake':
        if not args.idle_confirmed:
            raise ValueError('Inspect the terminal for an empty idle prompt before using --idle-confirmed')
        emit(wake(args.state, Path(__file__).resolve())); return
    with open_db(args.state) as db:
        if args.command == 'post':
            body = Path(args.file).read_text() if args.file else args.text
            row, created = post(db, args.sender, args.recipient, body, args.kind, args.id, args.reply_to)
            emit({'created': created, 'message': row})
        elif args.command == 'receive':
            if not 0 <= args.timeout <= 60 or not 1 <= args.limit <= 100:
                raise ValueError('Use a 0–60 second wait and a 1–100 message limit')
            emit({'messages': receive(db, args.recipient, args.timeout, args.limit)})
        elif args.command == 'ack':
            acknowledge(db, args.id, args.actor); emit({'acknowledged': args.id, 'by': args.actor})
        elif args.command in ('history','events'):
            table = 'messages' if args.command == 'history' else 'events'
            emit([dict(r) for r in db.execute('SELECT * FROM '+table+' WHERE seq>? ORDER BY seq', (args.after,))])
        elif args.command == 'status':
            binding = validate_binding(args.state)
            counts = {r[0]: r[1] for r in db.execute('SELECT recipient,count(*) FROM messages WHERE ack_at IS NULL GROUP BY recipient')}
            emit({'binding': binding, 'unacknowledged': counts})


if __name__ == '__main__':
    os.umask(0o077)
    try:
        main()
    except (OSError, ValueError, sqlite3.Error) as exc:
        emit({'error': str(exc)})
        raise SystemExit(1)
