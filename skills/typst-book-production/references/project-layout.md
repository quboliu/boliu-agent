# Canonical Typst project layout

Create each new edition as a standalone, reproducible project. Its root name is
exactly one of:

```text
<book-slug>-typst-zh
<book-slug>-typst-en
<book-slug>-typst-dual
```

`<book-slug>` contains only lowercase ASCII letters, digits, and hyphens. Use a
stable bibliographic or user-approved English slug, such as
`designing-data-intensive-applications`; do not put edition, translator,
publisher, date, or `typst` into the slug itself. If a title cannot be reduced
to an unambiguous stable slug, ask the user to choose it before creating the
tree. Parallel editions of one work share the same slug and differ only in the
final suffix.

```text
<book-slug>-typst-dual/
├── assets/
│   ├── covers/
│   │   ├── boliu/
│   │   └── source/
│   ├── figures/
│   └── fonts/
├── book/
│   ├── chapters/
│   ├── covers.typ
│   ├── core.typ
│   ├── main.typ
│   ├── matter.typ
│   └── template.typ
├── output/
│   ├── audit/
│   ├── build/
│   └── preview/
├── source/
├── editorial/               # optional maintained annotations and review ledger
├── book.toml
└── readme.md
```

The `readme.md` is optional unless the surrounding repository requires it. The
editorial directory is needed only for requested content audits. Other top-level roles are fixed.

## Role boundaries

- `source/` holds the declared content authority, source manifest, checksums,
  and source-to-output mapping. Treat its authoritative content as immutable
  unless the contract permits recorded corrections.
- `assets/covers/source/` holds the original cover in its preserved bytes;
  `assets/covers/boliu/` holds the credited historical line drawing for the
  publisher cover; `assets/figures/` holds supplied or traceable figures; and
  `assets/fonts/` holds only font files the project may legally redistribute.
- `book/` is the only maintained Typst source tree. `main.typ` is the single
  compilation entry point. `template.typ` is the renamed copied edition
  entry, while `core.typ`, `covers.typ`, and `matter.typ` remain the shared project modules.
  `chapters/` holds semantic content, not build outputs or source exports.
- `output/build/` holds reproducible release PDFs, `output/preview/` holds
  disposable page or chapter previews, and `output/audit/` holds QA manifests,
  checks, and reviewed raster output. No `output/` artifact is the sole source
  of truth.
- `book.toml` declares the edition, authoritative source, paths, source-cover
  and publisher-cover provenance, font licences, build command, profile
  version, and every exception. It is the mapping layer for a legacy tree.

## Required initialization

Keep accepted annotations, evidence/rebuttal ledgers and requested reviewer
sessions in `editorial/content-audit/`. These are maintained inputs; generated
reports remain in `output/audit/`.

1. Select the edition and stable slug before creating the directory.
2. Copy `core.typ`, `covers.typ`, `matter.typ`, and the matching edition entry from the skill
   templates into `book/`; rename that entry to `template.typ`.
3. Make `book/main.typ` import `template.typ`, apply `#show: book`, render the two cover pages, then
   include chapters from `book/chapters/`.
4. Place supplied sources and assets in their designated roots without silently
   rewriting them. Create the `output/` subdirectories before the first build.
5. Fill `book.toml`, compile from the root with `--root .`, and record the
   output checksum and visual-QA evidence in `output/audit/`.

Do not create edition-specific source directories under one shared root unless
the user expressly requests a multi-edition monorepo. In that case, each
edition still needs the same internal role boundaries and a separate contract.

## Legacy projects

Do not rename or move a functioning existing book merely to satisfy this
convention. First record the current paths and desired canonical equivalents in
`book.toml`; migrate only with the user's authorization and preserve a complete
source map. New material added to a legacy project should follow the closest
safe equivalent of these roles.
