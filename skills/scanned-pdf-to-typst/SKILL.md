---
name: scanned-pdf-to-typst
description: Converts scanned or hybrid PDF books into source-traceable, proofread Typst editions while preserving visual assets and producing reproducible PDFs. Use when a user asks to OCR or extract a scan, turn a legacy, image-only, or hybrid PDF into Markdown or Typst, recover figures or tables, proofread OCR, or make a faithful high-quality Typst book.
---

# Scanned PDF to Typst

made by quboliu

Treat the rendered page as visual evidence and OCR as an editable hypothesis. Preserve the original PDF unchanged, preserve page identity throughout, and never let a convenient text export silently override what the page shows.

## Quick start

1. Create an immutable source copy, checksum it, and inventory pages, text layers, fonts, bookmarks, and embedded images.
2. Classify the PDF as native, image-only, or hybrid. Rasterize representative pages before choosing an OCR/layout engine.
3. Produce a page-anchored Markdown or plain-text baseline plus a figure/asset manifest.
4. Review every source page against a rasterized rendering. Record one final page-status record per source page and separate correction records.
5. Apply only page-scoped, evidence-backed corrections to a clean baseline; regenerate the candidate instead of chaining edits.
6. Convert the verified semantic source to Typst, preserve source-page anchors and asset mappings, then compile and visually inspect the resulting book.
7. Write a release/build record before handoff and validate the actual PDF against it. Prefer the reusable `scripts/validate_pdf_release.py`; it tries PyMuPDF first, then another Python PDF parser, and reports a clearly labelled fallback or failure when neither is installed.

## Non-negotiable rules

- Keep source, raw extraction, correction ledger, final candidate, and release artifact as distinct files.
- Use the page rendering, not an extracted image object, as truth for figures with overlays or multiple layers.
- Do not use global replacements for ambiguous OCR glyphs, punctuation, code, units, or formulae.
- Do not describe a chart or table as structured data unless its cells or data were actually verified; a faithful figure is preferable to invented structure.
- A page is not reviewed merely because its OCR is short. Distinguish intentional blank, title, illustration, and extraction failure.
- Keep original-page anchors even after Typst pagination changes; physical output page numbers are not durable anchors.
- Require an independent release audit for coverage, correction scope, assets, compilation, and representative rendered pages.
- Treat the PDF hash and page count as release evidence, not as values copied from a build log. The final audit must recompute both from the delivered PDF and compare them with the release/build record.
- Keep a traceable visual-sample manifest: every reported sample filename, output page, and semantic page class must be present in the manifest and resolve to a file. Include at least one code or technical-dense sample, and distinguish searchable OCR prose/inline technical tokens from a genuine semantic Typst `raw` code block; `raw` typesetting alone does not establish executable code.
- When the source has no fenced code, mark code candidates using multiple weak signals (indentation, short/symbol-dense lines, common code tokens, and consecutive-line structure). Confirm candidates against the rendered page or an audit record before emitting `raw`; leave unconfirmed candidates as ordinary text and record that limitation. A readable `raw` block still does not make OCR content executable.
- Source PDF pages and Typst output pages are different coordinate systems after reflow. Use source-page anchors and `source-map` landmarks for traceability; never promise that a source page number equals a PDF output page number.

## Engine-selection protocol

Benchmark available OCR/layout options on 12 to 20 representative pages: ordinary prose, small type, columns, title pages, tables, diagrams, code, low-contrast pages, and near-blanks. Compare character fidelity, reading order, table/figure handling, language support, runtime, cost, privacy, and license terms. Record tool versions and parameters. A hybrid PDF may already have the best useful text layer; use a second engine only where it demonstrably improves the evidence.

## Reference routing

- Read [references/workflow.md](references/workflow.md) before extraction and proofread planning.
- Read [references/pitfalls.md](references/pitfalls.md) before applying corrections or extracting page assets.
- Read [references/typst-production.md](references/typst-production.md) when generating, building, and releasing Typst.
- Use scripts/validate_page_audit.py to validate the one-row-per-source-page final audit ledger.
- Read [references/release-validation.md](references/release-validation.md) when preparing the build record, visual-sample manifest, or final PDF audit. Run `scripts/validate_pdf_release.py` against the delivered PDF.

## Definition of done

The work is complete only when all intended source pages have an accounted-for status, every final text change has evidence and scope, visual assets resolve, Typst builds reproducibly with known fonts, a release/build record matches the delivered PDF's recomputed hash and page count, and mechanical plus visual release checks pass. Keep the manifests and commands needed to reproduce the edition.
