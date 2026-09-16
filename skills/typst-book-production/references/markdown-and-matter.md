# Markdown conversion and complete-book structure

The retired pphc-typst-book supplied useful patterns for chapter conversion,
HTML-export captions, part pages, hanging contents, front matter and attributed
quotations. These are adapted to the existing house templates; its dark/gold
covers, code chips, table striping, fixed-right folios and root-only template
layout are not inherited.

## Structural components

All edition entries export these from `matter.typ`:

- `frontchapter(title, body, running: title)`: an unnumbered recto opener;
  numbering is disabled within its body only. Use for preface or an unnumbered
  appendix. Numbered/lettered appendices need an explicit project policy.
- `part-page(number, title, blurb: [])`: a white recto divider with restrained
  accent rule. It is a semantic unnumbered level-one heading, appears in contents,
  and does not replace the next chapter opener. Chapter counters reset explicitly.
- `toc-page(title: [Contents], depth: 3)`: clickable hanging entries with
  wrapped-title alignment; continuation pages use mirrored outside folios.
- `copyright-page(body)`: source/licence/edition credits without furniture.
- `title-page(title, author, edition: [])`: optional additional title page,
  never a replacement for either mandatory cover.
- `quoteblock(body, attribution: none)` and `qattr(body)`: indented quotation
  and right-aligned attribution, without a decorative panel.

Example after the two mandatory cover calls:

```typst
#copyright-page[Source edition, original author, reproduction and font credits.]
#frontchapter([Preface])[
  == Purpose
  This section is intentionally unnumbered.
]
#toc-page(title: [Contents], depth: 3)
#part-page([PART I], [Foundations])
#include "chapters/001.typ"
```

Keep the continuous folio policy unless the project explicitly chooses roman
preliminaries; physical page parity never depends on displayed counters.
The structure fixture tests multi-page contents, hyperlinks and right-page starts.

## Converter

Install in the project build environment: `markdown-it-py==4.2.0`,
`mdit-py-plugins==0.6.1`, and PyMuPDF (record its exact installed version).
The converter uses a Markdown token tree, rather than global regex rewriting.

```sh
python3 /path/to/skill/scripts/md2typ.py \
  --project /path/to/book-slug-typst-zh \
  --source-dir /path/to/book-slug-typst-zh/source \
  preface.md chapters/01.md chapters/02.md \
  --front preface.md
```

Supply chapter paths in explicit reading order, relative to `source/`; each
contains one leading H1. `--front` lists unnumbered inputs. Outputs are
`book/chapters/001.typ`, etc., plus `source/source-map.json`. Copy all shared
template modules and rename the selected entry to `book/template.typ`; create
`book/main.typ` with `#show: book`, covers, matter and ordered includes.
The converter does not assemble a title/author/cover without project metadata.

Supported: paragraphs, semantic headings, emphasis/strong, inline/fenced/indented
code, nested lists and start numbers, links, quotations with a final dash
attribution, pipe tables and alignment, local images, explicit HTML-export
figure/table/listing captions, and opt-in verified Typst math.
Recognized plain Chinese chapter numbers and numeric section prefixes are
removed from display only when consistent with the declared chapter order.
Image assets are copied unchanged under lowercase content-derived filenames;
their hashes/dimensions enter the manifest. The initial image width is 80% of
the measure, NOT a 96dpi inference; tune at print size and record effective ppi.
Table fractions initially are equal; tune widths for the actual content.

Relative chapter/heading links become native label links. Anchors use lowercase
Unicode heading text with punctuation removed and spaces replaced by hyphens.
Duplicate headings, missing targets and unsupported URI schemes are rejected;
adapt alternative website anchor conventions explicitly. External HTTP(S) and
mailto targets remain clickable.

Dollar math defaults to rejection, because Markdown commonly contains LaTeX.
Use `--math typst` only after verifying/converting expressions into Typst syntax.
This option never translates LaTeX. Unknown HTML, footnotes, extensions and
unsupported constructs require a documented source adapter; they must not be
silently dropped. Run a representative-source trial before converting a corpus.
The converter preserves supplied content; bilingual pairing/translation remains
a subsequent explicit semantic step, not guessed from alternating paragraphs.

Outputs are derived and overwritten on regeneration. Do not manually patch them;
change the converter/adapter or recorded source corrections. Preserve custom
manifest exclusions/audit data separately and merge them deliberately after
regeneration. Render validation precedes chapter writes, but asset I/O can still
fail during output: fix the source/asset issue and rerun before using the tree.

## Tests and proof

```sh
BOLIU_FONT_PATH=/path/to/fonts python3 scripts/test_md2typ.py
python3 scripts/check-templates.py --font-path /path/to/fonts --output /tmp/book-proof
```

Tests include semantic preservation, unresolved-link rejection, unsupported
HTML/math rejection, asset/caption mapping, and compilation of generated chapters
with native links, quotations, code, tables and math. Review actual-source
coverage and use the real-project validator before publication.
