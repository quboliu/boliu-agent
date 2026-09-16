# Editorial and composition rules — boliu-b5-2

Read before composing any edition. This is the house style for Chinese,
English, and bilingual books. It adds concrete decisions to the measured DDIA
baseline; these are house choices, not claims of universal publishing standards.

## Paragraphs and restraint

Use flush-left paragraph starts in all three editions: first-line-indent = 0pt.
Distinguish paragraphs with Typst spacing = 1.1em and leading = 0.68em at 10pt.
Do not insert blank paragraphs, full-width spaces, or tabs to simulate indent.
This includes the first paragraph after a heading and both bilingual streams.
List hanging indents, block quotations, and footnote label alignment serve
different purposes and do not change the body-paragraph rule.

The alternatives are first-line indentation or paragraph spacing; neither is a
universal requirement. We deliberately retain DDIA's open paragraph style for
technical and bilingual reading. See
[Butterick on paragraph boundaries](https://practicaltypography.com/first-line-indents.html).
Typst leading measures the gap between font-defined line edges, NOT the
baseline-to-baseline distance; 0.68em is not a 6.8pt baseline pitch. Likewise,
declared block spacing can collapse at boundaries. Record actual measured
baseline pitch and visible heading gaps in the proof, not just source tokens.
See [Typst paragraph semantics](https://typst.app/docs/reference/model/par/).

Use white pages, black body text, neutral grays, and one restrained blue accent
(#1a5276). No shadows, gradients, badges, ornamental frames, rounded panels, or
translation backgrounds. Inline code has no background. Tables have no striping
by default. Code blocks alone may use a very pale gray (#f7f7f7) rectangle.
Use whitespace and type weight to communicate hierarchy. Limit bold to
meaningful emphasis; never use color as the sole carrier of information.

## Language, measure, and pagination

- Shared B5 live area is 141 × 208mm. Keep one reading column. Indexes may use
  two columns with a recorded gutter; bilingual prose remains sequential.
- Declare font chains for Latin, Chinese, code, and math. CJK headings must have
  an explicit Chinese face. Chinese body remains 10pt, equal to English.
- Chinese punctuation stays with its phrase: no opening punctuation at line
  ends or closing punctuation at line starts. Remove extraction-induced CJK
  spaces narrowly; never normalize identifiers or URLs as prose.
- English text uses language-aware hyphenation; headings and covers do not.
  Review rivers, excessively stretched lines, and repeated hyphenated endings.
  Use true punctuation in prose while preserving literal punctuation in code.
- Keep at least two prose lines on either side of a page split where possible.
  Keep a heading with at least two following body lines; inspect rather than
  assuming a sticky block guarantees this. Never shrink whole chapters to fit.
- Chapter openers begin on odd physical pages, omit running heads, and have a
  centered folio. Automatic blank versos have no furniture. Regular pages show
  a short explicit chapter title and folio, not a long bilingual heading.
- Keep source hierarchy and numbering; a wrapped heading hangs under its title,
  not its number. Contents use real headings, clickable targets, and hanging
  entries; test long translated titles. Reset footnotes at chapters consistently.

## Code

Blocks: 8pt DejaVu Sans Mono, 0.5em leading, 9pt horizontal / 7pt vertical
padding, full live width, square corners, no syntax colors, no shadow.
Inline code: 8.6pt, no chip or background, no hyphenation. Keep long multiword
snippets breakable at their original spaces; never box an entire long command.
Preserve whitespace, indentation, literal quotes, and Unicode exactly.

No clipping or silently truncated lines. Prefer a source-valid line continuation,
a landscape dedicated page, or an explicitly documented layout exception for
long code; never silently insert token breaks or reduce below 8pt.
Long listings may split at line boundaries, with continuation captions when
needed. Add line numbers only if referenced by the text. CJK comments need a
declared CJK fallback and a visual alignment check. Test copy/paste round trips.

## Mathematics

Use native Typst math, New Computer Modern Math, and the 10pt body context.
Inline expressions follow prose rhythm; display equations are centered with
8pt above/below. Preserve source numbering and labels. Otherwise number only
referenced display equations, on the right; do not number every inline formula.
Use native labels/references, never hand-positioned number text.

Align multiline derivations at relational operators, break at meaningful
operators, and keep a derivation together when it fits. Split a long derivation
deliberately at a logical step; never shrink the entire equation to illegibility.
Variables are math italic; operators and units are upright. Define symbols and
units consistently. Check subscripts, radical extents, fractions, matrix
alignment, equation-number collisions, and glyph coverage. In bilingual
editions share invariant equations; translate explanatory prose adjacent to them.

## Tables

9pt text; 6pt horizontal / 5pt vertical insets; 1pt top/bottom and 0.6pt header
rule; no vertical rules, background striping, or decorative cells by default.
Use a real repeating table.header. Caption goes above and stays with the header
and at least the first data row. Notes/units explanations go below at 8pt.
Table-caption gap starts at 6pt; verify the resulting block-spacing interaction.

Specify column widths or fractions based on content, summing to the live width;
do not guess equal columns for a prose-heavy table. Text is left aligned,
numeric columns right aligned or decimal-aligned, units in headers. Repeat
headers on subsequent pages and identify continuation in long tables. Keep rows
intact where feasible; split overheight rows semantically with a recorded policy.
Never rasterize a table or shrink all text to force width. Wide tables get a
reviewed landscape page or a meaningful split. Bilingual copies share geometry.

## Figures and captions

Prefer vector art for diagrams. Standard widths are 60%, 80%, or 100% of 141mm
(84.6, 112.8, 141mm), selected for label readability. Preserve aspect ratio.
Captions: 8.5pt, left/ragged-right within a centered block 92% of live width;
4pt below the image; 8pt outer space above/below the figure group.
The caption width is relative to the live area, not the image.
Keep image and caption together, within the live height. Oversize figures need
a dedicated page or documented split, not an unbreakable overflowing block.

Use native figure labels/references for numbered illustrations. Preserve source
numbers and bilingual caption correspondence. At final physical size, target
at least 300ppi for continuous-tone images and 600ppi for raster line art;
prefer vectors for fine engraving. These are house targets, subject to the
printer's requirements. Calculate effective ppi from placed size, not metadata.
Never treat upsampling as recovered detail. Check labels at actual print size,
grayscale legibility, crop boundaries, and caption attachment.

## Other matter

Footnotes default to 8pt; optical CJK reduction requires a tested font pair.
Keep markers and notes linked, notes on their reference page when feasible,
and distinguish gaps within bilingual notes from gaps between numbered entries.
Notes use a 0.5pt gray left rule, 10pt left inset, 9.5pt text, 10pt outer gaps;
no colored panel. Quotations use indentation, not oversized quotation ornaments.
Lists use real list elements and hanging alignment (bullet body inset 1.2em,
numbered 1.5em, item spacing 0.4em); retain source ordering and nesting.

Front matter order: original/fallback cover, publisher cover, edition/source
credits, contents, preface, then chapters. Optional matter exists only when
supported by content. Bibliography uses one consistent citation style and
clickable identifiers; indexes retain real destinations and a readable hierarchy.

## Delivery gates

Inspect every page for overflow and blank-page anomalies; inspect representative
pages closely at actual size and 144–288ppi. Test all three editions after shared
template edits, including long titles, multipage prose, code, equations, tables,
figures, footnotes, and both cover paths. Log inspected page numbers and issues.

Before calling a file print-ready, obtain the print specification: binding and
gutter allowance, trim, bleed, color/ICC requirements, PDF profile and font
embedding. Confirm the printer's preflight and a physical-size proof. The B5
template alone does not certify printing suitability. Keep the reader PDF's
two-cover sequence; any printer-specific jacket/interior separation must be an
explicit additional export. Do not insert a blank page before physical page 2.
