# Bookcase publication for mindbuffer books

This deployment applies to the user's books under `mindbuffer/books/`. Other
workspaces continue using their own explicit artifact contracts.

The reading authority is `/share/motecosmos/bookcase/`, backed by the private
`quboliu/bookcase` repository. The user edits its PDFs directly with Mac
Highlights. Read both the books and bookcase `AGENTS.md` before publishing.

## Compile, transfer, then move

1. Ask the user to save and close the affected PDF in Highlights when the user
   has not already confirmed this operation. A server cannot inspect unsaved
   application memory; file locks do not make an open reader cooperate.
2. Update the content authority and derived Typst appropriately. Build all
   required editions into the book's own `output/` and run its complete quality
   gates. Cover timestamps, diagnostics, fonts, source maps and duplex rules
   remain mandatory. Do not compile directly into the reading shelf.
3. Use the existing centralized builder with `--reader-closed`, or, after the
   book-local build and validation, run
   `python3 mindbuffer/books/scripts/bookcase.py publish <book-output-pdf> --reader-closed`.
   This flag records the actual saved/closed operation; it never disables
   annotation validation.
4. The publisher immediately commits/pushes the latest saved old
   PDF and verifies remote acknowledgement, migrates its native annotations, checks the result, atomically replaces
   the reading file, and immediately commits/pushes the new file. Only a
   verified remote acknowledgement permits removal of the output candidate.
5. Commit/push source and policy changes in mindbuffer too. Reopen the new
   reading PDF in Highlights after publication.

## Reading selection and mandatory naming

Only Chinese-original Chinese editions and English-original bilingual editions
enter bookcase. Keep required English-only and translated Chinese builds local;
do not publish proof pages, chapter extracts, source scans or abbreviated copies.

Use the complete original book title, normalize Latin letters to lowercase and
spaces/punctuation to hyphens, then append `-zh.pdf` or `-dual.pdf`. Preserve
complete Chinese titles with lowercase Latin letters. Register exact titles,
filenames and projects in `mindbuffer/books/bookcase-registry.json`; reject
generic `book.pdf`, short project aliases and missing language suffixes.
Inherited compiler filenames are internal staging names; the formal output
candidate must receive its complete-title name inside `output/build/` before
the move. There are no PDF symlinks in `mindbuffer/export/`; that directory may
retain audit records and metadata indices.

## Annotation authority and fallback

Use the current saved reading file, not a stale Git version or an unannotated
build baseline. Preserve comments, colors, dates, authors, popup/reply links,
appearances and opaque application data. Reflow requires content matching and
updated geometry; old page numbers alone are not sufficient.

Deleted, substantially rewritten or ambiguously located excerpts become
individual notes at the corresponding chapter heading. Retain the original
quotation, original comment, old page and native annotation snapshot. If the
chapter disappears, collect the notes at the book title with the old chapter
identified. The user decides later in Highlights whether to delete or move them.
Do not silently discard notes or guess a repeated excerpt. Verify every old
identity has one outcome and repeated migration does not create duplicates.
User-initiated deletion of notes is legitimate; never revive them from history.

## Operational checks

The publisher, Git hooks and reading-change watcher enforce the workflow.
Never bypass hooks or rewrite delivered reading history. The user explicitly
requires this new bookcase to be handed off with one clean initial commit.
Only its pre-handoff bootstrap history may be consolidated by finalize-import,
after verifying every registered PDF and absence of subsequent reader changes,
with an exact remote lease and the hook-approved initial-seal permit. Push failures retain local commits and
candidates, report pending remote backup and pause further publication.
The watcher saves stable reader changes immediately after a short write
debounce. Inspect `.git/bookcase-status.json` and the user service journal.

Use PyMuPDF and pikepdf for annotation and page validation. Verify native-object
retention, reflow, chapter fallback, popup/reply links, idempotence, filename
guards and concurrent writes with the actual publisher regression suite.
Do not claim that server checks constitute a visual test in Mac Highlights.

## Avoid redundant full-PDF copies

Git history (or Git LFS for large files) is the persistent version store for
reading PDFs. Do not create initial-import backups, old-PDF publication
snapshots, previous-version directories or permanent whole-book duplicates.
Recover the saved old reader PDF from its verified Git commit; migration
receipts record that commit instead of a local backup path.

Keep only the temporary files needed for migration, deterministic validation
and atomic replacement. Remove them after success. On failure retain the
current unpublished candidate and necessary diagnostics, rather than whole
old-book copies. Do not strip native annotation data or discard meaningful
Git history to reduce space. Required English/Chinese/bilingual editions and
user-requested chapter printing are distinct deliverables, not backup copies;
verify their repeated builds and clean temporary proof outputs.
