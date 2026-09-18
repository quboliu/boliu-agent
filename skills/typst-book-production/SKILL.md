---
name: typst-book-production
description: Produce and maintain publication-quality Typst books in a strict raw-to-Markdown-to-Typst workspace, with Chinese, English, or bilingual editions, book-local skill overlays, reproducible builds, and duplex PDF verification.
---

# Typst Book Production

made by quboliu

Produce a faithful, maintainable, and reproducible Typst book. This is a
general production core: each book supplies its own source provenance, language
policy, typography, semantic macros, terminology, and content exceptions.

## Use the 伯流出版社 design system

Every book begins from the shared publication profile in
[伯流出版社 design system](references/publisher-design-system.md). Its B5 grid,
type scale, vertical rhythm, figure, table, code, running-furniture, and cover
rules are calibrated from the finished DDIA edition. This is how independently
produced books retain one recognisable publisher character.

Read [editorial style](references/editorial-style.md) before every production or
layout change. The current profile is `boliu-b5-2`: minimalist, flush-left
paragraph starts (explicitly zero first-line indent) in all three editions,
with paragraph spacing. It defines code, equations, tables, images, punctuation,
pagination, front matter, and measurable release gates. Implement decisions in
the shared templates and verify output, not only written instructions.

Every complete-book PDF must support direct duplex printing: portrait pages in
reading order, left binding, long-edge flip, mirrored inside/outside margins,
outward-facing running folios, and chapter starts on odd physical pages.
Read [duplex printing](references/duplex-printing.md) before building or handing
off a book. Retain intentional blank versos and the fixed two-cover sequence.

Treat the profile as a measurable default, not a collection of decorative
suggestions. Put its tokens in the book's `template.typ`; do not replace them
with chapter-local spacing. A departure is allowed only for a real content,
language, binding, accessibility, or print constraint, and must be recorded in
the book contract with the replacement value and a visual comparison.

## Start from the runnable templates

Copy the relevant file from `templates/` into the book repository together with
`core.typ`, `covers.typ`, and `matter.typ`; do not edit the copy inside this skill. Use
`monolingual-zh.typ`, `monolingual-en.typ`, or `bilingual.typ` as the project
template according to the contract. The three entry points share the same core
tokens and covers module, so a change to page geometry, hierarchy, figures,
tables, or running furniture remains a deliberate project override rather than
an accidental divergence. Read [template use](references/template-use.md) before
adapting them.

The importing main file MUST apply `#show: book` after importing the edition
module. Importing a module does not apply its local show rules to the caller.
Verify actual PDF page dimensions; compilation alone cannot detect a missed
template. The smoke script in `scripts/check-templates.py` exercises this.

The first two pages are mandatory cover matter:

1. **Source cover (page 1).** When a published or open-source book already has
   an original cover, use that exact cover from the best available high-
   resolution, reproduction-permitted source; retain its proportions and record
   source, checksum, licence or permission, and any crop. Do not redraw,
   stylise, upscale, or substitute it. When no original cover exists, make the
   neutral fallback cover defined by the design system: title, original author,
   original-source/version statement, and no invented artwork.
2. **伯流出版社 cover (page 2).** Always follow with the publisher's distinct
   edition cover. It must visibly carry `伯流出版社`, identify the edition without
   impersonating the source edition, and use a contextually relevant, lawful
   line-drawing portrait of a well-known historical figure or a line-drawing of
   a notable scene in which that figure participated. Record the image source,
   rights, subject, and relevance. Do not use a living person's likeness,
   invented historical portrait, or a generic decorative image.

If a reproduction-permitted high-resolution original cover or the required
rights/provenance cannot be established, stop before distribution and ask for a
source or permission; a low-resolution web preview is not an acceptable stand-in.

## Select the source language and edition matrix

At the start, identify the source language and create its complete required
edition matrix. Record each edition in its own book contract:

- `monolingual-zh`: a Chinese-only edition.
- `monolingual-en`: an English-only edition.
- `bilingual`: adjacent English-Chinese content, unless the project explicitly
  specifies the opposite language order.

A Chinese source creates only `monolingual-zh`. An English source creates
`monolingual-en`, `bilingual`, and translated `monolingual-zh`; completing
one does not make the other required editions optional.

Read [edition modes](references/edition-modes.md) for the selected mode. Do not
introduce bilingual duplication into a monolingual edition, or simplify a
bilingual edition into a translation summary.

## Enforce the canonical book workspace

Read [project layout](references/project-layout.md) before creating, converting,
or migrating a book. Name the root workspace from the original work, never its
translation: a Chinese original uses its Chinese title; an English original
uses its English title normalized as a lowercase slug. Call this directory
name `<book-name>`. It contains three separated production layers:

1. `<book-name>-raw/` is immutable original material and contains nothing else.
2. `<book-name>-markdown/{chapters,images}/` is the source-language normalized
   intermediate and the content authority for every Typst edition.
3. `<book-name>-typst-<suffix>/` contains one final edition project.

A Chinese source requires only `-typst-zh`. An English source requires all of
`-typst-en`, `-typst-dual`, and `-typst-zh`. Do not bypass the Markdown
layer, store corrected material in the raw tree, invent alternate directory
names, keep a second source authority inside an edition, or retain nested Git
repositories or submodules anywhere in the book workspace. Run
`scripts/validate_workspace.py` before production and handoff. This validator
proves the directory contract only. A required edition directory may exist as a
scaffold while its content, translation, build, visual proof, or release status
is still incomplete; record those states separately and never report structural
compliance as publication completion.

## Establish the book contract

Before conversion or layout work, read the repository instructions and create
or update the project's book contract. It identifies the content authority,
edition, language order, source and output locations, template, fonts, build
command, source map, terminology, known anomalies, canonical project name,
publisher-profile version, and both cover records. Read
[project contracts](references/project-contract.md) for the required decisions.

The raw directory is immutable evidence. The source-language Markdown
intermediate is the normalized content authority for Typst conversion. Apply
reviewed corrections there, record their raw provenance and rationale, and
regenerate affected Typst editions instead of silently patching them.

## Produce semantic Typst

Read [source conversion](references/source-conversion.md) before converting or
regenerating content. Reconcile supplied local and web editions before choosing
authority; distinguish text, hierarchy, asset, and metadata-only differences.
Keep generated chapters marked as derived and regenerate them with their source
map. Existing authored Typst may remain maintained source under its contract.

For authoritative PDFs, read [PDF source recovery](references/pdf-source-recovery.md)
for paragraph-owned margin notes, vector extraction, code recovery and geometric
acceptance cases. These rules absorb the reusable UDL/PDF-dual experience without
bundling a universal converter or imposing UDL's paths, A4 size or special labels.
Distinguish producing a house-style book from preserving a paper or slide deck:
non-book PDF adaptations require their own explicit layout contract and must not
silently inherit the book's covers, B5 geometry or chapter machinery.

For Markdown corpora, inspect the actual source dialect and create or adapt a
book-local converter according to
[Markdown conversion and book structure](references/markdown-and-matter.md).
This skill deliberately does not bundle a universal Markdown converter. Keep
the converter, pinned dependencies, and acceptance tests in
`.agents/skills/<book-skill-slug>/` so future regeneration is repeatable rather than
rewritten each session.
The same reference documents reusable
contents, unnumbered front matter, part pages, copyright and quotation macros.

1. Inventory chapters, hierarchy, links, figures, tables, code, notes,
   footnotes, citations, and assets before conversion.
2. Convert semantic elements, not Markdown punctuation or rendered page shapes.
   Preserve reading order, numbering, visible links, code, formulas, figures,
   tables, and citations.
3. Keep repeated layout decisions in `template.typ` and named semantic macros.
   Keep chapter files focused on content; do not use page-specific spacing or
   manual breaks to hide ordinary flow problems.
4. Keep a source map between every content input and generated Typst output.
   When source files change, regenerate instead of hand-editing derived text.
5. Preserve supplied assets with stable paths and original bytes where fidelity
   matters. Do not replace a missing source visual with an invented one.

When the edition matrix has more than one output, a figure, table, code-block,
caption, or pagination policy is shared by default. Keep it in one template,
semantic macro, or data mapping consumed by every renderer; do not maintain
parallel edition-specific overrides that can drift. An intentional language or
content exception must be named in the book contract and checked in every
affected edition.

For bilingual work, pair each complete semantic element with its translation:
headings, prose, lists, captions, notes, footnotes, and table cells. Keep code,
commands, formulas, identifiers, URLs, and other invariant material single-copy
unless the book contract defines a different policy.

## Build and verify

For requested fact-checking, corrections, or version updates, read
[content audit](references/content-audit.md). Keep author text immutable and
inject accepted editorial notes from a separately reviewed sidecar. Verify exact
source hashes and anchors, evidence, acceptance and emitted-note counts; reject
drift or unresolved claims. This workflow does not run merely because a book
needs typesetting. House typography, two-cover sequencing and duplex rules
remain authoritative for annotated editions.

Use the project's explicit Typst version, root, font path, and reproducible
build command. Capture the raw Typst diagnostic stream for every release build.
Warnings are release failures unless the contract documents a narrowly reviewed
exception; font fallback and `document did not converge` are always blockers.
Pass the captured diagnostic file to `scripts/validate_book.py --compile-log`.
A successful, warning-free compile is necessary but not sufficient. Read
[verification](references/verification.md) before handoff. For iterative layout
or renderer changes, also read
[release hardening](references/release-hardening.md); it adds the cross-edition,
whole-book, PDF-interaction, and artifact-retention checks that ordinary
compilation cannot provide.

Read [production pipeline](references/production-pipeline.md) for deterministic
builds, the source manifest, real-project validation, regeneration and visual
regression checks. Use `scripts/validate_book.py` on the actual project;
`scripts/check-templates.py` tests bundled fixtures and cannot replace it.
For the inherited research lineage and historical project evidence, consult
[conversion research](references/conversion-research.md).

Verify content coverage, hierarchy and numbering, links and cross-references,
assets, fonts, code integrity, table and figure geometry, PDF existence and
page count. Rasterize and inspect representative chapter openers, dense text,
code, tables, footnotes, and image-heavy pages.

Compile the matching example in `templates/examples/` after changing a template
module. The examples intentionally render the publisher-cover artwork warning
until a project supplies a documented historical line drawing; that warning is
permitted for a fixture but is a release blocker for a book.

## Project overlays

Every book workspace has a local overlay at
`.agents/skills/<book-skill-slug>/SKILL.md`. The skill identifier is a stable
lowercase English slug even when the workspace uses a Chinese original title;
its directory and frontmatter name must match. The overlay owns book-specific
scripts, dependencies, terminology,
formula handling, fonts, macro names, approved visual decisions, source
anomalies, and learned pitfalls. It may refine the production core for genuine
content needs, but it must not rename, collapse, or bypass the canonical raw,
Markdown, edition, language, or local-skill boundaries.

Promote a lesson from a project overlay into this core only when it is
reproducible and useful across multiple books. Keep one-book taste and
exceptions in that book's decision log.
