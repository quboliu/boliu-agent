# Verification

Run these checks before calling a Typst book complete:

Use [production pipeline](production-pipeline.md) for actual-project manifest/
PDF checks, fixed build timestamps, source reconciliation and before/after
visual comparisons. For requested annotations, also run the converter's anchor,
acceptance and emission checks from [content audit](content-audit.md).
For iterative multi-edition changes, apply the whole-book and PDF-interaction
checks in [release hardening](release-hardening.md).

Read [editorial style](editorial-style.md) for the profile-specific acceptance
criteria. Confirm the zero-indent paragraph style in all three editions.
Apply [duplex printing](duplex-printing.md): verify physical odd/even margins,
outside folios, recto starts, blank versos, and cover sequence in the actual PDF.
For shared-template changes, run the bundled PDF smoke check and inspect its
rendered pages. It catches trim, cover-order, numbering, code-color/size, repeated
header and blank-verso regressions, but human proofing is still required.

Run `BOLIU_FONT_PATH=/path/to/fonts python3 -m unittest discover -s scripts
-p 'test_*.py'` from this skill directory (with PyMuPDF and Typst installed).
These reusable checks cover source-hash drift, long-cover capacity, literal
equation numbering/references, caption alignment and bilingual pair pagination.
Source conversion tests belong to each book project; see the acceptance cases
in [Markdown conversion](markdown-and-matter.md).

For PDF authorities, add the project-specific note-ownership, link-target,
vector-asset, code-indentation and measured geometry cases from
[PDF source recovery](pdf-source-recovery.md). These checks are not implemented
by the generic validator and must be verified in the actual project.

1. **Content:** every declared source element has the expected output element;
   bilingual editions also have a matching translation element in the correct
   order.
2. **Structure:** heading hierarchy, numbering, table of contents, labels,
   citations, footnotes, and external/internal links preserve their intended
   semantics. Inspect emitted PDF annotations and destinations; source markup
   or visible contents text alone is not link evidence.
3. **Build:** the documented command succeeds with the declared fonts, root,
   and Typst version; its raw diagnostic stream is captured and empty, and the
   PDF opens and has the expected page count. Run `validate_book.py` with
   `--compile-log`; PDF validation alone does not invoke the compiler. Treat
   every unreviewed diagnostic as failure, and always reject font fallback and
   `document did not converge` warnings even when a PDF was emitted.
4. **Assets and code:** no missing-image placeholders, font fallback surprises,
   malformed raw code, truncated code indentation, or table/figure geometry
   regressions remain. Every edition file under `assets/figures/` is declared
   in the source map or explicitly excluded with a reviewed reason.
5. **Visual QA:** rasterize and inspect the complete page sequence, using
   thumbnails for pattern detection and actual-size detail for a chapter opener,
   dense prose page, code page, footnote/notes page, table page, and image-heavy
   page. Check overflow, widows/orphans, pair adjacency, captions, running
   furniture, page bottoms, unexpected whitespace, and cross-edition geometry.
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
