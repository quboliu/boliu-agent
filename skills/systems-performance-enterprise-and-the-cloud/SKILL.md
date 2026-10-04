---
name: systems-performance-enterprise-and-the-cloud
description: "Book-local rules for recovering and publishing Systems Performance: Enterprise and the Cloud, second edition."
---

# Systems Performance: Enterprise and the Cloud
made by quboliu

本 overlay 只记录本书的来源、转换和审校规则；通用目录契约、Typst 出版规范、
B5 版式、双面打印和三版制作矩阵由 `typst-book-production` 负责。

## Authority and provenance

- The canonical book slug is `systems-performance-enterprise-and-the-cloud`; the
  supplied `systems-performance-v2` directory was only a staging name.
- The source language is English. The edition matrix is `-typst-en`,
  `-typst-dual`, and `-typst-zh`.
- `systems-performance-enterprise-and-the-cloud-raw/` contains the three supplied
  immutable source files: one EPUB and two PDFs. The EPUB is the semantic authority;
  the 929-page InDesign PDF is the print-layout and page-location authority; the
  2161-page Calibre PDF is an independent reflow/text cross-check. Their bytes,
  names, hashes, sizes, and metadata are recorded in `raw/readme.md`.
- Raw PDFs and EPUBs match the repository's global ignored-binary policy. They remain
  physically present and are represented by exact SHA-256 records; do not force-add
  them without an explicit repository policy change.
- The EPUB content is UTF-8 XHTML without a reliable charset declaration. Always
  decode bytes as UTF-8 before parsing; parsing raw bytes through an HTML parser can
  turn curly punctuation into `â`-style mojibake.

## Markdown authority

- `systems-performance-enterprise-and-the-cloud-markdown/chapters/` is the only
  normalized text authority. It contains ordered front matter, chapters 1–16,
  appendices A–E, glossary, index, and back matter. Each semantic XHTML spine item
  has one Markdown file; image-only XHTML plates are represented by the figure assets
  they reference, not as duplicate prose chapters.
- `systems-performance-enterprise-and-the-cloud-markdown/images/` contains the
  highest-quality recovered EPUB graphics, plus the source cover. Preserve original
  image bytes and use lowercase collision-safe derived names. The EPUB figure
  filenames (`01fig01`, `pg206-1`, and similar) are retained in a provenance map.
- The `extract_epub.py` converter is deterministic and emits a source manifest. It
  maps XHTML headings, paragraphs, emphasis, inline code, links, lists, tables,
  figures, footnotes, and preformatted examples. It must never alter raw files.
- Paragraphs in `pre` are code, even when they begin with `#`, `$`, or a heading-like
  token. Preserve whitespace and Unicode punctuation exactly. Do not run prose
  escaping over code or URLs.
- Every internal XHTML link is normalized to a stable semantic label based on its
  source file and anchor. Missing targets, duplicate IDs, and unresolved footnote
  links are hard conversion errors and are recorded in the audit report.
- Figure captions are taken only from explicit `figcaption`/`title-f` structures;
  page-number spans and duplicated source figure numbers are not prose. Tables are
  emitted as structured Markdown and checked for row/column counts before Typst.

## PDF calibration and reconciliation

- Use the 929-page Adobe InDesign/Distiller print PDF (504 × 657 pt) to verify
  print trim, chapter starts, heading order, table/figure presence, and representative
  text. Its page numbers are provenance only and must not become generated link labels.
- Use the 2161-page Calibre 4.22 Letter PDF (612 × 792 pt) only as an independent
  EPUB reflow/text/image cross-check. It is not a second print edition: the same
  semantic volume is expanded by reflow, different cover/matter handling, and raster
  image transport. Its pagination and cover matter are not layout targets. Classify
  disagreements as text, structure, asset, or metadata differences in `output/audit/`.
- Expected print-PDF chapter starts are recorded by the converter from the PDF TOC;
  the generated B5 edition intentionally reflows. Compare semantic landmarks rather
  than requiring identical page numbers.
- The book has 16 numbered chapters, appendices A–E, glossary, index, and back
  matter. Keep the source's section numbers in visible headings while using stable
  generated labels for links.

## Typst and edition rules

- All three editions derive their chapter files from the shared Markdown tree. The
  English edition is source-faithful. The dual and Chinese trees consume the
  reviewable sidecar at
  `.agents/skills/systems-performance-enterprise-and-the-cloud/references/translations/zh/`.
  The current sidecar is machine-translated and remains
  `machine-translated-needs-review` by default. On 2026-10-04 the user explicitly
  approved the bilingual edition for release before complete-text review. The
  book-local `editorial/content-audit/release-policy.json` records this override;
  dual uses `user-approved-for-release` and `release_ready=true`. Preserve the
  machine-translation origin and incomplete full-text review as separate facts.
  Other editions retain their own approval status. The local translator uses protected
  Markdown batches through the Google Translate web UI, keeps code/URLs/anchors/
  formulas/table delimiters invariant, and records structural fallbacks in its log.
  The dual renderer pairs complete semantic blocks (heading, paragraph, list,
  table, figure caption, note, and footnote) with English first; invariant
  commands, identifiers, URLs, and code remain single-copy as documented in the
  edition contract.
- Long code examples use `technical-code` semantics rather than hand-inserted line
  breaks. Keep shell, DTrace, BPF, SQL, C, Java, and pseudo-code literals byte-faithful
  in Markdown and Typst raw blocks.
- Mathematical notation is sparse and is recognized from explicit source math
  elements or reviewed display blocks only. Do not interpret shell `$`, awk `$1`,
  regular expressions, or metric names as Typst math. Preserve unverified formula
  text literally and log the decision.
- Preserve source figure numbering and captions. Asset copies under each edition's
  `assets/figures/` must originate from the Markdown image tree and appear in the
  edition source map; no edition may reference the raw EPUB directly.
- Use the supplied EPUB cover unchanged as page 1 and the user-approved public-domain
  Claude Monet painting The Japanese Footbridge (1899) as publisher cover art on page 2. In this book,
  the higher-resolution cover raster extracted from page 1 of the 929-page print PDF
  is selected over the lower-resolution EPUB cover; record both checksums and that
  selection. Record dimensions, source, rights, and relevance in every edition
  contract.

### Publication corrections (user requirements, 2026-10-01)

- Bilingual tables are two complete tables, English followed by Chinese. Both
  use identical column widths and corresponding row heights (the maximum of
  measured English/Chinese cells). Each owns its caption and repeated column
  headers. Code, identifiers, numbers and units remain invariant. Parse pipes
  inside Markdown inline code as literal content, never table delimiters.
- Use native body paragraphs with one shared 1.1em paragraph gap and 0.68em leading. English remains 10pt; bilingual Chinese body glyphs (including prose lists) use a tested 9.5pt optical compensation because Noto Serif CJK SC appears heavier at the same nominal size. Do not apply this reduction to headings, tables, figures, captions, notes, or code. Use bundled Libertinus Serif and Noto Serif CJK SC.
- Prose pairs retain English-then-Chinese reading order but may break naturally
  across pages. Do not keep a whole paragraph pair unbreakable. Recto breaks
  are for chapter/matter openers; numbered subsections flow with their text.
- Numbered figures may float to a nearby page top, preserving source image
  bytes, placed width and complete adjacent captions. Subsequent prose fills
  the available area. Check that floats remain near their references.
- Block code is syntax colored (explicit user override of the monochrome house
  default), using pinned Pygments 2.18.0. Recover shell sessions, commands, C,
  tracing syntax and other lexical types through the source-traceable classifier
  in `code_highlight.py`; literal output/notation remains neutral. Tokenization
  must reconstruct every source character, including the final output line.
  Listings stay at 8pt and may break at source-line boundaries. Overlong tokens
  have invisible discretionary display breaks; raw assets are unchanged.
- Typeset the index in two columns with a full-width opener title, 9pt text,
  ascender/descender line bounds and readable spacing. Keep all 26 alphabetical
  group symbols invariant across languages; permit long identifiers to wrap at
  separators without altering their source characters.
- Display current-edition physical folios in the index, with source print numbers
  retained in brackets. Resolve the folio from the existing nearest retained
  semantic anchor; state this precision visibly and do not promise an exact page boundary.
- Restore print-page index references using the authoritative EPUB page-span
  order and the nearest preceding retained semantic anchor. Preserve printed
  numbers and record this navigation precision in the source manifest; never
  claim exact original page-boundary positioning. Index cross-references use
  zero-size metadata anchors at their corresponding entries.
- Correct source labels to attach to the actual headings, figures and table/code
  starts. A label preceding a movable block can attach to the previous element.
- The current supplied body rasters largely render around 140ppi at full live width. The print authority also embeds them as rasters (e.g. Figure 1.1: 776×502 pixels, no vector drawing paths). Preserve source dimensions and bytes; report the 300/600ppi target shortfall in the contract and profile audit. Do not claim that upsampling supplies missing detail.
- Every build records a full-page publication sweep, complete table/listing
  inventory, actual page numbers and remaining whitespace classifications. The
  generator must never claim it has inspected a not-yet-built PDF.

### Page-furniture landmark policy

The shared role-history query previously failed to converge for this large book.
The book queries paired zero-size markers before and after each semantic recto
break. Opener markers suppress running heads; the intervals between paired
markers identify automatic blank versos and suppress all their furniture. Headers and footers test
whether a mark or blank interval belongs to their current physical page; they do not emit
metadata or affect the body measure. The common helper lives in
the overlay’s `scripts/page_furniture.typ` and is consumed by the local generator for all
three editions. Physical page constants are regression baselines only, never
rendering inputs. Recheck convergence, odd opener parity and centered folios
for every edition after layout changes.

## Output artifact contract

- Each edition contract declares `output_pdf = "output/build/systems-performance-enterprise-and-the-cloud-typst-<edition>.pdf"`. Both the local builder and central exporter must obey it.
- `output/build/` contains exactly one current PDF. Rebuilds and probes stay in external staging; obsolete artifacts are moved to a recoverable archive outside the workspace and recorded in a migration ledger.
- The builder validates the staged PDF, repeats the compile with the same batch timestamp and requires identical hashes before replacing the current PDF. `output/audit/build-record.json` records the actual commands, timestamp, input hashes and output hash.
- The central exporter selects the dual edition; refresh the local and central audits from that actual PDF, using its per-book manifest timestamp. Review scripts must derive the batch path and canonical filename from contracts and manifests.

## Required checks and regeneration

From the book root, run:

```sh
python3 .agents/skills/systems-performance-enterprise-and-the-cloud/scripts/extract_epub.py
python3 .agents/skills/systems-performance-enterprise-and-the-cloud/scripts/audit_sources.py
python3 /home/xuntingmu/.agents/skills/typst-book-production/scripts/validate_workspace.py \
  --workspace-dir . --source-language en
python3 .agents/skills/systems-performance-enterprise-and-the-cloud/scripts/validate_translation.py \
  --source-dir systems-performance-enterprise-and-the-cloud-markdown/chapters \
  --translation-dir .agents/skills/systems-performance-enterprise-and-the-cloud/references/translations/zh \
  --report .agents/skills/systems-performance-enterprise-and-the-cloud/references/translations/validation.json
```

For each Typst edition, use `python3 .agents/skills/systems-performance-enterprise-and-the-cloud/scripts/build_edition.py --edition en|zh|dual`.
Build twice with the same explicit `--timestamp` and compare the resulting SHA-256.
The central full-book export is `python3 ../scripts/export_books.py --books
systems-performance-enterprise-and-the-cloud` and selects the bilingual edition. Capture raw Typst stderr in `output/audit/compile.log`, then run
`validate_book.py` with the edition manifest, PDF, compile log, and B5 dimensions.
The release record must name inspected pages, source coverage, text/image/link counts,
PDF checksums, and unresolved source/rights risks. A validator pass does not waive
the unresolved copyright, font, or physical-proof requirements.

### Cover and contents design (user request, 2026-10-01)

- User explicitly replaces the historical line drawing with a classic painting. This authorization overrides the generic publisher-cover art rule for this book only. Use the entire unaltered National Gallery of Art CC0 download of Claude Monet, The Japanese Footbridge (1899); record source, rights, pixel size and SHA-256 in assets/covers/boliu/provenance.json. Keep the original cover on page 1 and visible batch stamps on both covers.
- Contents preserve every native entry and destination. User correction supersedes the previous no-leader design: follow DDIA with black bold chapter entries (12pt above/6pt below), blue sans sections (9pt; 12pt indent; 23pt number column; 2pt above/8pt below), and gray serif nested entries (8.4pt; 24pt/32pt for level 3, 36pt/42pt for level 4; 8pt below). Retain native dotted leaders and right-aligned physical folios. Keep major contents entries sticky with the following entry so a chapter label cannot be stranded at a page bottom. Contents entries retain their own matched language sizes. The earlier statement that the user requested no leaders was incorrect. Shared contents-style.typ owns the design.
- In every bilingual contents entry, align the Chinese title's first character
  with the first English title letter after the numbering column. For example,
  文 in 文件系统 aligns with F in `8 File Systems`, not with 8. Numbered major
  entries use a separate measured number column and a shared title column;
  preserve this alignment for double-digit chapters, wrapped titles, all native
  section levels, and scoped chapter-print contents. Unnumbered entries retain
  their title column. Check glyph coordinates in the full and chapter PDFs.
- User explicitly requires the publisher imprint `伯流出版社` at the bottom center of page 2. The bottom group ends with the centered imprint, with the export timestamp separately below it in the margin. Do not put the imprint at the top or left.

### DDIA quality benchmark (user request, 2026-10-01)

- Compare against the actual 965-page DDIA V2 bilingual PDF (local release v1.0.4, timestamp 2026-10-01 11:50:41 UTC), not only its declared tokens. Freeze the reference checksum and write measured comparisons and visual pairs in output/audit/ddia-benchmark.json and output/preview/ddia-comparison/. Keep DDIA read-only.
- Chinese structural headings use the same bundled Noto Sans CJK SC bold face as DDIA. English body text remains 10pt; bilingual Chinese body glyphs use Noto Serif CJK SC at 9.5pt for optical balance. Tables, figures, captions, notes, and code retain their component-specific sizes.
- Bilingual footnotes alone use Latin text 8pt and Chinese glyphs 7pt with a compact 0.18em language gap; verify this font pairing visually. Other Chinese components retain their own size. The shared bilingual-footnotes.typ owns this exception.
- A bilingual publisher cover includes both language titles. PDF metadata identifies Brendan Gregg, the original second edition, and the unofficial study/translation status.
- Index references show current-edition physical folios followed by the original
  print number in brackets. Both navigate to the nearest retained semantic anchor.
  State this precision visibly; the folio identifies the anchor page, not an
  exact reconstructed original page boundary.
- Benchmark every major component, source fidelity, translation QA, PDF interaction, deterministic production and physical-print readiness. Record statuses as measured parity, user-approved difference, remaining gap, or not verified. Do not turn structural validators into a claim of editorial/print completion.

### Audit remediation (user requirements, 2026-10-03)

- Center figure caption text by default, including wrapped English and Chinese
  lines; center the complete image/caption group. This updates the previous
  generic left-aligned caption default. Table captions remain above their tables.
- Tables may span pages. Repeat the table identity, language, continued marker,
  and original column headings on every continuation page. Untitled source
  tables use meaningful semantic identities, without invented author numbers.
  Paired language copies share column widths, row heights and title/header height.
- Keep figures above the bottom footnote area. Caption footnotes use nonfloating
  figures, native note destinations and complete note bodies. Keep each bilingual
  footnote pair together when it fits one live page. Verify all 197 notes in both
  languages against actual PDF footnote text, including mixed Latin/CJK fonts.
- In bilingual footnotes, align the first translated glyph with the first English
  body glyph after the native superscript marker, never with the marker itself.
  The shared `bilingual-footnotes.typ` must measure the current marker width so
  one-, two-, and three-digit footnote numbers retain this alignment; a fixed
  left inset that only matches the marker column is incorrect. Keep this rule
  covered by rendered PDF regression fixtures.
- User accepts the existing source image clarity. Preserve source bytes and
  placed widths; record actual resolution without making it a remediation gate.
- Correct reviewed translations in the authoritative Chinese sidecar, with a
  per-line correction ledger and refreshed hashes. Generate all editions through
  build_typst.py and build_edition.py; preserve raw English/code/link targets.
- Audit reports must identify the actual PDF checksum and timestamp. A staged
  validation does not constitute installation, skill synchronization or central
  export. Translation remains machine-translated-needs-review until full
  technical editing has actually been performed, unless the explicit user release
  approval above applies. Release approval never implies completed full-text review.

### Standalone chapter printing (user request, 2026-10-03)

- The default chapter-print edition is bilingual, preserving full-book folios
  and exact body page geometry. Export chapters 1–16, appendices A–E, glossary,
  index, front matter and back matter as 25 separately named lowercase PDFs.
- Use the central entry `python3 books/scripts/export_books.py --books
  systems-performance-enterprise-and-the-cloud --chapters`. It captures one new
  timestamp and routes to the local `scripts/export_chapters.py`.
- Keep the current full-book PDF and its timestamp unchanged. Read its verified
  checksum and build record; extract whole body pages without reflow. Compile
  the existing two cover helpers with the chapter batch timestamp. Identify
  the part and its source-page range on the publisher cover. Preserve cover
  image bytes, author, original second edition, recorded translation origin and
  current release approval.
- Keep both covers and insert a scoped native contents section after them.
  Reuse `book/template.typ`, `book/matter.typ` and the full-book outline renderer:
  preserve bilingual titles, hierarchy through depth 3, fonts, sizes, colors,
  hanging indents, dotted leaders and right-aligned original full-book folios.
  Heading stubs with original page counters are compilation-only destinations;
  discard them and remap every contents link to the actual retained heading.
- Pad an odd-length contents section with a furniture-free blank verso so the
  first body page is odd. Preserve the source's recto/verso order and add a blank
  final verso only when necessary to make the file page count even. Preserve
  source blank versos and furniture. Record each part's contents page count and
  first physical body page in the manifest and printing index; body printing
  must no longer assume physical page 3.
- Prepare all part offsets before remapping links. Resolve both within-part and
  cross-part destinations using the target part's cover-plus-contents offset.
  Verify every scoped contents entry and link against master outline titles,
  original folios and exact heading coordinates before publication.
- Retain local links, resolve named destinations, and remap cross-part links
  to relative sibling PDFs with correct raw-PDF destination coordinates.
  Preserve original URI links. Check all annotation targets, text spans, fonts,
  positions, image digests and vector paths against the full book.
- Validate all parts and same-batch repeated hashes before publishing the
  complete set. Keep local current files in `output/chapters/`; the full book
  remains the sole PDF in `output/build/`. Mirror the print set into
  `export/systems-performance-enterprise-and-the-cloud/`, with a searchable
  manifest and printing index; do not create a ZIP. Keep the latest complete
  bilingual PDF directly in `export/`. Archive prior sets outside the
  workspace, record their locations and reject master-file drift.

## Mixed-script font invariant

- The translated block's Latin words, abbreviations, digits and versions retain
  the English face, size, weight and style for the same content role. Body Latin
  remains Libertinus Serif 10pt even inside Chinese; CJK body glyphs alone use
  9.5pt. Footnote Latin remains 8pt; CJK footnote glyphs alone use 7pt.
- Use the shared `zh-content` helper, Latin-first chains and `dual-list`; do not
  style a whole Chinese block with a CJK font or reuse `dual-caption` for lists.
  Headings, contents, table cells, captions, notes and indexes retain their own
  component scales. Inline code, technical code and math retain their faces.
- Audit the actual complete PDF character by character with the core
  `audit_mixed_fonts.py`; prove same-term font/size/style equality with 3.4.1
  (`Futex`, `OProfile`, `RCU`, `epoll`) and role fixtures. Verify optical CJK
  adjustments also cover list items, without changing Latin or code sizes.
