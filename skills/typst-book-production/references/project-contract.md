# Project contract

Create one compact, versioned `book.toml` inside each Typst edition before
substantive conversion or layout work. Paths are relative to that edition
directory unless explicitly prefixed with `../`. All editions point to the
single sibling Markdown intermediate; none owns a second source tree.

```toml
edition = "bilingual" # monolingual-zh | monolingual-en | bilingual
project_name = "book-slug-typst-dual"
book_slug = "book-slug"
source_language = "en"
primary_language = "en"
secondary_language = "zh"
raw_authority = "../book-slug-raw/"
markdown_authority = "../book-slug-markdown/"
markdown_chapters = "../book-slug-markdown/chapters/"
markdown_images = "../book-slug-markdown/images/"
source_map = "source-map.json"
local_skill = "../.agents/skills/book-slug/"
publisher_profile = "boliu-b5-2"
paragraph_style = "flush-left-spaced"
binding = "left"
duplex = true
flip_edge = "long"
pdf_page_order = "reading"
recto_basis = "physical-pdf-page"
print_scale = "100%"
typst_entry = "book/main.typ"
template = "book/template.typ"
output_pdf = "output/build/book-slug-typst-dual.pdf"
build_command = "typst compile --root . --font-path assets/fonts book/main.typ output/build/book-slug-typst-dual.pdf"

[status]
structure = "complete"
content = "in-progress"
translation = "in-progress"
build = "not-run"
visual_proof = "not-run"
rights = "unresolved"
physical_proof = "not-run"
release = "blocked"
```

Also record:

- independent structural, content, translation, build, visual-proof, rights,
  physical-proof, and release states; directory existence or a validator pass
  must never imply content completion or release readiness;

- raw authority, source version/checksum, and the rule that raw material is
  immutable;
- Markdown authority, chapter/image paths, source-to-Markdown extraction
  provenance, and the rule that normalized corrections happen only in the
  Markdown layer;
- canonical book slug, project name, source language, selected `zh` / `en` /
  `dual` suffix, and path to the book-local skill;
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
- deterministic build environment and required quality gates;
- binding method/thickness, gutter allowance, duplex print settings, and
  digital versus physical proof status; see [duplex printing](duplex-printing.md).

The contract is an edition boundary. Put reusable production rules in this
general skill and book-specific behavior in
`.agents/skills/<book-skill-slug>/`; do not hide a second source authority or a
noncanonical directory behind a contract exception.
