# Edition modes

## `monolingual-zh`

Use Chinese content as the only reading stream. Choose fonts with verified CJK
coverage, preserve Chinese punctuation and line-breaking policy, and make body,
heading, code, note, figure, and table typography part of the project template.
Start from the 伯流出版社 Chinese profile: `Noto Serif CJK SC` (or a metrically
verified licensed replacement) at the shared 10pt body token. Retain the shared
grid, hierarchy, captions, and cover sequence; tune CJK line breaking and font
metrics through named tokens, never ad-hoc local spacing.
Do not add English source text merely as a traceability device; retain source
provenance in project records instead.

## `monolingual-en`

Use English content as the only reading stream. Set English hyphenation,
justification, quotation, citation, and code conventions deliberately in the
template. Verify that chosen fonts cover every required symbol and language
fragment, not only ASCII body prose.
Start from the 伯流出版社 English profile: `Libertinus Serif` (or a metrically
verified licensed replacement) at the shared 10pt body token, with deliberate
hyphenation and the shared grid and cover sequence.

## `bilingual`

Keep the source-language element adjacent to its translation in the declared
order. Pair complete semantic elements rather than slicing by line or word
count. A heading pair is one semantic heading; a note or footnote pair is one
note or footnote; captions stay with their figure or table.

Pairing expresses semantic correspondence in the reading stream: each source
element is followed immediately by its translation. In running body prose, text
flows naturally across page boundaries according to Typst's page budget. A page
break occurring between a source paragraph and its translation, or within either
paragraph, is normal document flow; do not lock prose pairs into unbreakable
containers (`breakable: false` or artificial block measurement wrappers), which
distort pagination, cause excessive bottom gaps, and destabilize layout
convergence. Pairing guarantees adjacent reading sequence, not physical page
containment.

Choose the pairing granularity for readability: cohesive option lists, scoring
rubrics and parameter groups may use the entire English group followed by the
entire Chinese group. Preserve item labels and order. Do not alternate languages
mechanically after every line or list item.

Identify heading pairs through source IDs, hierarchy and verified translation
mapping, not Han-character detection. A translated proper name can remain all
Latin. Adjacency is supporting evidence, not proof that two headings are a pair.
Emit one semantic heading with an explicit `linebreak()` between languages;
apply heading spacing once, not to two independently rendered headings. When
both language labels link to the same target, keep both clickable.

Use project macros to express pairing. Headings, captions, notes, and table
cells maintain their cohesive layout attachments, while running prose streams
naturally. Complex tables may use adjacent language-specific copies with
identical structure when a single bilingual grid would be unreadable. Keep
invariant code, commands, identifiers, formulas, and URLs single-copy unless the
contract says otherwise.

Maintain a terminology baseline and audit English-Chinese correspondence at the
element level. Missing translations, duplicated prose, reordered list items,
and mismatched links are content defects, not cosmetic issues.

Use the shared B5 grid and the same 10pt body size for both reading streams by
default. Keep language distinction in the verified serif pair and natural
metrics, not coloured translation panels or reduced Chinese body text. Narrow
optical compensation (for example in a small footnote) requires a documented
font-pairing test; it is never a blanket CJK rule.
