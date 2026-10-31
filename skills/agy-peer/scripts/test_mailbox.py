#!/usr/bin/env python3
"""Behavioral checks for delivery, retry, reply routing and process binding."""
import concurrent.futures
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import mailbox as peer


def concurrent_post(state, index):
    db = peer.open_db(state)
    try:
        row, created = peer.post(db, 'agy', 'codex', '消息 '+str(index), mid='parallel-'+str(index))
        return row['id'], created
    finally:
        db.close()


class MailboxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='agy-peer-test-')
        self.state = Path(self.tmp.name)
        self.db = peer.open_db(self.state)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_round_trip_and_ack_are_distinct(self):
        request, _ = peer.post(self.db, 'codex', 'agy', '中文\n多行正文', mid='request')
        received = peer.receive(self.db, 'agy')[0]
        self.assertEqual(received['body'], request['body'])
        self.assertIsNotNone(received['received_at'])
        self.assertIsNone(received['ack_at'])
        peer.acknowledge(self.db, 'request', 'agy')
        self.assertEqual(peer.receive(self.db, 'agy'), [])
        self.assertEqual(peer.receive(self.db, 'codex'), [])
        peer.post(self.db, 'agy', 'codex', '已完成', kind='result', reply_to='request')
        self.assertEqual(peer.receive(self.db, 'codex')[0]['reply_to'], 'request')

    def test_idempotent_retry_rejects_changed_content(self):
        first, created = peer.post(self.db, 'codex', 'agy', 'original', mid='stable')
        second, repeated = peer.post(self.db, 'codex', 'agy', 'original', mid='stable')
        self.assertTrue(created)
        self.assertFalse(repeated)
        self.assertEqual(first, second)
        with self.assertRaises(ValueError):
            peer.post(self.db, 'codex', 'agy', 'changed', mid='stable')
        self.assertEqual(len(peer.receive(self.db, 'agy')), 1)

    def test_unacknowledged_message_survives_receiver_restart(self):
        peer.post(self.db, 'agy', 'codex', 'question', mid='restart')
        peer.receive(self.db, 'codex')
        self.db.close()
        self.db = peer.open_db(self.state)
        self.assertEqual(peer.receive(self.db, 'codex')[0]['id'], 'restart')
        peer.acknowledge(self.db, 'restart', 'codex')
        peer.acknowledge(self.db, 'restart', 'codex')
        n = self.db.execute("SELECT count(*) FROM events WHERE event='acknowledged'").fetchone()[0]
        self.assertEqual(n, 1)

    def test_reply_and_ack_cannot_use_wrong_role(self):
        peer.post(self.db, 'codex', 'agy', 'task', mid='parent')
        with self.assertRaises(ValueError):
            peer.acknowledge(self.db, 'parent', 'codex')
        with self.assertRaises(ValueError):
            peer.post(self.db, 'codex', 'agy', 'wrong reply', reply_to='parent')
        with self.assertRaises(ValueError):
            peer.post(self.db, 'agy', 'codex', 'unknown reply', reply_to='missing')

    def test_independent_concurrent_writers_preserve_all_messages(self):
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(concurrent_post, [str(self.state)]*24, range(24)))
        self.assertEqual(len({mid for mid, _ in results}), 24)
        rows = peer.receive(self.db, 'codex', limit=100)
        self.assertEqual(len(rows), 24)
        self.assertEqual(len({r['seq'] for r in rows}), 24)

    def test_wait_returns_when_a_message_arrives(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            def delayed():
                time.sleep(.15)
                return concurrent_post(str(self.state), 99)
            future = pool.submit(delayed)
            rows = peer.receive(self.db, 'codex', timeout=2)
            future.result()
        self.assertEqual(rows[0]['id'], 'parallel-99')

    def test_stale_process_and_conversation_binding_are_rejected(self):
        binding = {'pid': 42, 'start_time': '123', 'conversation_id': 'a',
                   'tty': '/dev/pts/4', 'cwd': '/tmp', 'foreground': True}
        (self.state/'binding.json').write_text(json.dumps(binding))
        for key, value in [('start_time','124'), ('conversation_id','b'), ('foreground',False)]:
            with patch.object(peer, 'process_identity', return_value={**binding,key:value}):
                with self.assertRaises(ValueError):
                    peer.validate_binding(self.state)

    def test_shared_or_symlink_state_is_rejected(self):
        os.chmod(self.state, 0o755)
        with self.assertRaises(ValueError):
            peer.open_db(self.state)
        os.chmod(self.state, 0o700)
        link = self.state/'alias'
        link.symlink_to(self.state, target_is_directory=True)
        with self.assertRaises(ValueError):
            peer.open_db(link)


if __name__ == '__main__':
    os.umask(0o077)
    unittest.main()
