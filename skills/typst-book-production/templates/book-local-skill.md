---
name: <book-slug>
description: Handle source recovery, conversion, and publication rules specific to <book-title>.
---

# <book-title>

## Authority and regeneration

- Record the exact raw inputs and checksums used.
- For Git-derived raw material, record the upstream URL and fixed commit; keep
  the frozen working tree free of nested `.git` metadata and submodules.
- Record the command that regenerates Markdown chapters and images.
- Record the commands that regenerate each Typst edition.
- Record any legacy-path inventory, duplicate hashes, and recoverable quarantine
  location used during migration. Do not retain compatibility aliases.
- Record the stable semantic-label scheme that replaces source-page anchors in
  generated cross-references.

## Book-specific rules

- Document only rules that differ from or refine `typst-book-production`.
- State formula, code, image, table, footnote, and terminology decisions that
  affect faithful conversion.

## Scripts and dependencies

- Keep book-specific executable helpers under `scripts/`.
- Pin nonstandard dependencies and give each script's input, output, and
  acceptance check.
- Record the exact release compile command and raw diagnostics-log path; release
  builds must produce no unresolved Typst diagnostics.

## Known anomalies and pitfalls

- Record reproducible source defects, approved corrections, unresolved
  questions, and traps that a future regeneration must avoid.
