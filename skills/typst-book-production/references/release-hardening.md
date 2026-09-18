# Release hardening for iterative books

Read this after a non-trivial content, converter, template, or pagination
change and before calling a multi-edition book release-ready. It captures
failure modes that a successful Typst compile and a single-page spot check do
not expose.

## Keep editions semantically synchronized

For every required edition, regenerate from the same Markdown authority and
the same reviewed asset/source map. A shared decision must have one owner:
the common template, a named semantic macro, or one renderer data table used
by all editions. This includes figure and table widths, caption alignment and
spacing, code-block treatment, keep/break policy, and other repeated geometry.

Do not copy a layout map into one edition and hand-tune the other editions.
After a shared change, compare the editions by semantic asset identity and
reading order, not by page number. For every figure and table, check asset
identity, placed width, aspect-ratio preservation, crop boundaries, caption
presence, complete translation where required, and title/note presence. Compare
placed physical dimensions, not source-pixel dimensions. A language-specific
exception is acceptable only when the book contract names its reason and the
exception is visible in the release audit.

## Sweep the whole book, not only the reported page

Begin at physical page 1 and inspect the complete PDF. Use contact sheets or a
page-thumbnail index to find patterns, then inspect suspicious pages at actual
print size. At minimum, look for:

- clipped or unexpectedly tiny figures, distorted aspect ratios, and captions
  separated from their figures;
- missing table captions, table notes, repeated headers, or figure captions;
- captions and notes that look like ordinary body paragraphs because their
  block alignment, type treatment, or spacing is indistinguishable;
- large unexplained bottom whitespace, orphan headings/captions, accidental
  blank pages, and page breaks that split a semantic unit;
- code that is clipped, unhighlighted when the project requires highlighting,
  or missing its source-language label.

Classify each anomaly before fixing it: an explicit break, keep constraint,
oversize asset, caption association, heading policy, duplex parity, or
renderer divergence. Fix the semantic macro, shared token, source asset, or
converter rule that caused it. Do not cure ordinary flow with page-number
spacers, blank paragraphs, arbitrary `v()` calls, or edition-only patches.
After each fix, rebuild all required editions and repeat the affected whole-book
pattern scan so a local improvement does not create a later cascade.

## Preserve semantic furniture

Figures and tables are not just images or grids. Center the complete figure or
table wrapper, keep its title/caption attached according to the house style,
and reserve visibly distinct spacing from surrounding prose. In bilingual
editions, captions, table titles, and notes require complete paired translations
unless the contract explicitly marks the material invariant; a shortened
summary is not a translation.

Table captions belong above the table and notes/units below it. Use the
semantic table header so continuation pages repeat it. Verify these elements in
the generated PDF because a converter can silently drop Markdown titles or
notes even when the table body survives.

Preserve the language of each fenced code block. When the house profile calls
for language labels, render a restrained label at the block's upper right from
the fence metadata; it is part of the block chrome, not an ordinary caption.
Keep it out of the code measure and verify that neither the label nor the code
is clipped. Syntax coloring, if enabled by the project contract, must come from
a tested code renderer and must not leak raw markup or unstable terminal colors
into the PDF.

## Test navigation in the PDF itself

Contents text and a successful compile do not prove navigation. Inspect the
emitted PDF link annotations and destinations with PyMuPDF or an equivalent
parser. For every visible contents entry, confirm that:

1. a real internal link annotation exists;
2. its destination page is valid and lands on the intended heading or matter;
3. the printed page number agrees with the destination's physical page; and
4. outline/bookmark depth and contents depth are intentional. A deeper outline
   entry omitted from a shallower contents view is a design choice, not by
   itself a link failure.

Also test representative figure/table/code references and external links. Do
not diagnose a viewer's stale cache as a source defect without reproducing it
from the freshly built PDF and recording the edition, viewer, entry, and
destination.

## Reason about covers and duplex output physically

Count from physical page 1, not from a logical chapter counter. Inspect both
covers at trim size: the source cover occupies the full page according to its
documented crop/bleed, and the publisher cover is a complete page with its
publisher mark and edition identity placed according to the design system.
Do not embed a cover as a small centered image on a paper page. Verify the
cover sequence, mirrored inside/outside margins, recto chapter starts, outside
folios, intentional blank versos, and contents/front-matter parity together;
changing one front-matter page can shift every later physical page.

## Keep release artifacts truthful and reproducible

The final `output/build` directory contains exactly one current PDF. Put
independent rebuilds and diagnostic renders outside that directory. After every
release rebuild, regenerate the page count, source/layout audit, and output
SHA-256 from the actual PDF; never report stale audit data. Keep the raw Typst
diagnostic log and require it to be empty for a release. Where the contract
claims byte reproducibility, build twice from the same inputs and compare
hashes, then investigate any difference before handoff.

Record the editions, commands, font/input hashes, inspected page landmarks,
intentional pagination changes, unresolved anomalies, and the final PDF hashes
in the release record. A validator PASS is evidence for its checks only; it is
not a substitute for the whole-book visual and PDF-interaction audit.
