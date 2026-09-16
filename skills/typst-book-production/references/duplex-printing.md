# Direct duplex printing

This requirement applies to all three language editions and every full-book
release. The PDF is portrait, left-bound, one book page per PDF page, in reading
order. It is ready for duplex / long-edge-flip printing. Do not impose spreads,
reverse pages, or switch to booklet mode in the primary deliverable.

## Physical page geometry

Use physical PDF page positions for recto/verso decisions, independent of visible
folios or restarted counters. Page 1 is the front/right recto; page 2 is its
back/left verso. In an open book, physical pages 2–3, 4–5, etc. face each other.

| Physical page | Side | Left margin | Right margin | Running folio |
| --- | --- | --- | --- | --- |
| Odd | Right / recto | Inside 19mm | Outside 16mm | Right / outside |
| Even | Left / verso | Outside 16mm | Inside 19mm | Left / outside |

Keep top/bottom margins 22/20mm and the 141 × 208mm live area identical across
the spread. Set Typst `binding: left` explicitly, not inferred from language.
Use `inside` and `outside` margins, never a single fixed left/right pair.
Baseline positions should agree across ordinary facing pages with the same
font metrics; review show-through and vertical rhythm at physical print size.
Typst's binding and margin semantics are documented in the
[official page setup guide](https://typst.app/docs/guides/page-setup/).

The 19mm inside margin is the baseline, not an allowance for every possible
binding thickness. For thick books, record the binding method and required
gutter, increase the inside margin as needed, and reflow/reproof the complete
book. Do not merely shift existing text into the outside margin.

## Sequence and furniture

- Physical page 1 is the original or fallback cover. Physical page 2 is the
  伯流出版社 cover, printed on its reverse. This user-required sequence takes
  precedence over the customary blank back of a cover. Neither carries folios.
- Main numbered chapters begin on odd physical pages using a recto break.
  Treat front matter separately; never force every small section to a recto.
- Insert and preserve blank versos where needed. They count in physical
  pagination but have no title, folio, rule, or other visible content.
- Ordinary running heads mirror: folio on the outer edge, short chapter title
  toward the inner edge. Chapter openers omit running heads and use a centered
  footer folio. Do not use displayed counter parity to choose sides.
- The baseline folio counter remains continuous, including unprinted cover and
  blank pages. If a project needs roman preliminaries or body numbering starting
  at 1, record that separately and still use physical parity for layout.
- An odd final page is printable: the back of its final sheet is naturally
  blank. A printer-requested explicit final blank must be unmarked. A multiple
  of four is required only for a specified booklet/signature imposition, not
  ordinary duplex printing.

## Handoff and proof

State print settings with the PDF: correct paper size (B5 baseline), actual size
/ 100%, portrait, one page per side, duplex, long-edge flip. Disable automatic
blank-page removal and booklet imposition. On A4 equipment, print B5 centered at
100% and trim if intended; automatic fit-to-page changes the calibrated design.
Landscape foldouts require a separately verified orientation/flip policy.

Check actual PDF trim, odd/even text origins, mirrored folios, recto chapter
starts, all inserted blanks, and page-1/page-2 continuity. Proof at least one
facing spread and a cover/first-chapter transition, then print a short duplex
sample if a printer is available. Record digital checks separately from a
physical print proof; do not claim the latter when it has not been performed.

The bundled template checker verifies mirrored page-rule geometry and folio
positions on both odd and even ordinary pages. Full-book checking must also
cover all pages, binding clearance, and the project's print specification.
