---
name: ddia-v2-dual-typst
description: Maintain the DDIA V2 English-Chinese dual-language Typst book, including semantic translation units, book-quality pagination, tables, notes, footnotes, figures, and PDF verification.
---

# DDIA V2 dual-language Typst

made by quboliu

Use this skill for every translation, layout, sample, or PDF-export task in the
`DDIA-V2-Typest-dual` project. Treat this file and
`references/layout-decisions.md` as the project-specific source of truth. For
translation work, read `references/terminology.md` before editing any chapter;
it is the shared terminology baseline for all agents. The general Typst skill
may supply implementation knowledge, but it must not override the decisions
recorded here.

`typst-book-production` is this project's general production core. Use its
source-locking, semantic-conversion, reproducible-build, and four-layer QA
methods where they do not conflict with this file. This skill remains the DDIA
overlay: its explicit paths, English-Chinese order, terminology, B5 geometry,
font pairing, macro names, and documented source anomalies override the core.

## Scope and invariants

- Work in `DDIA-V2-Typest-dual/`; leave the original `DDIA-V2-Typest/` tree
  unchanged unless the user explicitly asks otherwise.
- Preserve the source's structure, numbering, links, code, figures, and table
  geometry. A bilingual change should add translation, not redesign the book.
- Keep the source text and the translation in the same semantic order. Do not
  silently omit, summarize, or reorder content.

## Translation units

- Put English first and Chinese immediately after it.
- Aim for roughly 600–900 English words (about 800 words) per bilingual unit,
  but split only at complete natural paragraphs or complete semantic blocks.
  Never cut a paragraph, list, note, example, or argument in half merely to
  hit a word count.
- Use the existing `dual[english][chinese]` macro for ordinary prose. If a
  source block is structurally special, preserve its source element and add a
  matching Chinese element rather than flattening it into prose.

## Typography and spacing

- Body English uses `Libertinus Serif`; Chinese uses the local `Noto Serif SC`
  font. Body Chinese is ordinary body text: 10pt, the same leading,
  paragraph spacing, justification, and visual weight as English.
- Do not add blue backgrounds, colored panels, badges, or other visual effects
  to translations. English and Chinese already provide sufficient distinction.
- Keep the existing B5 page geometry and restrained book palette. Adjust
  spacing globally in `template.typ` instead of adding page-specific nudges.

## Headings and titles

- English and Chinese headings share one semantic heading element. English is
  on the first line and Chinese is on the next line; never append the Chinese
  title to the English line.
- Use `dual-heading(level, en, zh)` and `dual-title(en, zh)` so the heading
  remains queryable, numbered consistently, and styled as a normal book
  heading.
- A translated heading is still a normal heading: retain a visible, balanced
  gap before the heading and between the Chinese heading line and the following
  body. Keep headings with the content that follows; do not leave an orphaned
  heading at a page bottom.
- Do not solve ordinary pagination with manual `pagebreak()` calls in samples.
- Ordinary numbered pages use a restrained running head with an explicit short
  English chapter identifier/title at upper left, the page number at upper
  right, and a fine gray rule below. Do not reuse the full bilingual level-1
  heading as a running title. Chapter openers omit the running head and keep a
  centered footer page number; the cover and automatic blank verso pages show
  neither. Contents pages use `CONTENTS` at upper left and the page number at
  upper right.

## Notes, footnotes, figures, and tables

- A source Note has one shared Note container. Put English first, then Chinese
  inside that same Note; do not create a second translated Note.
- A source footnote has one shared footnote entry. English uses
  `footnote-size` (currently 8pt). Chinese uses the separate
  `footnote-zh-size` (currently 7pt) as an optical compensation: Noto Serif
  SC's CJK glyphs occupy more of the em square than Libertinus Serif's Latin
  glyphs at small sizes. This is intended to make the two lines look equally
  large, not to claim that their nominal point sizes are identical.
- This optical reduction is a narrow rule for Chinese text inside these
  bilingual footnotes with this specific font pairing. Do not apply it to body
  prose, headings, titles, Notes, tables, figure captions, or any other
  Chinese text. If the font pairing, point size, or output medium changes,
  re-check visually before reusing the 7pt value.
- Keep each figure's image and caption together. Bilingual captions use one
  caption, with English first and Chinese on the next line. Do not make figure
  placement sticky with the next heading if that would create a mostly blank
  page.
- Tables must preserve the English table's columns, widths, line lengths,
  stroke styles, insets, and row structure exactly. A complex table may have a
  separate Chinese copy; that is preferred to forcing both languages into one
  cramped grid. Only the cell text should differ.
- Keep a table caption with its table. Use the project's `booktable` and
  `table-caption` helpers rather than hand-built one-off geometry.

## Verification workflow

1. Treat `DDIA-V2/**/*.md` as the independent content authority when it is
   available. Compare it directly with the bilingual Typst; do not validate the
   bilingual source only against the monolingual Typst from which it was copied.
   Preserve visible Markdown links, including each distinct target in glossary
   and index entries, as clickable Typst links. Preserve internal cross-reference
   semantics with stable Typst labels where the target exists.
2. Inspect the nearby source and the current template before editing.
3. For chapter translation, read `references/terminology.md` and record any
   unresolved term choices for the main agent instead of changing the baseline
   independently.
4. Make reusable changes in `template.typ` or a project macro; avoid local
   formatting patches unless the source element truly differs.
5. Compile the sample and the full book with the bundled fonts:
   `typst compile --font-path assets/fonts ...`.
6. Rasterize representative pages at 144 or 288 PPI and visually inspect
   heading-to-body gaps, paragraph flow, footnotes, Notes, tables, captions,
   lists, links, and page bottoms.
7. Use `typst query` for heading structure when changing heading macros, and
   check that sample files contain no accidental manual page breaks.
8. Report the generated PDF path, page count, and any known limitations.

Markdown footnote definitions with no citation marker in visible Markdown body
have no defensible placement in a paginated book. Record them as source-export
anomalies; do not silently attach them to guessed paragraphs or manufacture a
references section. O’Reilly footnote-marker backlinks are web-reader navigation
metadata and need not be reproduced when Typst supplies native footnote
navigation. Conversely, bibliographic, archive, DOI, and content URLs inside an
actually cited footnote are content: preserve every one in both language slots.

When Markdown contains an obvious extraction typo (for example a malformed
opening quotation mark), do not degrade the book merely to reproduce it. Keep
the corrected typography, record the discrepancy as a source erratum, and make
sure the words and link target remain unchanged.

If visible Markdown contains an internal fragment link but the Markdown export
contains no matching target element, preserve the fragment link and record the
missing target as a source-export anomaly. Do not invent the absent sidebar,
figure, or section, and do not attach its label to unrelated content merely to
make a link checker pass.

## Maintenance rule

Every accepted user correction is a durable project decision. Update both the
implementation and `references/layout-decisions.md` in the same change. Record
confirmed rules separately from unresolved questions, and include the sample
version that demonstrated the correction when useful. Before a later sample
or full-book export, reread this skill and the decision log so old layout bugs
are not reintroduced.
