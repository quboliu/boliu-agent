# Project contract

Create a compact, versioned contract in the book repository before substantive
conversion or layout work. New projects use `book.toml`; legacy projects may
map an existing manifest in their documented layout exception.

```toml
edition = "bilingual" # monolingual-zh | monolingual-en | bilingual
project_name = "book-slug-typst-dual"
primary_language = "en"
secondary_language = "zh"
source_authority = "source/"
publisher_profile = "boliu-b5-2"
paragraph_style = "flush-left-spaced"
typst_entry = "book/main.typ"
template = "book/template.typ"
output_pdf = "output/build/book-slug-typst-dual.pdf"
build_command = "typst compile --root . --font-path assets/fonts book/main.typ output/build/book-slug-typst-dual.pdf"
```

Also record:

- content authority, source version/checksum, and whether source corrections are
  allowed;
- canonical project name, the selected `zh` / `en` / `dual` suffix, and any
  documented exception from the standard project tree;
- source-to-output map and generated-file policy;
- chapter ordering, heading hierarchy, and numbering policy;
- page size, margins, font families, font licences, code face, fallback policy,
  the 伯流出版社 profile version, and every approved token override;
- source-cover status (`original` or `fallback`), source URL or repository path,
  checksum, pixel dimensions, licence/permission, and any applied crop; and the
  second-page 伯流出版社-cover image's subject, source, rights, and relevance to
  the book;
- semantic macros for headings, prose, notes, footnotes, figures, captions,
  tables, code, links, and running furniture;
- bilingual pairing order and special-element policy when applicable;
- terminology baseline, source anomalies, approved errata, and unresolved
  decisions;
- deterministic build environment and required quality gates.

The contract is a project boundary. Do not put book-specific type sizes,
translated terms, paths, or exceptions into the general production skill.
