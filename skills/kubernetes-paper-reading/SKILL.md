---
name: kubernetes-paper-reading
description: Turn Kubernetes-related research PDFs into source-traceable bilingual reading drafts with ordered text, restored figures, citation metadata, and review boundaries. Use when extracting, translating, annotating, or auditing papers such as Borg and Omega. Do not use for Kubernetes upstream documentation or unsupported generic PDF conversion.
---

# Kubernetes Paper Reading

This skill handles the paper-reading branch of the Kubernetes knowledge workflow.
The current extraction geometry and correction rules target the archived Borg and
Omega papers. The output is a bilingual reading draft, not a publication-ready
translation and not evidence that an interpretation or performance claim is
true. Read [paper-workflow.md](references/paper-workflow.md) before running a
paper pipeline.

## Workflow

1. Identify the exact local PDF and keep it outside the repository unless it is
   safe and explicitly requested for versioning. Record its SHA-256, venue,
   authors, and source URL.
2. Extract text units in two-column reading order with
   `scripts/extract_k8s_papers.py`. The extractor excludes configured figure and
   table regions; those regions must be restored from the PDF separately.
3. Render high-resolution figure/table crops with
   `scripts/crop_k8s_paper_figures.py` and check that every referenced asset is
   readable.
4. Generate a first bilingual draft with
   `scripts/draft_k8s_papers.py`. Select `google` only when sending the source
   text to a public endpoint is acceptable; otherwise use a local model.
5. Review reading order, paragraph joins, footnotes, references, terminology,
   captions, and the boundary between source text and interpretation. Keep
   figure explanations clearly marked as interpretation.

## Script roots and dependencies

All paper scripts accept an explicit `--archive-root`; generated text and assets
go under an explicit `--output-root`. The archive must contain the configured
relative paths for `borg` or `omega`; the draft script verifies the expected
PDF hash before writing output.

The extraction and crop paths need PyMuPDF (`fitz`) and Poppler's `pdftotext`.
Translation needs either `requests` for the Google provider or
`torch`/`transformers` for a local model. These are optional runtime
dependencies, loaded only when the corresponding operation is used, so
`--help` remains usable in a minimal environment.

This skill does not commit, publish, or assert that a paper's claims have been
independently reproduced. Use `deep-concept-research` when the user asks to
turn the reading into claim/evidence/experiment research, and use
`blog-publish` separately for an explicitly requested blog operation.
