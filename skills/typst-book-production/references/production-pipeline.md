# Source reconciliation, reproducibility and real-project checks

This workflow incorporates the source/conversion/audit practices formerly
maintained in chinese-typst-book. Publisher style, two covers, zero body indent,
and duplex geometry remain governed by the current production core.

## Lock inputs

Inventory chapter/navigation order, images, links, notes and source versions.
When a web edition is supplied alongside local files, compare text, structure,
assets and metadata separately. Do not download newer prose as an unrecorded
replacement. Compare image pixels where transport re-encoding explains byte
differences; record both checksums and the selected authority.

Prefer supplied diagrams; do not redraw or generate replacements for convenience.
Record asset dimensions and original bytes, font versions and licences. CJK
body, display and code require verified coverage; record the actual fallback
chain rather than relying on an accidental machine font. A user-required trim
size overrides the B5 default through a documented, reproofed project profile.

## Manifest

Keep `source/source-map.json` under version control. Source paths below are
relative to `source/`; output and asset paths are relative to the project root.
Use recursive coverage for Markdown/HTML corpora; explicitly list navigation or
other excluded source files, with reasons in the project decision log.

```json
{
  "chapters": [
    {"source": "chapters/01.md", "output": "book/chapters/01.typ", "order": 1}
  ],
  "images": [
    {"asset": "assets/figures/diagram.svg", "width": 800, "height": 400}
  ],
  "excluded_sources": ["summary.md"]
}
```

Add hashes, generator version, title, conversion policy and mapping granularity
as needed. An inventory is not proof of semantic completeness: compare headings,
lists, links, code and figures and, for bilingual work, every translated element.
For PDF/EPUB or mixed authority, record the extraction map and use the appropriate
source extensions in the checker; manual content audits remain necessary.

## Deterministic build and regeneration

Pin Typst, converter/package versions, source snapshots and font files. Set a
fixed `SOURCE_DATE_EPOCH` or `--creation-timestamp`, record that value in
`book.toml`, and document a single root-relative build command. Make packages
available reproducibly; avoid unspecified network or system-font dependencies.
Build twice with identical inputs and compare SHA-256; investigate differences
before promising byte reproducibility. Do not replace evidence with the phrase
"reproducible build".

When sources change, rerun the converter, rebuild the entire edition, validate
and inspect affected semantic landmarks. Fix generated content through the
converter or recorded source errata; do not hand-patch derived chapters and lose
the fix on regeneration. Authored Typst remains editable if declared as such.

## Project validation

```sh
python3 /path/to/typst-book-production/scripts/validate_book.py \
  --book-dir /path/to/book-slug-typst-dual \
  --source-dir /path/to/book-slug-typst-dual/source \
  --pdf /path/to/book-slug-typst-dual/output/build/book.pdf \
  --page-size-mm 176 250
```

Requires PyMuPDF for parsed PDF checks. The script checks recursive manifest
coverage, duplicate/order errors, referenced assets and dimensions, generated
placeholders, PDF trim, searchable text, font embedding, and text outside page
bounds. `--require-a4` is retained for explicitly A4 legacy projects. Neither
script proves code equivalence, correctness of all links, annotation evidence,
caption attachment, or complete duplex layout on an arbitrary real book.
Verify those in the release audit; never treat a script PASS as certification.

Scan extracted text for leaked converter commands such as literal `v(...)`,
`line(...)`, stale paths and implementation markers, with human review to avoid
rejecting legitimate code quotations. Check heading/figure counts using native
queries, contents links, footnotes and code text against the source.

## Visual regression and release

Preserve before/after rasters for covers/contents, chapter openers/endings,
dense prose, long code, equations, tables/notes and tall/wide figures. Compare
the same content landmarks, not old page numbers; pagination changes.
Use contact sheets for whole-book patterns and actual-size detail views for
punctuation, glyphs, river spacing, narrow columns and caption attachment.
Record page-count changes and explain intended drift.

Inspect nested paragraph overrides after any spacing change. Contents should
grow rather than be compressed into an arbitrary page count; check hanging
entries, wrapped title leading and guaranteed separation (block gaps may
collapse). Center whole figure wrappers, not only their inner image.
Use tiny probe documents for uncertain syntax and compile after conversion edits.

The release record in `output/audit/` names coverage, unresolved anomalies,
font/input hashes, exact commands, inspected pages, output SHA-256, and print
settings. Freeze accepted editorial notes under `editorial/content-audit/`;
they are maintained inputs, not disposable generated audit output.
