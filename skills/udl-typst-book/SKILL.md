---
name: udl-typst-book
description: Create and maintain the publication-quality Typst/PDF edition of Understanding Deep Learning, including equation tags, paragraph-attached margin notes, figures, tables, links, and future bilingual layout.
---

# UDL Typst book

made by quboliu

Use this skill when converting, rebuilding, reviewing, or visually refining the UDL v5.0.3 book in `/home/xuntingmu/workspace/mindstore/books/udl`.

## Authority and invariants

- Treat the supplied v5.0.3 PDF, equation source, official figure PDFs, BibTeX, and extracted Markdown as content authorities. Record deliberate layout adaptations in the project decision log.
- `markdown/..._official-eq.md` is the editable semantic source. `typst/chapters/*.typ` and `typst/images/` are generated artifacts; change the converter or template and regenerate them together.
- Preserve every paragraph, equation, figure, table, problem, note, footnote, internal target, and external URL. A successful Typst compile does not prove content preservation.
- Keep a single reusable template. Do not introduce page-specific spacing or manual nudges to repair one rendered page.

## Layout contract

- Body text uses a stable reading column with deliberate heading hierarchy, paragraph rhythm, figure/caption grouping, table geometry, running furniture, and folios.
- Display equations occupy the full reading-column width. The equation body is optically centered on the page; its number is independently aligned to the reading-column right edge. Never implement numbering with an inline `#h(2em)` spacer.
- A source margin note belongs to the paragraph beside which it appears. Move it to that paragraph's end and render it in parentheses, for example `(Notebook 2.1: Supervised learning)`. Keep its original clickable URL or page target. Never collect these notes at the end of a chapter.
- Marker/PDF reading order can split a note across adjacent paragraphs or duplicate its title. Collapse the fragments into one note, remove them from the prose position, and attach the complete note to the owning paragraph. If the source PDF contains a note missing from Markdown, add it through a reviewed manifest and audit it against the PDF.
- Prefer supplied official vector figures. Preserve raster assets only when no reliable official vector match exists; inspect dimensions and native appearance before accepting a low-resolution asset.
- Keep code, figures, captions, tables, and equations as semantic reading objects. Do not flatten them into screenshots or silently rewrite their content.

## Workflow

1. Inventory the source, chapter order, links, equation tags, figure assets, and original-PDF margin-note manifest before changing layout.
2. Update the shared converter/template and write a small Typst probe for uncertain syntax before rebuilding the entire book.
3. Regenerate all derived Typst files, compile the PDF, and treat missing files, font fallback, malformed links, duplicate labels, and overflow warnings as failures.
4. Run the mechanical checks in [quality-gates.md](references/quality-gates.md), including equation-number alignment, paragraph-note coverage, target preservation, figure availability, and PDF geometry.
5. Render representative original/current pages at high resolution. Always inspect an equation-heavy page, a page with a paragraph-attached note, a dense text page, a figure-heavy page, and a table/code page.
6. Record accepted tradeoffs and known source-extraction anomalies in [layout-decisions.md](references/layout-decisions.md); do not hide omissions behind a clean compile.

## Bilingual edition

The bilingual development project lives in `/home/xuntingmu/workspace/mindstore/books/udl/dual`. It reuses the English edition's assets and A4 geometry while following the DDIA dual-language workflow:

- put English first and Chinese immediately after it in one semantic unit;
- split only at complete paragraphs, lists, equations, figures, tables, notes, or other complete blocks;
- use one shared bilingual heading, figure caption, table caption, equation, or footnote object so the two languages do not create duplicate structural entries;
- keep every original URL and internal target in both language labels when both labels are visible;
- keep a paragraph-attached side note at the end of its owning bilingual unit, in parentheses, never in a chapter-end note section;
- retain the UDL equation component: formula body independently centered and equation tag independently right aligned;
- record UDL-specific geometry and translation decisions in `dual/references/` instead of silently copying DDIA's B5 settings;
- compile `dual/main.typ` and `dual/layout-probe.typ` through `dual/tools/build_dual.py` before expanding a chapter.

The first chapter sample is a layout baseline, not a claim that the chapter translation is complete. The full edition must reconcile every English semantic block with a reviewed Chinese counterpart before it is treated as deliverable.

Read the supporting references only when needed:

- [layout-decisions.md](references/layout-decisions.md) for the current UDL geometry and accepted adaptations.
- [quality-gates.md](references/quality-gates.md) for release checks and visual sampling.
- [side-notes.md](references/side-notes.md) for the source-order problem and the paragraph-attached note algorithm.
