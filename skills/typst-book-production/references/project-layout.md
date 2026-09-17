# Canonical book workspace layout

Treat the directory named `<book-name>` as the root workspace for the whole
book, not as one edition project. Derive `<book-name>` from the original work,
never from a translation: a Chinese original uses its Chinese original title;
an English original uses its English original title normalized to lowercase
ASCII words separated by single hyphens. Lowercase any English letters embedded
in a Chinese title. The name must not add an edition, translator, publisher,
date, `markdown`, or `typst` qualifier.

Use a separate `<book-skill-slug>` for the local skill. It is always a stable
lowercase English slug containing only ASCII letters, digits, and single
hyphens. Ask the user only when the original title or the skill slug is genuinely
ambiguous.

Every new workspace follows one of these two exact edition matrices. A Chinese
source has one Chinese Typst edition:

```text
<book-name>/
├── .agents/
│   └── skills/
│       └── <book-skill-slug>/
│           ├── SKILL.md
│           ├── references/          # only when this book needs them
│           └── scripts/             # only when this book needs them
├── <book-name>-raw/
├── <book-name>-markdown/
│   ├── chapters/
│   └── images/
└── <book-name>-typst-zh/
```

The matrix describes required destinations, not completion. Track structural
migration, source recovery, content conversion, translation, build, visual
proof, and release readiness independently for each edition. An empty or stub
edition satisfies none of the content or release gates merely because its
directory exists.

An English source has English, bilingual English-Chinese, and Chinese Typst
editions:

```text
<book-name>/
├── .agents/skills/<book-skill-slug>/
├── <book-name>-raw/
├── <book-name>-markdown/
│   ├── chapters/
│   └── images/
├── <book-name>-typst-en/
├── <book-name>-typst-dual/
└── <book-name>-typst-zh/
```

Do not substitute `source`, `sources`, `raw`, `md`, `typst-book`, a
translated title, or a second workspace stem for any canonical name. All English
characters in every new file and directory name must be lowercase.
Infrastructure such as `.git/` may coexist with this tree, but it does not
change any book-production role. Two preservation/protocol exceptions apply:
an original raw filename is not renamed merely to change case, and the required
skill entry point remains exactly `SKILL.md`.

## Workspace role boundaries

- `<book-name>-raw/` contains only the original, unmodified source materials:
  HTML, original Markdown, text or scanned PDF, EPUB, AZW, or another supplied
  non-Typst format. Original Markdown still belongs here. Never correct,
  normalize, split, OCR-overwrite, or add scripts, reports, extracted images,
  generated text, or Typst files in this directory. A lowercase `readme.md`
  containing provenance is the one permitted metadata file.
- `<book-name>-markdown/chapters/` contains the normalized intermediate text,
  normally one Markdown file per semantic chapter. Its language matches the
  source work: Chinese remains Chinese and English remains English.
- `<book-name>-markdown/images/` contains the highest-quality images recovered
  from the raw authority. This Markdown tree is the sole normalized
  intermediate authority shared by every Typst edition. Translation and
  bilingual pairing do not alter it.
- `<book-name>-typst-<suffix>/` is one final-edition project. It derives
  content from the sibling Markdown tree; it must not introduce another raw or
  Markdown authority.
- `.agents/skills/<book-skill-slug>/` is the book-local skill overlay. Put all
  book-specific scripts, dependencies, conversion rules, formula handling,
  terminology, anomalies, exceptions, and learned pitfalls there. Its
  frontmatter `name` and directory name are exactly `<book-skill-slug>`.

Do not put book-specific scripts or temporary extraction directories at the
workspace root, in the raw directory, in the Markdown tree, or in an edition
project. Promote a local rule into this general skill only after it proves
reusable across multiple books.

## Normalize Git-based raw material

Never retain a nested `.git` directory, `.git` file, Git submodule, gitlink,
or `.gitmodules` inside a book workspace. When supplied raw material is a Git
repository:

1. Record its canonical upstream URL, exact commit ID, branch or tag when
   relevant, retrieval date, and licence in
   `<book-name>-raw/readme.md`.
2. Verify the checkout is at that commit and has no intended local changes.
   Resolve or discard editor-generated mutations before freezing it.
3. Remove only the nested repository metadata and retain the checked-out tree
   as an ordinary immutable directory under `<book-name>-raw/`.
4. Never push book-production changes to the upstream repository. Generate the
   canonical Markdown intermediate from the ordinary snapshot.

For a large public archive that exceeds the hosting limit, keep the local raw
bytes unchanged but do not force them into ordinary Git. Record an immutable
download URL or commit, byte size, SHA-256, licence, and a verified retrieval
command in the raw `readme.md`; put the retrieval script in the book-local
skill. Use Git LFS only when the user explicitly requires the remote repository
to contain the large binary itself.

Apply the same explicit policy to large reproducible PDF outputs. Exact-ignore
the local output path when ordinary Git hosting cannot accept it, and publish it
through a release/artifact store or Git LFS only when the project explicitly
chooses that channel. Never let a broad ignore pattern hide source material,
manifests, audit records, or smaller edition outputs.

## Edition project layout

Each required Typst edition uses the same internal structure:

```text
<book-name>-typst-<suffix>/
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

1. Select the original-title `<book-name>`, stable English
   `<book-skill-slug>`, and source language before creating paths.
2. Create the complete workspace skeleton for the applicable edition matrix.
3. Preserve every supplied source byte under `<book-name>-raw/`.
4. Create or update `.agents/skills/<book-skill-slug>/SKILL.md` before adding any
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
changing paths. Hash or byte-compare apparent duplicates before choosing the
canonical copy. Move superseded, duplicate, and temporary material to a named,
recoverable quarantine outside the workspace; record its location, verify the
canonical workspace and builds, and only then delete it under explicit authority.
After an authorized migration, do not retain aliases or layout exceptions that
recreate competing source trees.

Git cannot retain empty directories. Where the canonical matrix requires a
directory before it has content, use a lowercase `.gitkeep`; remove it once real
tracked content exists. Treat `validate_workspace.py` as a structural check,
then report every edition's content and release status separately.
