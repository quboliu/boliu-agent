# Verification

Run these checks before calling a Typst book complete:

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

Record source coverage, unresolved anomalies, inspected pages, output checksum,
and the build command in the release record. A clean compile alone does not
establish fidelity or reading quality.
