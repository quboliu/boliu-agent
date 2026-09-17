# PDF source recovery and acceptance cases

Read when a PDF is the declared authority or when extraction has damaged reading
order, notes, code or assets. These methods consolidate useful experience from
the retired UDL and PDF-dual skills; they are instructions for project-owned
conversion and tests, not a universal extraction algorithm.

## Authority and output contract

Keep the original PDF immutable, with checksum and source/version recorded.
Map source page labels and semantic elements to the generated edition; reflowed
page numbers are not stable identities. Reconcile extracted Markdown, supplied
equation sources, bibliography and official assets against the declared authority.
Do not silently prefer a different edition or replace content with a summary.

Source-page anchors belong in provenance and audit records. Never reuse them as
internal cross-reference targets in a reflowed edition. Map them to stable,
unique semantic labels instead; page-number-derived labels can become cyclic
layout dependencies and cause Typst convergence warnings.

For a book, preserve content and important visual relationships while applying
the house typography, two covers and duplex rules. For a paper, course note or
slide adaptation, confirm the requested document type and layout separately;
do not force book covers, B5 or chapter starts onto a non-book document. Original
slide followed by its translated counterpart is an optional, explicitly requested
format, not a universal bilingual layout. Define page order, geometry and required
verification in that project's contract; adapt book-only checker assumptions
locally rather than expanding the generic validator with format exceptions.

## Paragraph-owned margin notes

PDF geometry can split a side note's label, title and links across paragraphs or
insert them inside a sentence. First inventory visible source notes and their
owning paragraphs using the PDF, not extracted adjacency alone.

For each note, record source page/region, owner paragraph ID, fragments, complete
label, every target, and chosen output placement. Join fragments only with visual
or semantic evidence of common identity. Preserve distinct targets in ranges and
source order for multiple notes; ordinary citations and figure references must
remain ordinary links. Remove only the positively identified extraction fragments.
If a note is missing from extraction, use a reviewed supplemental record with its
PDF location and target, not an invented completion.

Preserve ownership in the chosen layout. Paragraph-end parenthetical links are
one approved project adaptation, not a rule for every book; marginal or footnote
placement needs its own decision. In bilingual work keep the note attached to
its owning paired unit. Never collect paragraph-owned notes at chapter end merely
to simplify conversion. Uncertain ownership blocks that transformation for review.

Reconcile source-note and emitted-note IDs, counts, labels, destinations and owner
IDs. Count equality alone does not establish correctness. Test split titles,
duplicate fragments, missing notes, multiple notes, range targets and legitimate
inline links. Sample original and generated pages at the same semantic landmarks.

## Figures and PDF vectors

Prefer verified matching official vector assets. Confirm edition, labels and
visual content, caption, checksum and rights before replacing an extracted
raster. Filename, dimensions, OCR text, or image similarity may nominate a
candidate but do not prove identity. When the original PDF has
vector paths but no separate asset, a vector-preserving region crop may retain
quality better than a screenshot. Record source page, crop coordinates, checksum
and permission; inspect clipping, labels and embedded fonts. Where the toolchain
needs another format, preserve vectors where possible and visually verify conversion.
If no safe match exists, retain the original raster bytes and report effective
resolution; upsampling is not recovered detail.

## Code recovery and invariant blocks

Keep one code/formula object per semantic occurrence unless the contract says
otherwise. Deduplicate adjacent bilingual code only after checking identity and
the translation policy for comments; do not merge genuinely different examples.
Keep input snapshots unchanged and normalize derived Markdown/Typst/PDF together.

Before deduplication select the source-faithful indentation, not whichever copy
appears first. If extraction flattened code, recover nesting from PDF geometry
and authoritative code assets. A syntax-aware formatter is a documented adaptation,
not evidence for guessed nesting. Pass leading spaces unchanged to Typst `raw`.
Check nested-line x-coordinates and copy/paste text in the exported PDF.

A multiline fenced program beginning with `#` is code, not a heading. Convert a
fenced one-line title only with source evidence; a one-line code comment is not
automatically a title. Test comment-led programs and literal markup examples.

## Running furniture and measured geometry

Repeated source headers/footers can enter extracted prose. Map them to source
page identity and a deliberate running-furniture policy; remove only confirmed
repetition, not chapter titles or meaningful page labels.

Check actual PDF geometry at representative landmarks, not just template values:

- Formula body centering and right-edge equation tags are independent checks.
  Long tags must not shift the formula body. Use semantic equation components;
  never attach numbers with literal spaces or an inline horizontal spacer.
- Measure the heading's last visible line to its first following body line,
  including bilingual headings whose labels are Latin-only. Choose thresholds
  from the house style or explicit source-preserving profile, not a universal
  10pt rule. Verify once-applied spacing and reject stranded headings.
- Inspect code indentation, paired-unit page breaks, captions and page endings.
  Flag isolated options, code fragments and detached captions, not only overflow.

Project tests must include an equation-heavy page, a multi-note paragraph, a
vector crop/raster fallback, comment-led nested code, a Latin-only heading pair
and a cohesive option group when those constructs occur. Review every page of
short slide decks or dense source material. Report coverage, output paths/page
count and unresolved anomalies; a clean compile or translated pilot is not a
complete edition.
