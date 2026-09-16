# Terra iteration audit

## Result

**Pass, with one script hardening applied.** The release-validation additions
are generic and preserve the distinction between source-page traceability and
reflowed output-page numbering.

## Checks run

- `quick_validate.py` passed when run with PyYAML supplied by an isolated uv
  environment; the host default Python lacks that optional validator
  dependency.
- `validate_pdf_release.py` validated the real Typst PDF using an isolated
  release record and visual manifest derived from its public QA facts. It
  exited 0 and explicitly reported the object-tree fallback because no Python
  PDF parser was installed in that interpreter.
- A deliberately wrong SHA-256 exited 1 and reported the mismatch.
- A missing release record now exits 1 with structured JSON rather than a
  traceback. This was corrected in the validator during this audit.

## Scope review

The skill requires a Python-parser-first path, clearly labels the byte-marker
fallback, requires hash/page-count comparison, ties visual samples to a
manifest/report, calls for a technical-dense/code sample, and distinguishes
searchable OCR tokens from Typst raw code. It does not prescribe a page size,
font family, output page count, colour theme, or asset count.

`SKILL.md` remains the required uppercase entrypoint; all added supporting
resource and script names are lowercase.

## Unfenced OCR code follow-up audit

**Pass, with two small consistency hardenings applied.** The skill now treats
unfenced OCR code as a multi-signal candidate, requires rendered-page or audit
evidence before Typst `raw`, retains unconfirmed candidates as ordinary text,
and says explicitly that readable `raw` is not evidence of executable code.
This is routed through the entrypoint, workflow, Typst production, pitfalls,
and release-validation references without imposing any book-specific page,
font, asset, or output-count rule.

The entrypoint wording was corrected to avoid calling a Typst `raw` block
“executable.” The PDF-release validator now requires every code-class visual
sample to declare `code_treatment` as `confirmed-raw` or
`retained-ordinary-text`, and compares that field between manifest and report.
`quick_validate.py` and Python compilation passed. A fixture based on the
real Typst output passed validation; omitting `code_treatment` failed with the
expected diagnostic. Its PDF parser fallback was explicitly reported as
byte-marker evidence rather than text extraction.
