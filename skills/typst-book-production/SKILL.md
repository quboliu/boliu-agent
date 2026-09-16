---
name: typst-book-production
description: Produce and maintain publication-quality Typst books in Chinese, English, or adjacent Chinese-English bilingual editions. Use when converting or maintaining a book, long-form manuscript, or paginated source as a reproducible Typst PDF.
---

# Typst Book Production

made by quboliu

Produce a faithful, maintainable, and reproducible Typst book. This is a
general production core: each book supplies its own source authority, language
policy, typography, semantic macros, terminology, and exceptions.

## Select the edition

At the start, identify one edition and record it in the book contract:

- `monolingual-zh`: a Chinese-only edition.
- `monolingual-en`: an English-only edition.
- `bilingual`: adjacent English-Chinese content, unless the project explicitly
  specifies the opposite language order.

Read [edition modes](references/edition-modes.md) for the selected mode. Do not
introduce bilingual duplication into a monolingual edition, or simplify a
bilingual edition into a translation summary.

## Establish the book contract

Before conversion or layout work, read the repository instructions and create
or update the project's book contract. It identifies the content authority,
edition, language order, source and output locations, template, fonts, build
command, source map, terminology, and known anomalies. Read
[project contracts](references/project-contract.md) for the required decisions.

The declared source is authoritative. Keep it immutable unless the project
explicitly permits source corrections; record approved errata and source-export
defects separately instead of silently repairing or inventing content.

## Produce semantic Typst

1. Inventory chapters, hierarchy, links, figures, tables, code, notes,
   footnotes, citations, and assets before conversion.
2. Convert semantic elements, not Markdown punctuation or rendered page shapes.
   Preserve reading order, numbering, visible links, code, formulas, figures,
   tables, and citations.
3. Keep repeated layout decisions in `template.typ` and named semantic macros.
   Keep chapter files focused on content; do not use page-specific spacing or
   manual breaks to hide ordinary flow problems.
4. Keep a source map between every content input and generated Typst output.
   When source files change, regenerate instead of hand-editing derived text.
5. Preserve supplied assets with stable paths and original bytes where fidelity
   matters. Do not replace a missing source visual with an invented one.

For bilingual work, pair each complete semantic element with its translation:
headings, prose, lists, captions, notes, footnotes, and table cells. Keep code,
commands, formulas, identifiers, URLs, and other invariant material single-copy
unless the book contract defines a different policy.

## Build and verify

Use the project's explicit Typst version, root, font path, and reproducible
build command. A successful compile is necessary but not sufficient. Read
[verification](references/verification.md) before handoff.

Verify content coverage, hierarchy and numbering, links and cross-references,
assets, fonts, code integrity, table and figure geometry, PDF existence and
page count. Rasterize and inspect representative chapter openers, dense text,
code, tables, footnotes, and image-heavy pages.

## Project overlays

When a project-specific Typst skill exists, treat it as an overlay on this
production core. The overlay owns project paths, content authority, terminology,
fonts, page geometry, macro names, approved visual decisions, and known source
anomalies. Its explicit rules override this skill where they differ.

Promote a lesson from a project overlay into this core only when it is
reproducible and useful across multiple books. Keep one-book taste and
exceptions in that book's decision log.
