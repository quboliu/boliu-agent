# Chinese technical-book typography

These are starting points, not immutable laws. Change them only with a documented reason and representative-page review.

## Page and grid

- Select the trim from the project brief and treat it as a hard constraint. A4 is valid when explicitly required; use exact `paper: "a4"` and tune wide SQL/diagrams to the A4 grid instead of changing the paper size. Use a consistent inner/outer margin pair and reserve enough inner gutter for duplex reading.
- Use a stable baseline rhythm. Body text should be comfortable at normal zoom and remain legible when printed; do not solve density by reducing the body below roughly 10pt without a specific reason.
- Keep chapter openings, running heads, folios, and front matter on deliberate page styles. Avoid accidental blank pages except where a print convention requires them.
- A chapter opener should establish a clear title hierarchy and have enough following material to feel intentional. Keep the title with a short lead-in, figure, or first section when possible; do not strand a section heading at the bottom of a page.
- Running heads are contextual furniture, not a repeated book-title banner. Derive the left label from the latest semantic chapter heading and shorten it only at the template layer. Suppress it on the cover and chapter opener; use a distinct `CONTENTS`/`目录` style for contents pages and keep folios in one predictable position.

## Font policy

- Body: a readable CJK serif family, normally Noto Serif CJK SC Regular/Bold.
- Display and interface elements: a CJK sans family, normally Noto Sans CJK SC Regular/Bold.
- Code: a monospace CJK-capable face, normally Noto Sans Mono CJK SC, with a Latin fallback only when verified.
- Pin font families through the explicit Typst font-path option and check compiler output for unknown-font diagnostics. A PDF that renders Chinese with a fallback is a failed build even if it technically compiles.
- Keep the font licence beside vendored font files. Do not bundle a font whose redistribution terms are unclear.

## Hierarchy and rhythm

- Establish a visible three-level hierarchy: chapter, section, and sub-section. Use semantic Typst headings and counters so section numbers are queryable and appear consistently in the outline, running context, and page. Numbering should communicate structure, not decorate every paragraph.
- Choose one paragraph convention for the whole book and apply it consistently. For technical “block” prose, prefer `first-line-indent: 0pt` and use a measured paragraph spacing (roughly `0.8–1.1em`) to create the grouping; if a traditional indented style is chosen, do not also add a large paragraph gap. In either style, headings, the first paragraph after a heading or display object, lists, notes, captions, and code should use their own block rhythm instead of inheriting a prose indent.
- Diagnose vertical rhythm as separate systems: body line leading, paragraph separation, list-item spacing, and outline-entry spacing. Change and raster-check each at representative reading size; a plausible numeric value does not guarantee an open page because font metrics and block-collapsing behavior affect the result.
- After changing a global paragraph rule, inventory nested `set par` and `show` overrides in quotes, notes, table cells, captions, and code. Keep prose-bearing components in the same rhythm family while allowing code and compact metadata to remain intentionally tighter; otherwise the book will alternate between comfortable and unexpectedly dense regions.
- Optimize a table of contents for scanning, not for fitting an arbitrary page count. Give entries an explicit readable font, wrapped-line leading, and minimum row separation; allow the outline to gain pages rather than shrinking it. In Typst, adjacent blocks' `above`/`below` spacing can collapse, so use vertical `inset` or an explicit row structure when the design requires a guaranteed minimum entry height. Inspect the continuation page, longest titles, leaders, page numbers, and link targets after pagination settles.
- Keep emphasis sparse. Use bold for terms, colour or a note component for genuinely important guidance, and avoid a rainbow of ad-hoc styles.
- Chinese punctuation remains full-width in prose; code and SQL retain their source punctuation and spacing.

## Figures, tables, and code

- Every explanatory figure receives a stable number and a concise caption. Keep the image and caption in one figure container and, when possible, keep a short lead-in sentence on the same page. If the whole figure cannot fit, move the container rather than leaving a caption or an orphaned label behind.
- Preserve the source diagram's aspect ratio. Use contain-style fitting and an explicit maximum width; choose narrower widths for tall/portrait assets and wider widths for very wide diagrams instead of forcing every image to 100% of the text column. Review the width bands on rasterized pages. For reliable centering, give the figure wrapper the full reading-column width and align the whole `figure`; aligning only an image inside a shrink-wrapped figure may leave the figure itself flush left.
- Tables need readable cell padding, repeated header treatment where relevant, and a fallback for wide content. Prefer a short table or a deliberate landscape/wide treatment over tiny text; keep the table caption attached to the table.
- Code is a reading object: label its language (including a stable fallback such as `text`), use a tinted block with enough inset and a consistent reading-column width, preserve whitespace, and avoid splitting a small example across pages. Long code may continue only at line boundaries and should not acquire a different ad-hoc style on later pages.

## Colour and contrast

Use a small token set: ink, muted ink, paper, navy, accent, code background, quote background, and rule. Check that the document remains understandable in grayscale and that coloured text is not the only carrier of meaning.
