---
name: pdf-dual-typst
description: Create or maintain faithful English-Chinese bilingual PDFs from source PDFs with Typst, preserving source structure, visual content, and immediate bilingual pairing.
---

# PDF dual-language Typst

made by quboliu

Use this skill when a task converts a source PDF into a faithful English-Chinese
bilingual PDF with Typst. It applies to books, papers, course notes, slides,
manuals, and other paginated PDF materials. Do not use it for ordinary Markdown
translation that has no PDF deliverable, or when the source PDF is not the
content authority.

## Authority and scope

- Read the target repository's instructions before work. They decide source
  locations, output paths, terminology, licensing, permitted tools, and any
  stricter visual or translation requirements.
- Treat the source PDF (or its declared byte-identical local snapshot) as the
  authority. Do not silently omit, summarize, reorder, or invent text, visual
  elements, page labels, citations, links, formulas, code, tables, or figures.
- Keep the original PDF immutable. Write a separate Typst source and a separate
  bilingual PDF; never overwrite the original.
- Preserve the source's reading order, hierarchy, numbering, and page-level
  visual intent. A bilingual edition adds translation; it is not a redesign.

## Bilingual structure

- Put English first and its Chinese translation immediately after the same
  complete semantic unit. Do not cut a paragraph, list item, quotation, table,
  code block, formula, figure, or footnote in half to satisfy a size target.
- Choose bilingual alternation at the semantic-group level, not mechanically
  after every line. For a cohesive multiple-choice list, scoring rubric,
  parameter list, or similarly dense option group, render the complete English
  list followed by the complete Chinese list. Preserve labels (A–H, numbers,
  symbols) and ordering so the two groups remain directly comparable while
  avoiding distracting language switching between every item.
- Treat an ordinary English paragraph and its Chinese translation as one
  pagination unit whenever they fit on a page. Keep the pair together with a
  small, explicit inter-language gap; do not let English end at the bottom of
  one page and force its Chinese translation to begin alone on the next. For a
  pair too large to fit, allow a controlled break and verify the result.
- Pair every title and heading. Use a single semantic heading with English on
  one line and Chinese on the next when the template supports it.
- Determine heading pairs from source order, heading level, and translation
  adjacency—not from the presence of Han characters alone. A translated title
  may remain entirely Latin (for example, `VI Lab 3A–3C`, `I MapReduce`, or a
  proper name); it is still a bilingual pair when it is the immediately
  following same-level heading.
- In Typst, make the English/Chinese break explicit with `#linebreak()` (a
  source newline inside a content block is usually only whitespace). Render
  the pair as one heading block so its `above`/`below` spacing is applied once.
  Do not render the two language headings as independent blocks, which doubles
  their spacing and can leave the following paragraph visually touching the
  heading.
- Translate prose, captions, labels, notes, table cells, footnotes, and visible
  annotations faithfully. Preserve code, identifiers, formulas, command lines,
  URLs, proper product names, and technical notation unless the project has a
  documented translation policy for them.
- Treat code blocks, formulas, command transcripts, and other semantically
  invariant blocks as single-copy units by default. Do not duplicate an entire
  program merely to show a Chinese version when the program itself has nothing
  meaningful to translate. Translate the surrounding explanation instead; if
  comments inside code genuinely require translation, keep one code block and
  change only the comments under an explicit repository policy.
- When an input Markdown contains adjacent English/Chinese copies of the same
  code block (including copies that differ only in indentation or translated
  comments), normalize the three deliverables to one code block so Markdown,
  Typst, and PDF remain semantically equivalent and visually uncluttered.
- Before removing a duplicate code block, preserve the best indentation and
  line structure from the available copies. PDF-to-Markdown conversion often
  left-aligns every line; do not let deduplication turn a correctly indented
  program into a flat listing. If the authoritative PDF is the only reliable
  source, recover indentation from its rendered/text geometry or apply a
  syntax-aware formatter and record that decision.
- Pass leading spaces through the Typst `raw` payload unchanged. A newline in a
  source string is not a substitute for indentation, and a formatter must not
  trim common leading whitespace from nested code lines. Use a monospaced font
  and a breakable, shaded code block that keeps the recovered nesting visible.
- For slide-like pages, retain the original slide page followed immediately by
  a Chinese-localized counterpart only when that is the repository's declared
  format. Otherwise use adjacent bilingual text and figures in Typst.

## Layout and assets

- Inspect the source PDF's page size, margins, columns, headings, tables,
  captions, figures, code, and footnotes before designing the Typst document.
- Preserve critical visual relationships and table geometry. Do not simulate
  layout with ad-hoc manual spacing when a reusable Typst macro or grid rule can
  express it; use page-specific adjustments only for genuinely exceptional
  source elements.
- Give headings, body pairs, code blocks, tables, figures, and captions their
  own reusable spacing rules. Avoid stacking arbitrary `#v` calls, which makes
  spacing depend on which language or block happened to precede it.
- Use fonts that support both Latin and required CJK glyphs, and verify they are
  available to the compiler. Choose body sizes, leading, and page geometry from
  the source or repository template rather than hard-coding a book-specific
  default.
- Extract or render figures, charts, and diagrams from the authoritative PDF.
  Do not replace source visuals with guessed, hand-drawn, or AI-invented
  imagery unless the target repository explicitly authorizes that workflow.
- Keep figure/table captions with their visual object. Preserve table rows,
  columns, headers, and values; when one bilingual table would be unreadable,
  use adjacent English and Chinese copies with identical structure.
- Keep a heading with a reasonable amount of following body text; avoid a
  heading stranded at the bottom of a page. Keep code blocks, tables, and
  captions intact where possible, and flag pages ending with a lone heading,
  one option, or an isolated caption for visual review.
- PDF-to-Markdown extraction may turn repeated page headers/footers into body
  paragraphs. Preserve their source page identity (especially page labels),
  but move or compress redundant title/institution text into a restrained
  header marker so it does not crowd the cover or repeat above every section.

### Heading-spacing failure mode

The common failure is a heading such as `VI Lab 3A–3C` appearing almost
attached to the first paragraph below it. The usual cause is that the English
and Chinese headings contain no Han characters, so a CJK-based pairing test
misses them; each heading is then emitted separately, and a source newline is
mistaken for a visual line break. The fix is to pair adjacent same-level
headings structurally, emit one block with explicit `#linebreak()`, and set a
source-informed bottom gap (normally at least 10pt after the final heading
line, adjusted to match the original PDF's geometry).

## Typst source and export

1. Build reusable helpers for paired headings, prose, captions, notes, and
   footnotes before introducing repeated local formatting.
2. Record source provenance in the form required by the repository. Keep it out
   of the official source text unless the repository requires a visible mirror
   notice.
3. Compile with `typst compile`, including any required font paths.
4. Preserve clickable external links and meaningful internal references where
   the source exposes them.

## Verification

- Compare the Typst source and exported PDF against the authoritative source
  page by page. Verify all headings, paragraphs, lists, code, formulas, tables,
  figures, captions, footnotes, citations, and links are covered.
- Check that invariant code/formula blocks occur once per semantic occurrence;
  flag adjacent duplicate fenced blocks before declaring the bilingual copies
  equivalent. Confirm that any translated code comments follow the repository's
  explicit policy rather than introducing a second full code listing.
- For representative code blocks, verify indentation in the exported PDF, not
  only in the Typst source: inspect successive line x-coordinates (or raster
  output) and confirm nested statements are visibly offset while top-level
  statements align. Treat a flat block where the source shows nesting as a
  regression even when compilation succeeds.
- Add a coordinate-based spacing check for representative dense pages: extract
  PDF text blocks and measure the vertical gap from each bilingual heading
  block to the first following body block. Flag gaps below the chosen minimum
  (10pt is a useful default) and visually inspect every flagged page. Include
  headings whose English and Chinese strings are both Latin-only in this check.
- Check page endings for orphaned structural units: a heading without enough
  following text, a single list item separated from its list, a code fragment,
  or a caption without its figure. These are layout regressions even when the
  PDF compiles and all source strings are present.
- Rasterize representative pages and visually inspect page breaks, bilingual
  adjacency, CJK glyph coverage, overflows, widows/orphans, figure/table
  placement, code wrapping, and page bottoms. Inspect every page for slides or
  visually dense material.
- Treat a fenced block whose first line starts with `#` as code when it has
  multiple non-empty lines (Python/Ray comments are not Markdown headings).
  A fenced heading conversion should be limited to a genuine one-line
  structural heading; verify representative comment-led programs after export.
- Check the exported PDF opens, has the expected page sequence, embeds or finds
  the selected fonts, and contains no missing-image placeholders or clipped
  content.
- Report the Typst source path, exported PDF path, page count, source identity,
  and any verified limitations. Do not claim completion from a successful
  compile alone.
