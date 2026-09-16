# Typst production guide

The reviewed text is the content authority. Typst is a generated, reviewable publishing layer that must remain reproducible from it.

## Suggested layout

~~~text
publish/
  content/
    book.md
    source-map.json
  typst/
    book.typ
    template.typ
    chapters/
    assets/
    fonts/
    scripts/
  build/
  dist/
~~~

Keep derived content clearly labeled. Keep assets under stable relative paths and record their original PDF page, crop coordinates if applicable, checksum, and caption/source relationship.

## Semantic conversion

Convert source constructs deliberately:

| Reviewed source | Typst form | Check |
| --- | --- | --- |
| chapter/section | semantic heading/component | outline and hierarchy remain queryable |
| paragraph | normal prose | Typst markup is escaped only in prose |
| fenced or evidence-confirmed code candidate | labelled block raw | characters and whitespace unchanged; never infer executability from OCR |
| unconfirmed code candidate | ordinary prose + limitation ledger | searchable text is not a semantic code block |
| figure plus caption | figure with stable asset path | aspect ratio and caption stay together |
| verified grid table | table component | cells and reading order match source |
| uncertain visual table/chart | figure/crop | no invented structured data |
| source-page marker | comment/label/source map | traceable after pagination changes |

Parse blocks before inline content. In particular, protect fenced code, URLs, and image paths before escaping Typst-sensitive prose characters. For unfenced OCR, use multiple weak candidate signals (indentation, short/symbol-dense lines, common code tokens, consecutive-line structure), then require visual/audit confirmation before `raw`. Keep source anomalies and candidate decisions in a ledger instead of burying guesses in the converter. `raw` is a typesetting choice, not an assertion that OCR code is executable.

## Template policy

Put global visual decisions in template.typ:

- page size, margins, grid, page styles, running heads, and folios;
- CJK body/display/code font families and fallbacks;
- type scale, paragraph rhythm, heading rules, lists, quotes, notes, and links;
- figure sizing, captions, tables, and code blocks;
- colour tokens and accessibility/contrast choices.

Content chapters should contain headings and named semantic components, not repeated style constants. Use figure containers so captions do not become detached. Treat wide/tall figures and wide tables as explicit layout cases rather than shrinking everything until it fits.

For Chinese books, verify actual CJK glyph coverage in the compiled PDF. A nominally successful build with a fallback font is a failed production gate.

## Reproducible build

Document one command that can run from a clean checkout. Record:

- Typst version;
- explicit project root;
- explicit font path and font licenses;
- source-to-output converter version/commit;
- asset manifest;
- reproducibility timestamp policy, if the installed Typst version supports it.

Write these values to a machine-readable release/build record alongside the
PDF. At minimum it must contain the generated PDF SHA-256, page count, Typst
version, exact build command, and creation-timestamp policy/value. Recompute
the hash and page count from the delivered PDF during final QA; do not merely
trust values emitted by the build process.

An example shape is:

~~~bash
typst compile --root "publish/typst" --font-path "publish/typst/fonts" \
  "publish/typst/book.typ" "publish/dist/book.pdf"
~~~

Pin or record any packages and avoid hidden system-font dependencies. Compile a tiny probe when a Typst behavior is uncertain rather than guessing in a large book.

Do not make `pdfinfo` a release dependency. Run
`scripts/validate_pdf_release.py` with the release record and visual manifest.
It tries PyMuPDF first for page count and text extraction, then `pypdf` or
`PyPDF2`, and finally reports an explicit Python byte-level fallback (or a
clear failure). A fallback may establish a page-tree count and basic text
markers, but it must not be described as full text extraction.

## Mechanical release checks

- chapter/source-map coverage and source-page anchors are complete;
- no unresolved image path, placeholder, stale path, or TODO remains;
- headings, figures, captions, links, code blocks, and tables have expected counts;
- code fence balance and raw text integrity are checked;
- final PDF exists, is nonempty, and has plausible page count;
- final PDF hash and page count are recomputed and match the release/build record;
- compilation has no missing font/file warnings;
- generated content has not been hand-edited outside the documented converter flow.

## Visual release checks

Rasterize and inspect at least:

1. cover/title and contents;
2. chapter opening;
3. ordinary body prose;
4. dense text and code, including a confirmed candidate block and one unfenced OCR code case when present;
5. table/note-heavy content;
6. image-heavy content;
7. a tall figure, a wide figure, and a chapter ending.

Use a contact sheet for a long book. Check CJK font rendering, punctuation line breaks, heading placement, widow/orphan behavior, code wrapping, overflow, image scale, captions, table legibility, page furniture, and contrast. Store a visual-sample manifest with each filename, physical output page, and semantic class (for example `cover`, `contents`, `body-text`, `technical-dense-code`, `figure`, `chapter-ending`). The visual report must repeat the same records exactly. Include a technical-dense or code sample, and explicitly identify whether it is a confirmed semantic `raw` block or an unfenced OCR candidate retained as ordinary text; searchable OCR text containing code-like tokens is not equivalent to a semantic Typst code block (`raw` with preserved whitespace/language). When layout changes, compare the same semantic landmark rather than the old output page number. Source PDF page numbers remain traceable only through source-page anchors and the source map.

## Release statement

State the edition's guarantees and limitations. For example: all source pages are represented and page-anchored; OCR text was visually reviewed under the stated protocol; visual figures are preserved from rendered source pages; chart internals were not asserted to be structured data unless separately verified.
