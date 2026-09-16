# DDIA V2 dual-language layout decisions

This is the short, maintained decision log for `ddia-v2-dual-typst`. Update it
when the user confirms a new translation or typesetting rule.

## Confirmed

- Bilingual-only work normally remains in `DDIA-V2-Typest-dual`. For the
  2026-08-21 heading-hierarchy repair, the user explicitly required the
  semantic heading levels to stay synchronized across `DDIA-V2`,
  `DDIA-V2-Typest`, and `DDIA-V2-Typest-dual`; that cross-tree synchronization
  is therefore intentional.
- Translation units are hybrid semantic blocks: target about 600–900 English
  words, but split only between complete paragraphs or complete semantic
  blocks. Continuity wins over an exact word count.
- English body font is `Libertinus Serif`. Chinese body font is local `Noto
  Serif SC`. English and Chinese body text use the same 10pt size, leading,
  spacing, justification, and ordinary paragraph treatment.
- Translation has no colored background or special callout treatment.
- Titles and headings use one shared semantic element: English line first,
  Chinese line second. They use ordinary book heading spacing, including
  extra space between the two-line heading and the following paragraph.
- Numbered chapters attach `Chapter N` to the semantic level-1 heading's
  numbering, even though the opener draws that label separately. This ensures
  the table of contents includes chapter numbers without changing the approved
  chapter-opener composition. Front matter such as Preface, Glossary, and Index
  remains unnumbered. In the table of contents, `Chapter N` is ordinary inline
  content immediately before the English chapter title; it must not occupy a
  separate hanging-number column or push the title into a special alignment.
- Structural headings follow the published DDIA second-edition hierarchy:
  chapter `N`, section `N.n`, and subsection `N.n.n`. The authority is the
  O'Reilly second-edition record (Martin Kleppmann and Chris Riccomini,
  ISBN 9781098119058, February 2026) together with the indented 2026 print
  table of contents. Markdown represents those levels as `#`, `##`, and `###`;
  lower in-body headings use `####`.
- The PDF table of contents includes levels 1 through 3. Level 1 is the chapter,
  level 2 is a blue primary section, and level 3 is a smaller gray subsection.
  Body levels 2 and 3 display decimal numbers with distinct typography. Level 4
  remains a visibly subordinate run-in-style heading without a displayed number
  and does not enter the table of contents, avoiding editorial over-numbering.
- Custom table-of-contents rows must preserve hierarchy explicitly rather than
  relying on `outline(indent: auto)`, because overriding `outline.entry` bypasses
  its default indentation. Level 1 stays at the text edge. Level 2 uses a 12pt
  inset and 23pt number column; level 3 uses a 24pt inset and 32pt number column.
  The separate number column creates a hanging title edge for wrapped lines.
  Every bilingual entry is an unbreakable block; level-2 and level-3 entries use
  8pt inter-entry spacing so separate entries are farther apart than the English
  and Chinese lines within one entry.
- Preface, Glossary, and Index remain unnumbered. Index letter-group headings
  are semantic level-2 headings but are neither numbered nor included in the
  table of contents.
- Level-1 title text is always ragged-right (`justify: false`). This applies to
  every chapter and front-matter opener so a wrapped English title cannot acquire
  stretched inter-word spaces from the globally justified body style.
- One source Note becomes one bilingual Note. English and Chinese share the
  Note container.
- One source footnote becomes one bilingual footnote. English remains 8pt in
  Libertinus Serif; Chinese uses 7pt in Noto Serif SC so the two lines are
  optically equal at this small size. This is a font-metric compensation, not
  a general Chinese-size rule: it applies only inside these bilingual
  footnotes with this font pairing. Body, headings, Notes, tables, and figure
  captions keep their own established sizes.
- Bilingual footnotes use publication-style grouping: the Chinese translation
  has a first-line indent matching the visual start of the English footnote
  text, the English-to-Chinese gap within one entry is deliberately compact,
  and the gap between separate numbered entries is larger. This is a footnote
  grouping rule, not a body-paragraph indentation rule. Implement the Chinese
  indent as an explicit first-line horizontal displacement inside
  `dual-footnote`; Typst's paragraph `first-line-indent` does not visibly take
  effect in the current nested footnote block and must not be relied upon here.
- Tables preserve source geometry exactly. Separate Chinese tables are allowed
  for complex tables, while captions remain attached to their tables.
- In Chinese table labels such as `表 1-2.`, the period is part of the table
  numbering convention and remains the ASCII full stop `.`. Do not localize it
  to the Chinese sentence-ending punctuation `。`.
- The same numbering rule applies to Chinese figure labels such as `图 8-10.`:
  retain the ASCII full stop `.` rather than the Chinese full stop `。`.
- Ordinary numbered pages use a restrained running head: a short English
  chapter identifier and title at upper left, the page number at upper right,
  and a fine gray rule below. Chapter openers omit the running head and retain
  a centered footer page number. Contents pages use `CONTENTS` at upper left
  and the page number at upper right. The cover, pre-heading front matter, and
  automatic blank verso pages show neither running heads nor page numbers.
  Running titles are explicit short metadata, not the full bilingual level-1
  heading, so long two-line chapter titles cannot leak into the page header.
- Figure image and caption stay together. Bilingual captions are two lines in
  one caption, English first and Chinese second.
- Samples use natural pagination; manual page breaks are not used to disguise
  flow or blank-space problems.

## Current implementation anchors

- Shared macros live in `DDIA-V2-Typest-dual/template.typ`: `dual`,
  `dual-heading`, `dual-title`, `dual-note`, `dual-footnote`, `fig`,
  `dual-caption`, `booktable`, and `table-caption`.
- `body-size` is the shared 10pt body-text control in both the monolingual and
  bilingual templates. Heading, code, caption, and footnote sizes remain
  independently controlled and must not be reduced merely because body text is.
- `footnote-size` controls English footnotes and `footnote-zh-size` controls
  the narrowly scoped Chinese optical compensation.
- Captions and headings use sticky blocks only where that improves attachment
  to the following element without forcing an entire unrelated element onto a
  new page.
- Cover and level-1 chapter titles disable automatic hyphenation so title words
  do not receive automatic internal breaks; body text keeps automatic hyphenation.
- The bilingual cover uses a restrained technical-book layout: English title
  first, the established Chinese title “数据密集型应用系统设计” on its own line,
  followed by English and Chinese subtitles. Edition information is not
  duplicated, and the footer explicitly identifies the artifact as an
  unofficial bilingual study edition.
- Recto starts are enforced by the `chapter` and `frontchapter` opener macros.
  The TOC does not add a trailing `pagebreak(to: "odd")`, avoiding a redundant
  TOC-to-frontchapter break while preserving odd-page starts for book sections.
- Enforced recto transitions use the shared `recto-break` helper. When the
  transition inserts an automatic blank verso, that page is completely blank:
  it has no running heading, rule, or page number. Normal body pages and chapter
  openers retain their established running-head behavior; never hard-code blank
  page numbers. Blank-page suppression always applies strictly between the
  `recto-break` marker and the next level-1 heading. The marker page itself is
  suppressed only when the marker is located at the top of the body area: that
  means the zero-height marker was pushed onto an otherwise blank transition
  page. A marker lower on the page remains attached to a content-bearing
  chapter-end page, whose running head and page number must remain visible.
- In ordinary Chinese prose, source wrapping must not create visible spaces
  between Chinese closing punctuation and the following Han character. The
  normalization is narrowly scoped to text rendered by `dual-zh`: it removes
  only whitespace in that exact context and must not alter code/raw content,
  URLs, Latin word spacing, tables, or the English source.
- Translation completeness is checked at the source element level, not merely
  by confirming that all English survives. Every English paragraph, list item,
  heading, Note/Warning segment, footnote, figure/table caption, and table cell
  must have a semantically corresponding Chinese element in the same order.
  A Chinese translation of only the final item in a multi-item English list is
  a missing-translation defect even if the surrounding semantic block is
  bilingual. Do not collapse a structured English list into an incomplete or
  ambiguously aligned Chinese block.
- Chapter 3 content QA restored nine cross-reference labels that were missing
  from extracted Example headings (Figures 3-6 and Examples 3-5, 3-7, 3-8,
  and 3-13). The surrounding second-edition prose and existing stable labels
  determine each target unambiguously. It also corrects obvious source-export
  typos (`LIVING_IN` to `LIVES_IN`, and “a the” to “the”) in the Markdown,
  monolingual Typst, and bilingual Typst trees together.
- Chapter 3 translates `hydrating IDs` by meaning as “根据 ID 加载对象” rather
  than the misleading literal “水合”, and consistently uses “一对少数” for
  `one-to-few`.
- Independent content QA uses `DDIA-V2/**/*.md` as the authority rather than
  comparing the bilingual Typst only with the monolingual Typst. Visible
  Markdown links are semantic content: glossary, index, body cross-reference,
  bibliography, archive, and DOI targets remain clickable and preserve each
  distinct URL. Internal targets use stable Typst labels when the destination
  exists.
- Unreferenced Markdown footnote definitions and O’Reilly marker backlinks are
  source-export metadata/anomalies, not placeable book content. Audit and record
  them, but never guess a paragraph attachment or add a fabricated references
  section. Obvious Markdown extraction typos may retain corrected publication
  typography when explicitly recorded as source errata.
- A visible internal fragment whose destination is absent from the Markdown
  export remains a literal fragment link and is logged as a source-export
  anomaly. Never fabricate the missing sidebar, figure, or section, or mislabel
  a nearby element merely to satisfy link resolution.
- The second-edition print table of contents contains Chapter 10 subsection
  `Logical Clocks`, but that heading and its content are absent from all three
  supplied source exports. Record this as a source-export omission. Do not add
  an empty heading, invent prose, or attach neighboring text to it.
- The supplied Chapter 6 export references both Figure 6-1 and Figure 6-2 but
  contains only the Figure 6-2 timing-diagram asset and caption. Label that
  asset `fig_replication_sync_replication`; preserve Figure 6-1 references as
  literal missing-fragment links. Never relabel Figure 6-2 as Figure 6-1 or
  fabricate the missing leader/follower diagram.
- Accepted corrections to shared English content and hierarchy are synchronized
  across Markdown, monolingual Typst, and bilingual Typst. Translation-only
  corrections remain scoped to the bilingual tree. After Chapter 3, this rule
  covers restored Example 5-4/5-5 cross-reference text, level-4 Example heads,
  OASIS attribution, and unambiguous second-edition grammar/typography errata.
- O’Reilly's second-edition errata page is a review input, not an automatic
  rewrite list: unconfirmed submissions are applied only when the supplied
  context makes the correction unambiguous. The accepted Chapter 4, 7, 8, 9,
  and 10 corrections remove grammatical duplication, restore punctuation, and
  correct `Provididng` to `Providing`; they do not alter technical meaning.
- Translate `time-of-day clock` consistently as “实时时钟” in Chapters 9–10.
  “日时钟” is not an accepted rendering. `wall-clock time/timestamp` may remain
  “墙上时钟时间/时间戳” where the English explicitly uses `wall-clock`.
- Chapter 8's introductory sentence “In the harsh reality of data systems,
  many things can go wrong:” is paired with “在数据系统的严酷现实中，许多事情都可能出错：”
  immediately before its bilingual fault list; it must not remain as an
  unpaired English lead-in.

## Version checkpoints

- v11: heading translations moved to their own line.
- v14: global spacing and orphan prevention were corrected; table and figure
  caption flow was stabilized.
- v15: Chinese footnote size was explicitly bound to the English 8pt footnote
  size (nominally).
- v16: Chinese footnotes were optically reduced to 7pt because Noto Serif SC
  appears larger than Libertinus Serif at the same nominal size. The reduction
  is explicitly scoped to this footnote/font pairing.
- v17: TOC/frontchapter odd-page breaks were de-duplicated, and automatic
  hyphenation was disabled only for the cover title and level-1 headings.
- v18: the cover was rebuilt as a bilingual technical-book cover with a strong
  left rule, publication-style Chinese title, bilingual subtitle, non-duplicated
  edition labeling, and an explicit bilingual study-edition notice.
- v19: automatic recto filler pages were made typographically blank, and
  Chinese punctuation-to-Han spacing caused by source wrapping was normalized
  within `dual-zh` only.
- v20: completeness auditing was strengthened to require element-by-element
  English–Chinese correspondence, prompted by four omitted ORM list items in
  Chapter 3 that earlier English-preservation checks did not detect.
- v21: Markdown became the independent content QA authority. Link preservation,
  cited-footnote URL parity, source-export anomaly handling, and explicit source
  errata were added after the final Markdown-based audit exposed links that had
  survived only as plain anchor text.
- v22: bilingual footnotes gained aligned Chinese first-line indentation and
  clearer group spacing: tighter within an English-Chinese pair, looser between
  separate numbered footnotes.
- v23: all three source trees were aligned to the verified DDIA second-edition
  chapter/section/subsection hierarchy; the PDF gained decimal section numbers,
  three-level contents styling, unnumbered level-4 headings, and globally
  ragged-right chapter-title text to eliminate stretched title-page spacing.
- v24: English and Chinese body text were reduced together from 10.5pt to 10pt
  after comparison with the 10.5pt A4 reference book. B5 geometry, headings,
  code, captions, and footnotes retained their established independent sizes.
- v25: the table of contents gained explicit nested insets, fixed-width number
  columns, hanging title alignment, unbreakable bilingual rows, and publication-
  quality inter-entry spacing. This replaces the ineffective automatic indent
  and weak 1pt/2.5pt gaps that caused all levels to align and run together.
- v26: Chapter 3 passed a Markdown-authority completeness audit covering every
  list item, long prose fragment, code block, figure, Note, cited footnote, and
  link. Translation terminology/semantics were corrected, and missing
  cross-reference text in nine extracted Example headings was restored.
- v27: Chapters 4–14 plus Glossary and Index passed the same Markdown-authority
  audit. All unordered and ordered list items, semantic headings, code blocks,
  figures/captions, notes, cited footnotes, and link targets align; all Chinese
  translation units are nonempty. Shared fixes were synchronized across the
  three source trees, Chapter 10 list markup was normalized, second-edition
  errata were applied conservatively, and the Figure 6-1 source-asset omission
  was separated from the correctly labeled Figure 6-2 asset.
- v28: Chapter 8's previously unpaired opening lead-in to the fault list gained
  its missing Chinese translation.
- v29: The full-book audit repaired omitted lead-ins/paragraphs in Chapters 3,
  8, and 13; wrapped eight previously raw Chinese paragraphs in Chapter 4's
  bilingual containers; and normalized eight Chapter 2 list groups into
  complete English–Chinese semantic units. The full PDF and all 17 chapter
  PDFs were rebuilt.
