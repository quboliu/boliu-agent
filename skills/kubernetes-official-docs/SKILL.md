---
name: kubernetes-official-docs
description: Process Kubernetes upstream official documentation into source-faithful bilingual reading drafts and auditable standalone Markdown. Use when aligning official English and zh-cn sources, expanding Hugo shortcodes, pinning documentation versions, restoring code or figures, assembling article parts, or auditing the result. Do not use for kubectl operations, cluster troubleshooting, or generic Kubernetes Q&A.
---

# Kubernetes Official Docs

made by quboliu

This skill covers the official-document source workflow, not Kubernetes runtime
operations. Its normal output is a reviewable bilingual draft or an audited
standalone Markdown article. A generated translation is a drafting aid and
never closes source-fidelity or terminology review by itself.

## Choose the workflow

- For a Kubernetes `zh-cn` page whose HTML comments contain the English source,
  use the source-pair workflow in [official-docs-workflow.md](references/official-docs-workflow.md).
- For an already extracted bilingual draft, use the normalization, shortcode
  completion, and code-unquoting scripts in that same reference.
- For the pinned Kubernetes API Conventions document, use
  `scripts/draft_api_conventions.py`; read the translation boundary notes before
  choosing Google or a local model.
- For assembling the current five-article topic set and producing audit reports,
  use the explicit-root commands in the reference. Do not assume a personal
  archive or blog path.

## Required invariants

1. Record the upstream repository and commit/version before generating output.
   English and official Simplified Chinese sources must come from the same
   frozen source boundary when bilingual alignment is claimed.
2. Keep English source blocks, code literals, link destinations, API identifiers,
   and substantive shortcode expansions distinguishable during review.
3. Treat feature-state, glossary, code-sample, figure, table, and third-party
   shortcode expansion as content restoration, not lossless normalization. Check
   each expansion against the pinned source archive.
4. Run the audit script after assembly. Resolve hard failures; report skipped
   optional checks such as a missing Pandoc installation instead of silently
   treating them as passes. Read [audit-and-provenance.md](references/audit-and-provenance.md)
   for the manual boundary.
5. Do not commit or push a blog change as part of this skill. If the user asks
   for publication, hand the prepared article to `blog-publish` after the user
   confirms the target repository.

## Script execution

Resolve this skill's directory, then invoke scripts with `python3` and explicit
paths. `--help` must be safe to run before any source or output exists. The
official-document scripts use these roots:

- `--draft-root`: generated article parts, defaulting to
  `./kubernetes-topic-drafts`.
- `--output-root`: assembled article directory, defaulting to `./阅读`.
- `--archive-root`: required pinned source archive for restored assets and
  source hashes.

The source-pair, normalization, and code-unquoting helpers modify only the
paths explicitly supplied to them. Inspect the target diff before running the
in-place completion or normalization steps on user content.

The translation scripts may use a public network endpoint or a local
Hugging Face model. Explain that boundary before sending source text externally;
keep translation caches out of committed content. Never place credentials or
raw environment dumps in this skill.
