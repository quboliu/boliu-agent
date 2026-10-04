---
name: bookcase-publish
description: Publish validated book reading PDFs to a user-selected private bookcase repository, migrate Highlights annotations, and immediately commit and push. Use alongside book production skills after complete reading editions are exported or replaced, or when checking bookcase synchronization. Resolve locations from local configuration or ask the user before publication.
---

# Bookcase Publish
made by quboliu

Complete the chain from validated book-local output to the reading shelf:
push the old reader’s latest annotations, migrate and validate, replace
atomically, then immediately commit and push the new reader.

## Resolve the user’s locations

The shared skill has no machine-specific source or destination defaults.
Read `${XDG_CONFIG_HOME:-$HOME/.config}/bookcase-publish/config.json` if present:

- `books_root`: absolute directory containing book projects and the source registry.
- `bookcase_root`: absolute directory of the reading PDF Git repository.

These are machine-local defaults. Explicit user paths for the current task take
precedence. If either is unknown, ask the user for the books source directory and
reading repository before publishing. Do not infer a new workspace, create a
repository or persist assumed paths. Once confirmed, save local defaults when
requested or appropriate for the installation. Keep this configuration outside
the skill and its published mirror; never embed its values in shared docs.

Resolve symlinks and read both repositories’ and the affected book’s AGENTS.md.
Locate maintained tools from their instructions. The existing deployment uses
`bookcase-registry.json`, `scripts/bookcase.py`, `scripts/export_books.py` and
`bookcase-workflow.md` relative to `books_root`; the reader repository has
`.bookcase/registry.json` and a `.bookcase/` runtime. If the layout differs,
resolve missing entrypoints with the user. Call existing code rather than
copying the publisher into the skill or creating a second implementation.

Examples use safely quoted shell variables `BOOKS_ROOT` and `BOOKCASE_ROOT`
set from resolved configuration. Always pass the destination explicitly.
Check `git -C "$BOOKCASE_ROOT" config --get bookcase.booksRoot` matches the
source directory. Set a missing local value from confirmed paths; resolve
conflicting values with the user. Inspect build entrypoints for remaining
machine-specific assumptions before running them on another host.

## Choose and build the reading edition

Publish only a Chinese original’s complete Chinese edition (`zh`) or an English
original’s complete bilingual edition (`dual`). Other required editions remain
local. Chapter printing stays in the book’s own `output/chapters/`; scans,
excerpts and proofs remain local too.

Use the registry’s exact complete-title filename: lowercase Latin letters,
hyphens, then `-zh.pdf` or `-dual.pdf`. Preserve complete Chinese titles.
Compiler aliases are internal names; the publisher stages the formal candidate
in the book’s `output/build/`. Do not create export PDF symlinks.

Use the book’s production skill to build its required edition matrix in its own
`output/` and pass existing quality gates. The publisher requires an empty
`output/audit/compile.log`. All existing covers must contain the same visible,
searchable `YYYY-MM-DD HH:mm:ss UTC` batch timestamp passed through
`--input export-timestamp=...`. Never compile directly into the reading shelf.

## Publish after export

1. Establish that the affected PDF was actually saved and closed in Mac
   Highlights before replacement. Existing confirmation for this operation
   suffices. Otherwise ask for confirmation while continuing source work and
   local builds; wait before replacement. Explain that unsaved application
   notes are invisible to the server. `--reader-closed` records this fact;
   never treat it as an assumption or validation bypass.
2. Use the supported central builder or publish the validated local candidate.
   Check the builder’s current help and source roots instead of assuming it
   supports every book. If it already published, verify without publishing
   twice. Direct Typst compilation and independent local builds alone do not
   complete publication.
3. Let the publisher commit and push the latest saved old reader first,
   verify remote acknowledgement, migrate every native annotation, validate,
   and replace atomically. It then immediately commits and pushes the new
   reader. Remote acknowledgement is required before reporting completion or
   removing the candidate. Never replace a reading PDF via direct cp/mv.
4. Commit and push affected source, configuration and audit changes in their
   owning source repository too, preserving unrelated work. Report the final
   PDF path, verified commit, migration outcome and chapter fallback notes.
   Tell the user to reopen the PDF in Highlights. Server checks do not establish
   how Highlights visually renders it.

Supported central builder, with a slug obtained from its current help:

```bash
python3 "$BOOKS_ROOT/scripts/export_books.py" \
  --books <registered-slug> --output "$BOOKCASE_ROOT" --reader-closed
```

Independently built and validated registered reading edition:

```bash
python3 "$BOOKS_ROOT/scripts/bookcase.py" --bookcase "$BOOKCASE_ROOT" \
  publish '<absolute candidate PDF path inside this book’s output>' --reader-closed
```

## Preserve annotation meaning and native data

The current saved reader PDF is authoritative. Retain native identity, comments,
colors, authors, dates, appearances, popups, replies and opaque application data.
Reflow requires content matching and updated geometry; old coordinates alone
are insufficient.

Deleted, substantially rewritten or ambiguously located text causes each note
to be collected at the corresponding chapter heading, retaining its original
excerpt, comment, old page and original native annotation data. If the chapter
vanished, collect at the book title and identify the old chapter. The user later
deletes or manually relocates these notes in Highlights.

Every old annotation must have one migration outcome. Failed identity,
attribute, count or body checks block replacement. Repeated migration must not
duplicate notes. User deletion is legitimate; never revive notes from history.

## Synchronization, failure and storage

The existing bookcase-watch.service observes saved reader PDFs every two seconds
and commits and pushes after writes are stable for five seconds. It does not
watch book outputs or publish new builds; invoke the publisher. On another
host, locate its configured monitoring service rather than assuming Linux.

```bash
python3 "$BOOKS_ROOT/scripts/bookcase.py" --bookcase "$BOOKCASE_ROOT" sync
systemctl --user status bookcase-watch.service
journalctl --user -u bookcase-watch.service --since today
```

Check the reader repository’s `.git/bookcase-status.json`, clean tracked status
and matching local/remote branch tips. An active watcher alone does not prove a
successful push. On failure, preserve the local commit, current reader and
unpublished candidate, report pending remote synchronization and pause further
publication. Resolve the cause and use sync to retry; verified sync cleans
matching pending candidates. Never bypass hooks or retry indefinitely.

Git history is the persistent version store; the current publisher uses per-file
LFS at 90 MiB or above. No initial migration copies, old-reader snapshots,
previous/backup directories or hidden full PDFs/archives in metadata. Clean
operation temporaries after success; failures retain only the current candidate
and necessary diagnostics. Preserve reading history. Do not force-push,
reinitialize or run initial-import/history-sealing commands on a delivered shelf.

As a temporary local storage measure, a normal `publish` runs a wide-window
delta repack after remote acknowledgement: `git repack -Adf --window=250
--depth=50`. This only reorganizes local reachable Git objects; it does not
prune history, rewrite commits, or clean LFS. Retry it manually with:

```bash
python3 "$BOOKS_ROOT/scripts/bookcase.py" --bookcase "$BOOKCASE_ROOT" repack
```

If repacking fails after the remote publication was verified, keep the local
candidate, repair the cause, run `repack`, then run `sync` to clean matching
published candidates. Do not treat a successful repack as a replacement for
remote acknowledgement.

For new books, register the complete title, source language, reading project,
edition, exact filename and build path in source and shelf registries before
normal publication. Bootstrap commands cannot bypass validation.

Publisher implementation changes require its existing isolated regression suite;
skill/documentation changes do not require exporting real PDFs:

```bash
python3 -m unittest discover -s "$BOOKS_ROOT/scripts" -p test_bookcase.py -v
```
