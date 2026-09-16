# Canonical book workspace layout

Treat the directory named `<book-slug>` as the root workspace for the whole
book, not as one edition project. `<book-slug>` is a stable English title slug
containing only lowercase ASCII letters, digits, and single hyphens. It must
not contain an edition, translator, publisher, date, `markdown`, or `typst`.
Ask the user to choose the slug when no unambiguous title slug exists.

Every new workspace follows one of these two exact edition matrices. A Chinese
source has one Chinese Typst edition:

```text
<book-slug>/
├── .agents/
│   └── skills/
│       └── <book-slug>/
│           ├── SKILL.md
│           ├── references/          # only when this book needs them
│           └── scripts/             # only when this book needs them
├── <book-slug>-raw/
├── <book-slug>-markdown/
│   ├── chapters/
│   └── images/
└── <book-slug>-typst-zh/
```

An English source has English, bilingual English-Chinese, and Chinese Typst
editions:

```text
<book-slug>/
├── .agents/skills/<book-slug>/
├── <book-slug>-raw/
├── <book-slug>-markdown/
│   ├── chapters/
│   └── images/
├── <book-slug>-typst-en/
├── <book-slug>-typst-dual/
└── <book-slug>-typst-zh/
```

Do not substitute `source`, `sources`, `raw`, `md`, `typst-book`, a
translated title, or a second slug for any canonical name. All English
characters in every new file and directory name must be lowercase.
Infrastructure such as `.git/` may coexist with this tree, but it does not
change any book-production role. Two preservation/protocol exceptions apply:
an original raw filename is not renamed merely to change case, and the required
skill entry point remains exactly `SKILL.md`.

## Workspace role boundaries

- `<book-slug>-raw/` contains only the original, unmodified source materials:
  HTML, original Markdown, text or scanned PDF, EPUB, AZW, or another supplied
  non-Typst format. Original Markdown still belongs here. Never correct,
  normalize, split, OCR-overwrite, or add scripts, reports, extracted images,
  manifests, generated text, or Typst files in this directory.
- `<book-slug>-markdown/chapters/` contains the normalized intermediate text,
  normally one Markdown file per semantic chapter. Its language matches the
  source work: Chinese remains Chinese and English remains English.
- `<book-slug>-markdown/images/` contains the highest-quality images recovered
  from the raw authority. This Markdown tree is the sole normalized
  intermediate authority shared by every Typst edition. Translation and
  bilingual pairing do not alter it.
- `<book-slug>-typst-<suffix>/` is one final-edition project. It derives
  content from the sibling Markdown tree; it must not introduce another raw or
  Markdown authority.
- `.agents/skills/<book-slug>/` is the book-local skill overlay. Put all
  book-specific scripts, dependencies, conversion rules, formula handling,
  terminology, anomalies, exceptions, and learned pitfalls there. Its
  frontmatter `name` and directory name are exactly `<book-slug>`.

Do not put book-specific scripts or temporary extraction directories at the
workspace root, in the raw directory, in the Markdown tree, or in an edition
project. Promote a local rule into this general skill only after it proves
reusable across multiple books.

## Edition project layout

Each required Typst edition uses the same internal structure:

```text
<book-slug>-typst-<suffix>/
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
├── editorial/
│   └── content-audit/
├── output/
│   ├── audit/
│   ├── build/
│   └── preview/
├── book.toml
└── source-map.json
```

`assets/figures/` contains reproducibly copied edition inputs derived from the
sibling Markdown `images/` directory; it is never an independent authority.
`book/` contains maintained Typst and generated Typst chapters. `output/`
contains only reproducible artifacts. `editorial/content-audit/` holds
accepted annotations and review ledgers and remains present even when empty so
edition trees stay structurally consistent. `book.toml` defines the edition
contract; `source-map.json` maps the sibling Markdown inputs to the generated
Typst and copied figure paths.

## Required initialization

1. Select the stable English slug and source language before creating paths.
2. Create the complete workspace skeleton for the applicable edition matrix.
3. Preserve every supplied source byte under `<book-slug>-raw/`.
4. Create or update `.agents/skills/<book-slug>/SKILL.md` before adding any
   book-specific rule or script. Start from the
   [book-local skill template](../templates/book-local-skill.md), replace its
   placeholders, and add only the resources the book actually needs.
5. Produce source-language Markdown chapters and highest-quality images before
   starting Typst conversion.
6. Copy `core.typ`, `covers.typ`, `matter.typ`, and the matching edition
   entry into every edition's `book/`; rename the entry to `template.typ`.
7. Make `book/main.typ` import `template.typ`, apply `#show: book`, render
   both covers, and include `book/chapters/`.
8. Fill each edition's `book.toml` and `source-map.json`, compile from the
   edition root with `--root .`, and record release evidence in
   `output/audit/`.
9. Run `scripts/validate_workspace.py` on the workspace, then
   `scripts/validate_book.py` on every required edition.

## Existing nonconforming workspaces

The canonical layout is mandatory for all new work and for a legacy workspace
once the user authorizes migration. Never silently rename, move, merge, or
delete existing material. Inventory every current path, map it to one canonical
role, identify duplicate authorities, and obtain migration authorization before
changing paths. After an authorized migration, do not retain aliases or layout
exceptions that recreate competing source trees.
