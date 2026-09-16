# Release quality gates

Run these gates in order. A release is not ready if a gate fails or if a visual exception is not recorded.

## Mechanical gates

- Source inventory is complete: all intended chapters are mapped to generated files in the documented order.
- Every local image reference resolves; no generated file contains a stale source path, TODO, or placeholder.
- Typst compiles with the documented font path and no missing-font/file warnings.
- The PDF exists, is non-empty, has a plausible page count, and contains searchable text for normal prose.
- Headings and figures have the expected structural counts; level-one/section headings are queryable, their automatic numbers are consistent, and the table of contents is present and links to headings.
- Code fences are balanced and language labels are retained.
- Asset dimensions are recorded or checked so low-resolution images are not silently enlarged beyond an acceptable threshold.
- The source-anomaly ledger exists for every accepted extraction exception; no unexplained source loss, guessed footnote placement, or invented cross-reference is hidden in generated files.
- Search generated Typst and extracted PDF text for leaked converter/template commands (for example raw `v(...)`, `line(...)`, or implementation labels) and for stale source paths, TODOs, and placeholder text.

## Visual gates

Render at least:

- the cover/title and contents pages;
- one ordinary text-heavy page;
- one page with a long SQL/code block;
- one table or note-heavy page;
- one image-heavy page;
- a chapter opening and a chapter ending.

Rasterize samples at 144 or 288 PPI. Inspect for clipped glyphs, fallback Chinese fonts, bad punctuation line breaks, widows/orphans, headings stranded at page bottoms, captions separated from figures, table overflow, code wrapping, inconsistent vertical rhythm, and weak contrast. On ordinary pages verify that the left running head names the current chapter (not only the book), the folio appears once, and chapter openers use their special header/footer treatment. Check at least one tall and one wide figure so adaptive sizing does not leave excessive whitespace or cause enlargement. Use a contact sheet when the book is long so repeated defects become visible.

When a template or conversion rule changes, keep a before/after raster sample of the affected page classes (cover/contents, chapter opener, text, code, table/note, image, chapter end). Compare semantic landmarks (the same chapter, heading, code block, or figure), not only old physical page numbers, because rhythm changes repaginate the book. Record the before/after page count. A page-count change is not itself a failure, but unexplained drift or a newly introduced visual exception must be recorded in the decision log before handoff.

## Reproducibility gates

- Build command is documented and runs from a clean checkout.
- Typst version and font files are identified; font licences are present.
- Source-to-output mapping and asset manifest are committed.
- Generated output is reproducible enough that a rebuild does not introduce unexplained layout drift. If a change is intentional, record why and which pages were reviewed.
