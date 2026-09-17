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

Keep `source-map.json` at each Typst edition root under version control.
`source` paths are relative to the sibling
`<book-slug>-markdown/chapters/`; output and asset paths are relative to the
edition root. All source-language Markdown chapters must be covered. Record
raw-to-Markdown extraction provenance in the book-local skill; the edition map
begins at the normalized Markdown boundary.

```json
{
  "chapters": [
    {"source": "01.md", "output": "book/chapters/01.typ", "order": 1,
     "source_sha256": "<64 lowercase hexadecimal characters from the actual input bytes>"}
  ],
  "images": [
    {"asset": "assets/figures/diagram.svg", "width": 800, "height": 400}
  ],
  "excluded_sources": ["summary.md"],
  "excluded_assets": ["assets/figures/unused-source-variant.svg"]
}
```

Replace the illustrative hash above with the actual SHA-256 of each chapter's
source bytes. Missing, malformed or mismatching source hashes fail validation;
nonconforming manifests must be regenerated from reviewed inputs, not merely
stamped with new hashes while retaining stale output. Record generator version,
title, conversion policy and mapping granularity as needed. Source hashes detect
drift;
they do not prove that Typst/PDF corresponds to the source. Compare headings,
lists, links, code and figures and, for bilingual work, every translated element.
Every file under `assets/figures/` must appear in `images` or in the reviewed
`excluded_assets` list; a short manifest that merely samples existing assets is
not coverage evidence. Prefer removing unused copied figures over excluding
them without a reason.
For PDF, EPUB, or mixed raw authority, record and test the raw-to-Markdown
extraction in the book-local skill; manual content audits remain necessary.

## Deterministic build and regeneration

Pin Typst, converter/package versions, source snapshots and font files. Set a
fixed `SOURCE_DATE_EPOCH` or `--creation-timestamp`, record that value in
`book.toml`, and document a single root-relative build command. Make packages
available reproducibly; avoid unspecified network or system-font dependencies.
Build twice with identical inputs and compare SHA-256; investigate differences
before promising byte reproducibility. Do not replace evidence with the phrase
"reproducible build". Capture raw Typst stderr for each release build in
`output/audit/compile.log`. A release log must be empty; retain nonempty logs as
failure evidence rather than discarding warnings after a PDF is emitted.

When sources change, rerun the converter, rebuild the entire edition, validate
and inspect affected semantic landmarks. Fix generated content through the
converter or recorded source errata; do not hand-patch derived chapters and lose
the fix on regeneration. Authored Typst remains editable if declared as such.

## Project validation

```sh
python3 /path/to/typst-book-production/scripts/validate_book.py \
  --book-dir /path/to/book-slug/book-slug-typst-dual \
  --source-dir /path/to/book-slug/book-slug-markdown/chapters \
  --manifest /path/to/book-slug/book-slug-typst-dual/source-map.json \
  --pdf /path/to/book-slug/book-slug-typst-dual/output/build/book.pdf \
  --compile-log /path/to/book-slug/book-slug-typst-dual/output/audit/compile.log \
  --page-size-mm 176 250
```

Before edition validation, enforce the workspace and edition matrix:

```sh
python3 /path/to/typst-book-production/scripts/validate_workspace.py \
  --workspace-dir /path/to/book-slug \
  --source-language en
```

Requires PyMuPDF for parsed PDF checks. The script checks recursive manifest
file coverage, source hashes, referenced outputs/assets and declared dimensions, generated
placeholders, PDF trim, searchable text, font embedding, and text outside page
bounds. When `--compile-log` is supplied it also rejects a missing or nonempty
raw Typst diagnostics log; release validation requires this option.
`--require-a4` is retained for explicitly A4 legacy projects. Neither
script proves code equivalence, correctness of all links, annotation evidence,
caption attachment, or complete duplex layout on an arbitrary real book.
Verify those in the release audit; never treat a script PASS as certification.

The `chapters` list contains source/output mapping edges, not an absolute
one-file-per-chapter requirement. Repeated sources and outputs are allowed:
one Markdown chapter can generate several Typst files, and several Markdown
inputs can contribute to one output. Hash every input edge; record semantic
fragments and reading order in project metadata. Project-specific checks own
mapping cardinality, duplicate fragments, ordering and semantic coverage. The
generic checker verifies declared files and hashes only. Canonical workspaces
validate the Markdown intermediate with `--source-extensions .md`; raw PDF,
EPUB, HTML, or other extraction coverage belongs to book-local tests because
raw material is not the Typst conversion input.

The generic checker does not classify source-language residue. Literal Obsidian,
HTML or Markdown syntax may be legitimate quoted code. Detect conversion leaks
with source-aware project tests and PDF review, not a global substring ban.

Mark unfinished project work with the reserved marker `BOLIU-UNRESOLVED: reason`
(including in comments); the checker rejects it anywhere in Typst source.
Ordinary `TODO`, `FIXME` and `placeholder` words are not automatic failures:
they may occur legitimately in quoted source code or template documentation.
Review unmarked TODOs manually and migrate actual unfinished tasks to
the reserved marker. The rendered `NOT FOR RELEASE` cover warning remains a
separate PDF failure. Absence of markers does not prove content completeness.

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
