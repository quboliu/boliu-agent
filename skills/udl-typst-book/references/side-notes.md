# Paragraph-attached margin notes

## Why the source needs normalization

The PDF places blue `Notebook`, `Problem(s)`, and `Appendix` references in the outer margin. PDF-to-Markdown extraction reads the margin text in geometric order, so a lead such as `[Notebook 2.1](...)` can appear inside a sentence, while `[Supervised]` and `[learning]` appear in a following paragraph. Appendix notes can similarly be split between a body link and a following `Appendix ...` line.

## Required transformation

For each source paragraph:

1. identify a margin-note lead (`Notebook N.N`, `Problem N.N`, `Problems N.N`, or `Appendix ...`);
2. absorb adjacent same-target title fragments and range links;
3. absorb a title-only continuation paragraph or a same-target title fragment immediately before a lead paragraph;
4. remove all absorbed fragments from their extraction positions;
5. append one complete parenthetical linked note to the owning paragraph;
6. keep the original page target or external URL for every note;
7. record the source paragraph, visible label, and target in a machine-readable manifest.

The owner is the nearest prose paragraph that the PDF margin note visually accompanies. A note-only paragraph is therefore attached to the previous prose paragraph. A note lead embedded in prose is attached to that same paragraph. Multiple notes on one paragraph are rendered in source order inside one pair of parentheses, separated by `; `.

## Special cases

- `Notebook N.N` plus title fragments becomes `Notebook N.N: Title`.
- `Appendix X` plus descriptor fragments becomes `Appendix X: Descriptor`.
- `Problems N.N` plus a dash/range link retains both distinct page targets.
- A source link that is a normal figure, chapter, bibliography, website, or citation link remains inline and is not treated as a margin note.
- If the original PDF visibly contains a margin note absent from the Markdown extraction, add an explicit override rather than guessing from nearby prose. The current acceptance example is `Appendix A: Argmin function` beside equation 2.3 on original PDF page 32.
