# PDF release validation

Use this reference when a Typst build is ready for release. It defines the
smallest evidence package needed to make the PDF claim reproducible and
auditable.

## Build/release record

Store JSON beside the build artifacts. The required fields are:

```json
{
  "pdf": {"path": "dist/book.pdf", "sha256": "...", "page_count": 123},
  "typst_version": "typst 0.15.1",
  "build_command": "typst compile --root ...",
  "creation_timestamp": {"policy": "SOURCE_DATE_EPOCH", "value": 0}
}
```

The validator recomputes SHA-256 and page count from the actual PDF and fails
on either mismatch. It does not invoke `pdfinfo`: it tries PyMuPDF first,
then `pypdf`/`PyPDF2`, and finally uses a clearly labelled Python PDF
object-tree fallback. The fallback can check `/Count`, `/ToUnicode`, and text
operators, but is not equivalent to page-by-page text extraction. If all
parsers fail and the byte markers are absent, treat the release as blocked.

Run:

```bash
python3 scripts/validate_pdf_release.py \
  --pdf dist/book.pdf \
  --record build/release-record.json \
  --visual-manifest build/visual-samples.json \
  --visual-report build/qa-report.json \
  --report build/pdf-release-validation.json
```

## Visual sample manifest

Use a deterministic list. Every sample needs a path, one-based physical output
page, and semantic class:

```json
{
  "samples": [
    {"filename": "sample-001.png", "output_page": 1, "semantic_class": "cover"},
    {"filename": "sample-042.png", "output_page": 42, "semantic_class": "technical-dense-code", "code_treatment": "confirmed-raw"}
  ]
}
```

The report's `visual_review.samples` list must match this list exactly. Include
cover/title, contents, ordinary body text, a figure/image-heavy page, chapter
opening/ending, and at least one code or technical-dense page. If the source
has code without fences, include one such unfenced OCR case in the visual
sample and label whether it was confirmed into `raw` or deliberately retained
as ordinary text. A page whose PDF text is searchable is not thereby a
semantic code block: report whether code was emitted as Typst `raw` with a
language/whitespace policy or remains OCR inline text, and never claim that
OCR `raw` content is executable.

For a sample whose `semantic_class` contains `code`, set `code_treatment` to
either `confirmed-raw` or `retained-ordinary-text`. The validator checks this
field, and the visual report must repeat it exactly with the manifest.

## Page identity

The source PDF page and output PDF page are separate coordinate systems. A
reflowed Typst document can change output page numbers after any font, figure,
or spacing change. Keep source-page labels in the generated content and use
the source map plus semantic landmarks to connect visual samples to source
evidence; never use equal page numbers as proof of identity.
