# Project contract

Create a compact, versioned contract in the book repository before substantive
conversion or layout work. A `book.toml`, `book.yaml`, or decision-log section
is acceptable if it records these decisions unambiguously.

```toml
edition = "bilingual" # monolingual-zh | monolingual-en | bilingual
primary_language = "en"
secondary_language = "zh"
source_authority = "source-markdown/"
typst_entry = "book/main.typ"
template = "book/template.typ"
output_pdf = "dist/book.pdf"
build_command = "typst compile --root . --font-path assets/fonts book/main.typ dist/book.pdf"
```

Also record:

- content authority, source version/checksum, and whether source corrections are
  allowed;
- source-to-output map and generated-file policy;
- chapter ordering, heading hierarchy, and numbering policy;
- page size, margins, font families, font licences, code face, and fallback
  policy;
- semantic macros for headings, prose, notes, footnotes, figures, captions,
  tables, code, links, and running furniture;
- bilingual pairing order and special-element policy when applicable;
- terminology baseline, source anomalies, approved errata, and unresolved
  decisions;
- deterministic build environment and required quality gates.

The contract is a project boundary. Do not put book-specific type sizes,
translated terms, paths, or exceptions into the general production skill.
