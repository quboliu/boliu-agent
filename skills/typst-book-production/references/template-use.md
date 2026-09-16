# Using the runnable templates

Copy the relevant entry file plus `core.typ` and `covers.typ` from
`templates/` to the book's `book/` directory. Then create a `main.typ` that
imports the chosen entry and calls the cover macros before the body.

Install or vendor the declared fonts before compiling. The templates require
`Libertinus Serif`, `Noto Serif SC`, `DejaVu Sans`, and `DejaVu Sans Mono` by
default. Keep any vendored, redistribution-permitted fonts in `assets/fonts/`
and compile with an explicit font path, for example:

```sh
typst compile --root . --font-path assets/fonts book/main.typ dist/book.pdf
```

Treat an unknown-font warning or fallback in the PDF as a failed build, not a
cosmetic warning. Record the actual font files and their licences in the book
contract.

```typst
#import "template.typ": *

#source-cover(
  "Book title",
  "Original author",
  "Original source: publisher, edition, year",
  original-cover: "assets/source-cover.png",
)
#boliu-cover(
  "Book title",
  "Original author",
  "Original source: publisher, edition, year",
  "Chinese edition",
  artwork: "assets/historical-line-art.svg",
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

- `monolingual-zh.typ` selects Noto Serif SC and Chinese language behavior.
- `monolingual-en.typ` selects Libertinus Serif and English language behavior.
- `bilingual.typ` adds `dual`, `dual-heading`, and `dual-caption`; source text
  precedes Chinese and both remain full semantic elements.

Do not change the core values in individual chapter files. For a justified
project-level exception, copy the affected named token into the project template,
record the old/new values and visual comparison in the contract, then test every
example page class specified in the design system.
