# Conversion research provenance (historical)

This preserves the research lineage and project evidence incorporated from the
retired chinese-typst-book. MySQL/A4 entries are historical project examples, not
defaults. Current publisher, editorial and duplex rules take precedence. Record
new adopted/adapted/rejected choices in each book's decision log.

## Project override — 2026-09-04

The MySQL 实战45讲 brief explicitly requires strict A4 output. The generic
technical-book preference for a roomier trim is therefore overridden for this
project: `paper: "a4"`, with the PDF page box verified as 595.2756 pt ×
841.8898 pt on every page.

## Sources surveyed

| Source | Useful contribution | Decision |
| --- | --- | --- |
| [Typst reference documentation](https://typst.app/docs/) | The authoritative model for headings, outlines, pages, text, images, raw code, and set/show rules. | Adopt as the implementation authority; test uncertain syntax with a probe document. |
| [typst-author-chinese](https://github.com/Gakusyun/typst-author-chinese) | Chinese-native typography concerns: font selection, CJK/Latin mixing, punctuation, indentation, spacing, headings, tables, figures, and CLI validation. | Adapt its Chinese typography checklist; keep the actual template project-local so visual decisions remain explicit. |
| [typst-author](https://github.com/apcamargo/typst-skills/tree/main/typst-author) | Modern Typst project structure, semantic set/show rules, includes, and common syntax pitfalls. | Adopt the small-probe and compile-after-edit discipline. |
| [typst-skill](https://github.com/statzhero/typst-skill) | Practical coverage of current Typst layout, tables, figures, citations, and custom functions. | Adapt its broad implementation checklist; do not rely on undocumented packages. |
| [oracle-write-complete-book](https://github.com/Soul-Brews-Studio/oracle-book-skills/tree/main/skills/oracle-write-complete-book) | End-to-end book workflow: outline, drafting, Typst rendering, review, iteration, and quality gates. | Adopt the pipeline and visual-review loop; replace its Thai-specific defaults and unrelated repository paths. |
| [Noto CJK](https://github.com/notofonts/noto-cjk) | Official CJK font family and release/licence information. | Vendor a small, explicit Simplified Chinese font set and record its licence; never depend on an accidental system font. |

## What we deliberately combine

- **Chinese correctness** from typst-author-chinese: real CJK fonts, clear indentation and spacing rules, mixed-script care, and font-path validation.
- **Typst correctness** from typst-author and typst-skill: semantic components, set/show rules, current syntax, probes, and short compile loops.
- **Publishing process** from oracle-write-complete-book: source inventory, staged generation, deterministic build, visual review, and an explicit release gate.
- **Editorial discipline** from the typography audit idea: inspect hierarchy, density, alignment, contrast, and repeated patterns across representative pages rather than trusting one screenshot.

## What we reject or constrain

- Generic academic-writing and LaTeX-conversion recipes are useful for isolated features but are not the book's governing workflow.
- UI typography audit skills are adapted only as a visual-review mindset; screen-oriented spacing rules are not copied into a print/PDF book.
- AI-generated illustrations are not used to replace supplied technical diagrams. New visuals require an explicit editorial need and must be labelled as newly created.
- The local Markdown corpus is the content source of truth. Web pages are used for reconciliation and provenance, not for silently importing later edits.

## Current project application

For MySQL 实战45讲, the local Markdown and web version were reconciled before typesetting. The 48 page-level documents matched semantically; the 380 image references resolved to 329 unique resources, with the local copies pixel-equivalent to the web assets after ignoring transport metadata/encoding differences. The Typst project therefore uses the local Markdown text and its original .gitbook/assets figures as inputs.
