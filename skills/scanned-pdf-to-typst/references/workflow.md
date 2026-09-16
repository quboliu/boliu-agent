# End-to-end workflow

This is a preservation-and-publication workflow. It intentionally separates source recovery, textual correction, semantic conversion, and page design so that a mistake in one stage cannot silently rewrite evidence from another.

## 0. Make the source immutable

Create a project tree before processing:

~~~text
project/
  source/
    original.pdf
    source-manifest.json
  extract/
    raw.md
    raw.txt
    pages.json
    assets/
  review/
    page-status.jsonl
    corrections.jsonl
    source-crops/
  publish/
    content.md
    typst/
    build/
    dist/
~~~

Record the original path, SHA-256, file size, PDF page count, bookmark count, extraction command, and tool versions in source-manifest.json. Do not overwrite original.pdf or modify its metadata.

Useful discovery commands include:

~~~bash
pdfinfo "source/original.pdf"
pdffonts "source/original.pdf"
pdftotext -layout "source/original.pdf" "extract/raw.txt"
pdfimages -list "source/original.pdf"
pdftoppm -r 300 -png "source/original.pdf" "review/page"
~~~

The goal is not to commit to these utilities. It is to collect enough evidence to classify the file and decide whether the existing text layer is usable.

## 1. Classify before OCR

Classify each document, and occasionally individual page ranges, as:

| Class | Reliable starting material | Main risk |
| --- | --- | --- |
| Native PDF | embedded text, vector figures | reading order and semantic recovery |
| Image-only scan | rasterized page image | OCR errors and layout reconstruction |
| Hybrid scan | image plus OCR text layer | text layer looks searchable but disagrees with page |

For a hybrid PDF, extract the embedded text as a baseline and compare it to rendered samples. It can be better than a fresh OCR pass because it may contain publisher-specific language training, but it remains untrusted until visually sampled.

## 2. Select an OCR and layout path with a small benchmark

Choose 12 to 20 pages that expose the whole book: front matter, body prose, dense/small text, a table, a diagram, a code listing, a low-contrast page, a title page, and a near-blank page. Run each candidate path with saved settings.

Score the results separately:

- character fidelity for the actual language and historical typography;
- reading order and paragraph boundaries;
- treatment of code, formulae, punctuation, numerals, and units;
- table and caption association;
- detection of image-only/title/blank pages;
- cost, throughput, privacy/residency, licensing, and reproducibility.

Do not pick a provider from a generic leaderboard. The best option is the one that wins on this book's representative pages and constraints. Record the scorecard and leave the original text layer available as a comparison baseline.

## 3. Build a page-anchored baseline

The baseline must retain a stable source-page marker before every page, for example:

~~~text
<!-- source-page: 106 -->

... extracted content for source page 106 ...
~~~

Store a page manifest with source-page number, extracted character count, text-layer/OCR origin, image references, and an initial classification. Preserve exact code and URL fragments as raw material rather than normalizing them during extraction.

For figures, make two inventories:

1. raw embedded objects, useful for reuse where they reproduce the rendering; and
2. rendered-page crops or full page images, which are the truth where PDFs use masks, overlays, tiled images, or vector labels.

Generate page composites from the rendered PDF when a figure consists of multiple extracted objects. A single item from pdfimages is not proof that it is a complete figure.

## 4. Make the review ledger first-class data

Keep two separate ledgers:

- page-status.jsonl has exactly one final status per source page;
- corrections.jsonl has one entry per proposed or accepted text correction.

The final status record should be compact and machine-checkable:

~~~json
{"page":106,"status":"corrected","reviewer":"reviewer-id","evidence":"review/source-crops/p0106.png","correction_ids":["c014"]}
~~~

Valid statuses are project-defined, but make intentional blank, title/supplemented, illustration-only, no-change, corrected, and unresolved distinguishable. A page with a short text extraction must still have a deliberate status.

Every correction should include:

~~~json
{"id":"c014","page":106,"before":"unique surrounding text","after":"verified replacement","evidence":"source crop or page reference","reason":"visual confirmation","status":"accepted"}
~~~

Use sufficient surrounding text to make the match unique on that page. If the observation has no confidently supported replacement, mark it unresolved rather than guessing.

Validate the final page-status ledger:

~~~bash
python3 scripts/validate_page_audit.py \
  --records review/page-status.jsonl \
  --page-count 433
~~~

The script checks coverage and duplicates. It intentionally does not decide whether a correction is semantically true; that remains a visual/evidence review task.

## 5. Apply corrections safely

Start every candidate from the immutable raw baseline. Apply accepted correction records in source-page order and only when both the page marker and unique context match. Save a merge manifest with:

- raw baseline checksum;
- candidate checksum;
- correction ids applied;
- source pages changed;
- skipped/conflicted records and their reasons.

After regeneration, diff raw and candidate. Every changed page must appear in the merge manifest, and every accepted correction must be either applied once or explicitly closed as no-op/superseded. Never patch a candidate repeatedly without being able to reconstruct it from raw.md plus the ledger.

## 6. Decide how to represent tables, charts, and figures

Use a structured Typst table only when the visual source establishes its rows, columns, cell content, and reading order. Preserve a table as an image/figure when OCR is ambiguous, cells span irregularly, or typography carries important meaning.

For charts:

- preserve the rendered figure as the canonical visual;
- transcribe data only when labels, scales, and values can be verified;
- keep captions, original-page anchors, and an asset mapping;
- label any reconstruction as editorial rather than presenting it as source-exact.

Do not redraw a diagram merely because its source format is inconvenient. Redrawing requires a separately reviewed design/artifact and should be a deliberate editorial decision.

## 7. Normalize into semantic source before Typst

The reviewed Markdown is a content layer, not a layout simulation. Map headings, paragraphs, lists, quotes, code, figures, captions, tables, links, notes, and page breaks into explicit semantic constructs. Preserve:

- original-page anchors;
- code whitespace and punctuation;
- literal URLs and identifiers;
- asset IDs and caption text;
- a source-map record connecting each semantic block to the source page.

Do not use broad regular-expression replacements across mixed prose and code. Parse blocks first, protect raw/code content, then transform inline prose.

When OCR has no fenced code, run a candidate pass before conversion. Combine
weak signals—indentation, short lines with high symbol density, common code
tokens such as `func`, `return`, braces or SQL verbs, and consecutive-line
structure—rather than promoting a line from one signal alone. Confirm each
candidate against the rendered source page or an audit record before emitting
a Typst `raw`/code block. Unconfirmed candidates stay ordinary searchable
text and the release limitation is recorded. A confirmed `raw` block preserves
layout and tokens; it does not certify that OCR substitutions produce
executable code.

A compact JSONL candidate ledger is sufficient:

```json
{"id":"code-candidate-109-01","page":109,"line_span":"42-58","signals":["short-symbol-dense","func-token","consecutive-lines"],"evidence":"review/source-crops/p0109.png","decision":"confirmed","typst_form":"raw","executable":"not-asserted"}
```

## 8. Build Typst as a derived publishing artifact

Keep the Typst template, generated content, assets, font files/licenses, converter, build command, source map, and release files in a stable tree. Put visual decisions in a template rather than repeating styles through content files.

Read [typst-production.md](typst-production.md) for the project layout, semantic mapping, compilation, and layout checks.

## 9. Release through independent gates

Mechanical checks:

- source page count equals final audit ledger coverage;
- source-page anchors survive into reviewed content;
- candidate diffs match the correction/merge manifests;
- every referenced asset resolves and has a documented source;
- Typst compiles with pinned/recorded version and known fonts;
- no placeholders, stale paths, or unresolved review statuses remain.

Visual checks:

- inspect title/front matter, ordinary text, dense text/code, table/note, image-heavy, chapter opening, and chapter ending pages;
- use a contact sheet for a long book to reveal repeating failures;
- inspect at reading size for clipping, CJK font fallback, punctuation breaks, widows/orphans, overflow, caption separation, and figure scaling;
- compare semantic landmarks after re-pagination, not merely output page numbers.

An independent reviewer should verify the manifests and rendered output without authoring new corrections in the same pass.

## 10. Validate the PDF release record

Before handoff, create a machine-readable build/release record containing the
Typst version, exact command, timestamp policy/value, generated PDF SHA-256,
and page count. Recompute the final PDF hash and page count from the delivered
file and compare them with the record. Prefer the Python-based
`scripts/validate_pdf_release.py`; it uses PyMuPDF when available and reports
its parser fallback explicitly when it is not.

Keep a visual-sample manifest that maps each raster filename to the physical
Typst page and a semantic class. The report must repeat the same mapping, and
the manifest must include a code or technical-dense sample. Do not label
searchable OCR prose containing code-like tokens as a semantic executable
Typst code block.

## 11. Deliver a preservation package

Deliver or retain:

- the original PDF and immutable source manifest;
- raw extraction and all page/asset manifests;
- final reviewed content plus page-status and correction ledgers;
- merge/promotion report with checksums;
- Typst source, build command, version/font information, and final PDF;
- release audit report, including known limitations.

State the difference between visually verified transcription and fully structured extraction. A figure whose inner text remains only in the raster is still preserved, but it is not a machine-readable chart dataset.
