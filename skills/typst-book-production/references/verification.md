# Verification

Run these checks before calling a Typst book complete:

Read [editorial style](editorial-style.md) for the profile-specific acceptance
criteria. Confirm the zero-indent paragraph style in all three editions.
Apply [duplex printing](duplex-printing.md): verify physical odd/even margins,
outside folios, recto starts, blank versos, and cover sequence in the actual PDF.
For shared-template changes, run the bundled PDF smoke check and inspect its
rendered pages. It catches trim, cover-order, numbering, code-color/size, repeated
header and blank-verso regressions, but human proofing is still required.

1. **Content:** every declared source element has the expected output element;
   bilingual editions also have a matching translation element in the correct
   order.
2. **Structure:** heading hierarchy, numbering, table of contents, labels,
   citations, footnotes, and external/internal links preserve their intended
   semantics.
3. **Build:** the documented command succeeds with the declared fonts, root,
   and Typst version; the PDF opens and has the expected page count.
4. **Assets and code:** no missing-image placeholders, font fallback surprises,
   malformed raw code, truncated code indentation, or table/figure geometry
   regressions remain.
5. **Visual QA:** rasterize and inspect a chapter opener, dense prose page,
   code page, footnote/notes page, table page, and image-heavy page. Check
   overflow, widows/orphans, pair adjacency, captions, running furniture, and
   page bottoms.
6. **Publisher-profile QA:** compare the inspected pages with the named
   伯流出版社 tokens: page grid, body measure, type scale, vertical rhythm,
   heading attachment, figure/caption spacing, table geometry, and running
   furniture. Inspect page 1 and page 2 at output resolution: page 1 is either
   the exact high-resolution source cover or the neutral fallback; page 2 bears
   `伯流出版社`, the edition identification, and the documented lawful historical
   line drawing. Confirm that neither cover has headers, footers, or page
   numbers.

Record source coverage, unresolved anomalies, inspected pages, output checksum,
and the build command in the release record. A clean compile alone does not
establish fidelity or reading quality.
