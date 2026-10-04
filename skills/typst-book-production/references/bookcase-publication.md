# Bookcase publication entrypoint

The export-to-reading-shelf workflow is maintained in the independent
`bookcase-publish` skill. Load its SKILL.md from the installed user skill
directory before publishing or replacing a reading PDF. Its repository mirror
is `skills/bookcase-publish/SKILL.md` in `quboliu/boliu-agent`.

That skill resolves source and reading directories from machine-local
configuration, or asks the user when unknown. Shared skill text must not
prescribe a machine-specific destination. It owns reading-edition selection,
full-title naming, Highlights annotation migration, atomic replacement,
immediate commit/push, watcher verification and storage constraints.

Continue applying typst-book-production and book-local quality gates to source
updates and compilation. The publisher performs the final annotated-reader
replacement after successful local build validation.
