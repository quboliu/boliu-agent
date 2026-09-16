# Using the runnable templates

Copy the relevant entry file plus `core.typ`, `covers.typ`, and `matter.typ` from
`templates/` to the book's `book/` directory. Then create a `main.typ` that
imports the chosen entry and calls the cover macros before the body.

Install or vendor the declared fonts before compiling. The templates require
`Libertinus Serif`, `Noto Serif SC`, `DejaVu Sans`, and `DejaVu Sans Mono` by
default. Keep any vendored, redistribution-permitted fonts in `assets/fonts/`
and compile with an explicit font path, for example:

```sh
typst compile --root . --font-path assets/fonts book/main.typ output/build/book.pdf
```

Treat an unknown-font warning or fallback in the PDF as a failed build, not a
cosmetic warning. Record the actual font files and their licences in the book
contract.

```typst
#import "template.typ": *
#show: book

#source-cover(
  "Book title",
  "Original author",
  "Original source: publisher, edition, year",
  original-cover: "/assets/covers/source/cover.png",
)
#boliu-cover(
  "Book title",
  "Original author",
  "Original source: publisher, edition, year",
  "Chinese edition",
  artwork: "/assets/covers/boliu/historical-line-art.svg",
  artwork-credit: "Subject, artist/source, public-domain or licence basis",
)

#chapter("1", "Chapter title")
```

For an original cover, preserve the supplied file unchanged, record its SHA-256
and rights in the contract, and pass its stable path to `original-cover`. Leave
`original-cover` unset only if no original cover exists; this renders the
approved text-only fallback. `boliu-cover` deliberately renders a prominent
`NOT FOR RELEASE` placeholder when `artwork` is missing. Replace it only with
the documented historical line drawing required by the design system.

The entry files are intentionally thin:

They also export the structural components in
[Markdown conversion and book structure](markdown-and-matter.md). These add
front matter after the mandatory two covers and keep physical duplex parity.

- `monolingual-zh.typ` selects Noto Serif SC and Chinese language behavior.
- `monolingual-en.typ` selects Libertinus Serif and English language behavior.
- `bilingual.typ` adds `dual`, `dual-heading`, `dual-caption`, `dual-note`,
  and `dual-footnote`; source text
  precedes Chinese and both remain full semantic elements.

`dual` measures both streams at the current column width and keeps the pair
unbroken if it fits a full live page (208mm in the baseline). Longer pairs retain
normal paragraph pagination. For a changed trim/margin profile or constrained
container, set its `pair-height:` to the actual available full-region height;
do not use the remaining space on the current page as that threshold. Proof
footnote-heavy pairs separately because note reservations reduce available space.
The measurement follows Typst's [measure/layout API](https://typst.app/docs/reference/layout/measure/).

Do not change the core values in individual chapter files. For a justified
project-level exception, copy the affected named token into the project template,
record the old/new values and visual comparison in the contract, then test every
example page class specified in the design system.

The edition file is renamed to `book/template.typ`; its exported `book`
function is applied in main with `#show: book`. Use project-root absolute asset
paths beginning with `/` under `--root .` to avoid resolution relative to a
macro's module. Changes to constants belong in the copied `book/core.typ`;
declaring a same-named constant in a chapter does not override an imported
function's lexical scope.

`book-table(columns, header: ([A], [B]), ..cells)` repeats the supplied header
and inserts its separating rule. Legacy positional calls still work but have
no inferred header; update them explicitly. For long tables, use native table
and figure mechanics with the same style and test continuation pages.
`display-equation[$ ... $]` is not the calling convention: pass math content
as `#display-equation($ a^2 + b^2 = c^2 $) <eq-example>`, then use
`@eq-example`. Use `number: "(3.7)"` to preserve a supplied source number.

Run `python3 scripts/check-templates.py --font-path /path/to/fonts --output
/path/to/qa-output` from this skill directory after a shared-template change.
It requires Typst and PyMuPDF, compiles the three edition fixtures and stress
fixture, checks actual trim, cover order, chapter numbers and blank furniture,
and renders sample pages for human review. It does not certify visual quality.
