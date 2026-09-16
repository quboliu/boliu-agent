# Evidence-backed content annotations

Use only when the brief asks for fact-checking, corrections, deepening or version
updates. Ordinary typesetting does not trigger this workflow. Preserve original
sources; publish accepted editorial notes separately, never silent edits.

## Scope and evidence

Record source hashes, audited chapters, source-era/current versions, subject
boundaries, allowed note types and reviewer requirements. Later behavior is a
version change, not proof the original was wrong. Accept reader-relevant
corrections or missing boundaries/mechanisms, not taste, trivia or claims the
source already adequately qualifies.

Apply general reasoning checks where relevant:

- Verify executable spelling against raw source and primary documentation;
  typography that changes execution is semantic, not merely cosmetic.
- Verify alleged later self-corrections against the exact counterexample, not
  a matching topic. Keep safety prerequisites near actionable instructions.
- Disambiguate lifecycle stages, layers, units and measurement scopes before
  equating similarly named concepts or diagnostics.
- Check local optimizations against global correctness. Prove semantic
  equivalence before recommending transformations; sample agreement is not proof.
- Separate existence, applicability, enablement, limits and triggers. Verify
  version-specific defaults and operational side effects instead of extrapolating.

Read [database audit examples](database-audit-examples.md) only for relevant
database material. Other fields supply project-local checks; do not turn this
general document into a catalogue of domain-specific exceptions.

Use evidence labels: `document-confirmed`, `source-confirmed`, `reproduced`,
`analytically-derived`, or `text-confirmed`. Preserve primary sources, exact
versions and assumptions. Analytical claims require checkable derivations;
textual contradictions alone do not determine which passage is correct.
Performance magnitudes, timing and configuration-sensitive claims require
reproduction. Community errata provide candidates, not automatic acceptance.

## Review and acceptance

Keep candidates, objections, accepted/rejected/unresolved verdicts and final
wording in an editorial ledger. If a second reviewer is required, submit every
candidate with its exact anchor and evidence, retain the real exchange and
require agreement on the final minimal claim. Do not impersonate reviewers.
Unresolved claims stay out of the book. Otherwise record an explicit editorial
decision; do not invent a second-review gate.

## Project-owned annotation integration

Keep accepted notes separate from immutable sources and generated chapters,
for example in `editorial/content-audit/annotations.json`, `ledger.json` and
optional `reviewer-sessions/`. The project implements injection and its tests;
the generic validator does not verify evidence or reviewer agreement.

Each accepted note needs a stable ID, source path/hash, semantic location,
expected occurrence count, placement, type, final text and evidence links.
Use format-appropriate anchors: exact raw quotes for Markdown, or stable IDs
and page/region mappings for other sources. Preserve raw escapes rather than
display-normalized text. Fail on source drift, ambiguous anchors or omitted
material; never guess note placement.

Cross-check accepted ledger and renderable note IDs/text in both directions.
Emit each accepted note exactly once; reject rejected/unresolved entries. Check
reviewer archives only when the contract requires that review mode. Preserve
the source-to-output map and test hash/anchor drift, missing/duplicate emission
and unaccepted notes. Escape literal text for its actual Typst context, including
comment delimiters and brackets, while preserving inline semantics. Compile
minimal probes; do not alter source prose to accommodate the renderer.

## Presentation and release

Use the house style: white background, gray side rule, textual category label
and readable evidence footer. Keep original prose visually primary. Place a
minimal note after a complete semantic block, not inside code or a sentence.
Keep short notes together; use a reviewed breakable variant with attached
headings for overheight notes. Cross-book references need the actual shared
mechanism, a verified excerpt and stable location, not merely a keyword match;
they do not replace primary evidence about the audited subject.

Rebuild the whole PDF. Check accepted/emitted counts, evidence links, attachment,
overflow and blank-page anomalies. Inspect every annotated page and its neighbors.
Report precisely which chapters were audited and what remains unresolved; a
pilot is not a whole-book audit.
