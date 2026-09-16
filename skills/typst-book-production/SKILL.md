---
name: typst-book-production
description: Produce and maintain publication-quality Typst books in Chinese, English, or adjacent Chinese-English bilingual editions. Use when converting or maintaining a book, long-form manuscript, or paginated source as a reproducible Typst PDF.
---

# Typst Book Production

made by quboliu

Produce a faithful, maintainable, and reproducible Typst book. This is a
general production core: each book supplies its own source authority, language
policy, typography, semantic macros, terminology, and exceptions.

## Use the 伯流出版社 design system

Every book begins from the shared publication profile in
[伯流出版社 design system](references/publisher-design-system.md). Its B5 grid,
type scale, vertical rhythm, figure, table, code, running-furniture, and cover
rules are calibrated from the finished DDIA edition. This is how independently
produced books retain one recognisable publisher character.

Treat the profile as a measurable default, not a collection of decorative
suggestions. Put its tokens in the book's `template.typ`; do not replace them
with chapter-local spacing. A departure is allowed only for a real content,
language, binding, accessibility, or print constraint, and must be recorded in
the book contract with the replacement value and a visual comparison.

The first two pages are mandatory cover matter:

1. **Source cover (page 1).** When a published or open-source book already has
   an original cover, use that exact cover from the best available high-
   resolution, reproduction-permitted source; retain its proportions and record
   source, checksum, licence or permission, and any crop. Do not redraw,
   stylise, upscale, or substitute it. When no original cover exists, make the
   neutral fallback cover defined by the design system: title, original author,
   original-source/version statement, and no invented artwork.
2. **伯流出版社 cover (page 2).** Always follow with the publisher's distinct
   edition cover. It must visibly carry `伯流出版社`, identify the edition without
   impersonating the source edition, and use a contextually relevant, lawful
   line-drawing portrait of a well-known historical figure or a line-drawing of
   a notable scene in which that figure participated. Record the image source,
   rights, subject, and relevance. Do not use a living person's likeness,
   invented historical portrait, or a generic decorative image.

If a reproduction-permitted high-resolution original cover or the required
rights/provenance cannot be established, stop before distribution and ask for a
source or permission; a low-resolution web preview is not an acceptable stand-in.

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
command, source map, terminology, known anomalies, publisher-profile version,
and both cover records. Read
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
