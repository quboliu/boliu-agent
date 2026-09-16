# UDL layout decisions

This file records decisions that are specific to the UDL edition. It is not a replacement for the source PDF.

## Current decisions

- Use A4 for the working edition and keep one stable reading column. The original PDF's generous outer area is not recreated as a marginal-text column because the requested adaptation moves each margin note beside its owning paragraph.
- Chapter openers, headings, running heads, folios, figures, captions, tables, code blocks, equations, notes, and problems are controlled by the shared Typst template.
- Display equations use a three-column layout `(flexible, formula, flexible)` with the equation number in a right-aligned `auto` column. This centers the formula independently of the number.
- Original blue margin references are rendered as parenthetical links at the end of the paragraph that owns them. The visible label keeps the original kind and number, and a notebook title or appendix descriptor is joined with `: `.
- If PDF extraction splits a note into a lead label and a title-only link, or places the lead in an otherwise empty following paragraph, the converter joins those fragments before rendering. The source manifest must retain the original target for every fragment.
- The original PDF remains the authority for notes that are absent from Markdown. Such notes are added through a small reviewed override, with their source page and target anchor recorded.
- Figures use official local vector PDFs whenever the mapping is unambiguous. Raster figures are retained at their original bytes when no safe vector match exists; upscaling a raster alone is not treated as a clarity improvement.
- Figure 1.1 is a reviewed exception to the extracted-raster fallback: the source PDF contains the drawing as vector paths, so the builder crops that region into `fig_1_1.pdf` and uses the vector crop in the generated edition.
- A figure and its caption stay together. Tables retain source column order and semantic text; wide tables may use a controlled smaller size or a deliberate landscape/fallback component after visual review.

## Representative acceptance pages

- Original PDF page 32 demonstrates the Appendix A margin note beside equation 2.3.
- Original PDF page 35 demonstrates a Notebook 2.1 note and a Problems 2.1–2.2 note in the outer margin.
- Original PDF page 33 demonstrates centered display mathematics with a right-edge equation tag around equation 2.5.

Every future layout change should recheck these pages and at least one later chapter with multiple adjacent notes.
