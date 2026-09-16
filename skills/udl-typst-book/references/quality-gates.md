# UDL release gates

Run these checks after regeneration. A PDF that merely compiles is not a release candidate.

## Source and structure

- The generated include order matches the source chapter and appendix order.
- All source paragraphs, headings, problems, notes, figures, tables, and code blocks are present.
- No `TODO`, unresolved placeholder, raw conversion marker, empty image, or accidental generated note section remains.
- Equation tags are present in source order and the converter emits no legacy `#h(2em)` equation-number spacer.

## Links and annotations

- Every original internal page target that has a source definition remains defined and clickable.
- Every external URL remains present and clickable.
- The paragraph-note manifest and generated paragraph-note markers have equal counts and matching labels/targets.
- No margin note is rendered at the end of a chapter. A note must occur in the same semantic paragraph block as its owner.
- Spot-check page 32's `Appendix A: Argmin function`, page 35's `Notebook 2.1: Supervised learning`, and page 35's `Problems 2.1–2.2`.

## Typography and geometry

- Compile with the pinned Typst version and explicit font paths where the environment provides them.
- Check for missing glyphs, font fallback, duplicate labels, overflow, clipped content, and unexpected blank pages.
- Formula bodies are centered in the reading column and tags share one right edge. The tag must not shift the formula's optical center.
- Captions stay with figures, short tables do not split, and headings do not strand at a page bottom.
- The PDF has the intended A4 geometry and a stable page count after a repeat build.

## Visual sample

Render at high resolution and inspect:

1. front matter and a chapter opener;
2. original pages 32–35 after the layout shift;
3. a dense equation page with multiple aligned formulas;
4. a page with several adjacent paragraph notes;
5. a figure-heavy page using an official vector asset;
6. a raster fallback, a table, a code block, Notes, Problems, and an appendix page.

Record any accepted source-PDF differences in `layout-decisions.md` before handoff.
