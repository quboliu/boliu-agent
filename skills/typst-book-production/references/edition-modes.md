# Edition modes

## `monolingual-zh`

Use Chinese content as the only reading stream. Choose fonts with verified CJK
coverage, preserve Chinese punctuation and line-breaking policy, and make body,
heading, code, note, figure, and table typography part of the project template.
Start from the 伯流出版社 Chinese profile: `Noto Serif SC` (or a metrically
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
order. Pair complete semantic elements rather than slicing by line, word count,
or page boundary. A heading pair is one semantic heading; a note or footnote
pair is one note or footnote; captions stay with their figure or table.

Use project macros to express pairing and keep the pair together where it fits.
For long pairs, allow a controlled break and inspect the resulting page. Complex
tables may use adjacent language-specific copies with identical structure when a
single bilingual grid would be unreadable. Keep invariant code, commands,
identifiers, formulas, and URLs single-copy unless the contract says otherwise.

Maintain a terminology baseline and audit English-Chinese correspondence at the
element level. Missing translations, duplicated prose, reordered list items,
and mismatched links are content defects, not cosmetic issues.

Use the shared B5 grid and the same 10pt body size for both reading streams by
default. Keep language distinction in the verified serif pair and natural
metrics, not coloured translation panels or reduced Chinese body text. Narrow
optical compensation (for example in a small footnote) requires a documented
font-pairing test; it is never a blanket CJK rule.
