---
name: chinese-typst-book
description: Build and maintain publication-quality Chinese technical books with Typst, including source reconciliation, semantic Markdown conversion, evidence-backed annotations, typography, figures, code, reproducible PDF builds, and visual QA.
---

# Chinese Typst Book

made by quboliu

Use this skill when a local Markdown/HTML corpus needs to become a polished, maintainable Chinese technical book in Typst and PDF. The source files remain the content authority; the Typst tree is a derived, reviewable publishing artifact.

## Operating contract

1. **Lock the source before designing.** Inventory Markdown pages, navigation order, image references, external links, and any supplied web version. If both local and web sources exist, reconcile them first and record whether differences are textual, structural, asset-level, or only metadata. Do not silently “improve” source facts while typesetting.
2. **Create a decision log.** Before implementing a visual system, record the relevant research and the choices adopted, adapted, or rejected. Use `references/research-decisions.md` as the starting template. Prefer official Typst documentation, primary font documentation, and reusable skills with clear provenance.
3. **Design a system, not isolated pages.** Define page size, grid, margins, body/heading/code fonts, type scale, paragraph rhythm, chapter openings, running furniture, colour tokens, callouts, tables, figures, captions, links, footnotes, and front/back matter in one template. Keep content files semantic and free of repeated styling constants.
4. **Convert semantics, not Markdown punctuation.** Map headings, paragraphs, lists, quotes, code, links, images, captions, tables, and intentional page breaks to named Typst components. Preserve SQL/code verbatim. Escape Typst-sensitive prose characters and compile immediately after changing conversion rules.
5. **Make assets reproducible.** Prefer the supplied local figures over redrawing or AI-generating them. Preserve original image bytes when fidelity matters; copy or reference assets with stable relative paths, record dimensions and missing references, and include font licences when fonts are vendored. Never fetch replacement images merely because a local asset is inconvenient.
6. **Build deterministically.** Pin the Typst version where practical, use explicit `--font-path` and `--root`, set `SOURCE_DATE_EPOCH`/`--creation-timestamp` for repeatable output, and keep a single documented build command. Avoid hidden package or system-font dependencies.
7. **Run quality gates before handoff.** A successful compile is necessary, not sufficient. Check source coverage, missing assets, unresolved placeholders, font diagnostics, code-block integrity, figure captions, table overflow, heading/outline structure, PDF existence/page count, and representative rendered pages. Inspect both dense text/code pages and image-heavy pages with a raster preview. Use `scripts/validate_book.py` for the mechanical checks.
8. **Maintain by regeneration.** When Markdown changes, rerun conversion, rebuild, validate, and visually inspect pages affected by the change. Keep generated Typst files clearly marked as derived, keep a source map/manifest, and do not hand-edit generated chapter text unless the generator and regeneration workflow are updated too.
9. **Close the learning loop when requested.** If real project work exposes a reproducible, non-obvious failure mode, promote the general lesson to the relevant skill reference. Keep book-specific taste, page numbers, and tuned constants in that project's decision log; do not universalize one title's local settings.
10. **Audit without rewriting when requested.** If the brief requires fact-checking while the source remains immutable, keep corrections and extensions in a reviewed sidecar and inject them as visibly editorial callouts. Fail closed when an anchor drifts, and never present an unresolved reviewer disagreement as settled. Do not dismiss malformed executable tokens—such as smart punctuation replacing ASCII option prefixes or misspelled system-variable names—as ordinary copy edits when copy-paste would fail or change behavior. Read `references/content-audit.md` for the evidence, rebuttal, and injection workflow.

## Recommended project layout

```text
book/
├── book.typ                 # entry point and front/back matter
├── template.typ             # page, typography, semantic components
├── chapters/                # generated semantic Typst chapters
├── assets/                  # stable local figures, when copying is necessary
├── fonts/                   # vendored fonts plus licences
├── content-audit/           # optional annotation sidecar, evidence, rebuttal ledger
├── scripts/                 # project adapters and build commands
├── build/                   # ignored intermediate previews/dependency files
└── dist/                    # final PDF and release artefacts
```

The source Markdown can live beside this tree. Keep a machine-readable source map containing source path, output path, chapter order, and image mappings.

## Default visual direction for Chinese technical books

Use a restrained editorial palette and generous whitespace: warm paper or white pages, deep navy for structure, one amber accent for emphasis, a serif CJK body face for long reading, a sans CJK display face for hierarchy, and a mono face for SQL/terminal material. Treat the requested paper size as a hard project constraint: if the brief specifies A4, use exact A4 throughout and tune diagrams/code to that grid; do not silently substitute B5. Start with a real Chinese font family and verify glyph coverage; do not accept a PDF that silently falls back to DejaVu for Chinese text.

Keep chapter title pages recognisable, but let the body pages carry the book: running chapter/section context, page numbers, short captions, deliberate code blocks, and consistent note treatment. Avoid decorative elements that compete with diagrams or make the book look like a slide deck.

## Typst implementation rules

- Use `#set` rules for global defaults and `#show` rules or named functions for semantic components.
- Keep all repeated layout decisions in `template.typ`; chapter files should mostly contain content and component calls.
- Use Typst raw blocks for SQL/shell/code and pass a language label when syntax highlighting is available.
- Use `figure` for numbered, captioned images; use a stable image path and explicit sizing policy.
- Generate the table of contents from headings and check that the outline depth matches the intended reading hierarchy. Heading numbers belong to the semantic heading/counter, not to literal title text, so queries, running heads, and the outline remain correct.
- Derive running furniture from the current semantic level-one heading. On ordinary pages, put a short current-chapter title at the left and the folio at the right; give the cover, contents, front matter, and chapter opener their own page styles. A chapter opener normally suppresses the running head and may use a centered footer folio. Do not fill an unavailable chapter context with a repeated book title merely to occupy the header.
- Treat a chapter opener as a reusable component: make the opener, title, and a useful first content block stay together, and keep a section heading with at least its first following paragraph or figure. Use deliberate page styles rather than page-specific spacing patches or manual breaks in ordinary content.
- Treat code, figures, and tables as reading objects. Keep a figure with its caption, preserve image aspect ratio with an explicit maximum width, give code a stable reading-column width/inset and language label, avoid splitting short examples, and provide a considered fallback for long or wide blocks.
- Compile after small changes. When a syntax detail is uncertain, create a tiny probe document instead of guessing across the whole book.
- Treat warnings as failures when they indicate missing fonts, files, or malformed content.

The following rules are portable layout lessons distilled from the DDIA V2 dual-language project. They are intentionally separated from that project's bilingual-only rules: do not import English/Chinese pairing units, B5 geometry, bilingual footnote sizes, or translation terminology into a monolingual Chinese book unless its own brief requires them.

## Quality references

Read only the reference that is relevant to the current phase:

- `references/research-decisions.md` — what was researched and how it informed this skill.
- `references/typography.md` — Chinese type, font, page, spacing, and figure decisions.
- `references/source-conversion.md` — Markdown-to-Typst semantic mapping and edge cases.
- `references/content-audit.md` — immutable-source technical audit, evidence and rebuttal gates, sidecar annotation injection.
- `references/quality-gates.md` — mechanical and visual release checks.

Use the bundled scripts for repeatable work:

```bash
python3 /path/to/chinese-typst-book/scripts/validate_book.py \
  --book-dir /path/to/book \
  --source-dir /path/to/markdown \
  --pdf /path/to/book/dist/book.pdf
```

The skill is complete only when the PDF is compiled, validated, and visually sampled, and the next maintainer can reproduce it from the documented command.
