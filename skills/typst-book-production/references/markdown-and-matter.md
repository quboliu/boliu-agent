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

## Project-owned conversion

Do not route every book through one universal script. Inspect the supplied
source dialect, chapter organization and exceptional structures, then create or
adapt a converter in
`<book-name>/.agents/skills/<book-skill-slug>/scripts/` with book-local tests.
Document exact dependencies, explicit input order, regeneration commands,
formula rules, known anomalies, and learned pitfalls in that local skill or its
references. Reuse the implementation on subsequent updates; model flexibility
is not permission to improvise a new conversion each session. Existing
maintained Typst does not require a conversion script.

Prefer a structural parser with an explicit semantic mapping. Inventory dialect
extensions before parsing: unsupported footnotes, task lists or custom HTML may
become ordinary text rather than unknown tokens. Detect them deliberately;
implement their semantics or stop with a source location and adaptation need.
Never use blind global replacements across prose, code and math.

### Invariants to implement

- Preserve everything under `<book-name>-raw/` byte-for-byte. Produce
  source-language intermediate chapters only in
  `<book-name>-markdown/chapters/` and highest-quality extracted images only
  in `<book-name>-markdown/images/`. Declare reading order and front matter
  explicitly. Each edition maps Markdown elements to generated Typst in its
  root `source-map.json` and records `source_sha256` from the exact Markdown
  bytes converted.
- Preserve complete heading numbers and hierarchy. Do not strip a source
  prefix unless it agrees with the complete generated counter, not merely the
  chapter number. Handle excerpts, jumps, duplicates and appendices explicitly.
- Render inline semantics everywhere, including quotations, attribution,
  captions, notes and table cells. Extracting a dash-prefixed attribution must
  not flatten emphasis, code or links into literal Markdown.
- Preserve code whitespace and punctuation; syntax examples inside code must
  not trigger prose-footnote or HTML conversion. Determine math syntax first:
  Markdown dollar delimiters do not mean the contents are valid Typst math.
- Preserve internal link destinations with stable, collision-checked labels;
  resolve source-specific anchors deliberately. Fail on missing destinations.
  Preserve external links and footnote/reference relationships.
- Recover the best available image once into the Markdown `images/` tree.
  Reproducibly copy edition figure inputs from there without quality loss;
  record hashes, dimensions and provenance, and use lowercase collision-safe
  paths. Reject missing/out-of-root inputs. Choose placed size for print
  readability, not from assumed screen DPI. Tables need content-aware widths.
- Pair bilingual content by semantic element, never by alternating lines or
  guessed paragraph counts. Preserve invariant code/formulas single-copy as
  declared in the book contract; conversion alone does not produce translation.
- Validate all inputs and planned outputs before replacing generated files.
  Stage multi-file output and publish only after success, so an asset failure
  cannot leave a mixed old/new edition. Preserve audit metadata and exclusions.
  Fix derived text through the converter or recorded errata, not hand patches.

### Required project acceptance cases

Implement tests for the constructs actually present, including their failure
paths. The following past failures are reusable acceptance cases, not an
exhaustive list or a bundled converter's claimed feature set:

| Input or event | Required outcome |
| --- | --- |
| `Text[^1]` plus definition; undefined or unused footnotes | Faithful linked notes, or explicit rejection; never silent text fallback/drop |
| The same footnote syntax inside inline/fenced code | Exact literal code |
| First section `1.7`, repeated `1.1`, or skipped hierarchy | Preserve intentional source numbering or reject; never silently renumber |
| `> -- *Author* [work](https://example.org)` | Styled attribution and clickable link, without printed Markdown syntax |
| Missing internal anchor, duplicate titles, nested lists, HTML captions | Explicit project-specific mappings and failures, with no lost structure |
| LaTeX math and existing equation tags | Verified translation and preserved tags, or explicit rejection |
| Source changes after conversion | Hash check fails until regeneration; output must reflect changed content |
| Asset failure midway through conversion | Previous accepted output remains coherent; failed staging is not published |

Run a small end-to-end project: immutable raw subset → source-language Markdown
chapters/images → generated Typst → both covers and all copied template modules
→ compiled PDF → `validate_workspace.py` and `validate_book.py`.
Check extracted content, links, footnotes, numbering and assets against the
source, then inspect rendered pages. Add short and overheight bilingual pairs
when applicable. General template tests cannot replace these project tests.
