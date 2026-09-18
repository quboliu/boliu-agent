# 伯流出版社 typst book design system

This is the default visual system for books made with `typst-book-production`.
It is calibrated from the finished DDIA bilingual B5 edition, then generalized
so Chinese-only, English-only, and bilingual books read as one publisher's
catalogue. It is a starting profile, not evidence that every source book had
these measurements.

## Non-negotiable method

Define the following values once as named tokens in `template.typ`. Use those
tokens for every chapter and inspect the rendered PDF before accepting a change.
Keep a profile version and any override in the book contract. A new book may
change a token only for an explicit physical or content reason; it must name the
old value, new value, reason, and tested pages. Never solve an ordinary layout
problem with local negative spacing, manual line breaks, or page-specific
nudges.

The baseline is B5. A different trim size must preserve comparable proportions,
body measure, hierarchy, whitespace, and furniture, then receive a new measured
token set rather than simply copying millimetres.

## Baseline print profile: `boliu-b5-2`

Version 2 retains DDIA's page/text geometry and explicitly adopts no first-line
indent. It removes rounded code panels, inline-code chips and table striping.
Read [editorial style](editorial-style.md) for the full composition rules and
distinguish inherited measurements below from these deliberate house refinements.

| Element | Default token | DDIA-calibrated value |
| --- | --- | --- |
| Trim | B5 | 176 × 250 mm |
| Margins | top / bottom / inside / outside | 22 / 20 / 19 / 16 mm |
| Live text width | trim width minus inner/outer margins | 141 mm |
| Body | serif, justified | 10 pt; leading `0.68em`; paragraph spacing `1.1em`; first-line indent 0 pt |
| Bilingual body pair | `paragraph-gap` | Use the same body paragraph spacing between original/translation and between adjacent paired units; no separate language or pair gap |
| English body face | `body-en` | Libertinus Serif |
| Chinese body face | `body-zh` | Noto Serif CJK SC |
| UI/head face | `display` | DejaVu Sans |
| Code face | `mono` | DejaVu Sans Mono; blocks 8 pt; inline code 8.6 pt |
| Footnotes | `footnote` | 8 pt; first entry gap `0.65em` |
| Level 1 | `h1` | 22 pt bold sans, ragged right |
| Level 2 | `h2` | 13 pt bold sans; before `1.8em`, after `1.05em` |
| Level 3 | `h3` | 11 pt bold sans; before `1.3em`, after `0.65em` |
| Level 4 | `h4` | 10.5 pt bold italic serif; before `1em`, after `0.5em` |
| Chapter opener | `chapter-top` | 30 mm down from live-area top; label 12 pt, title rule after 3 mm, body begins 10 mm after rule |
| Running head | `running-head` | 8 pt sans; 3 pt to a 0.4 pt light-gray rule; page number is paired at the outer side |
| Opener footer | `opener-folio` | centered 8.5 pt; ordinary running head omitted |
| Block code | `code-block` | 100% live width; 9 pt horizontal / 7 pt vertical inset; square corners; very light gray fill; no syntax colors |
| Figures | `figure` | vertical space 8 pt above and below; centered; caption 4 pt below image, 92% of live width, 8.5 pt |
| Tables | `table` | 9 pt text; 6 pt horizontal / 5 pt vertical cell inset; 1 pt top/bottom rules, 0.6 pt header rule, no box grid or striping; 6 pt above/below |
| Captions | `caption` | 8.5 pt muted gray; attached to the figure or table |

The values are deliberately specific because the publisher character lives in
their relationship: a 141 mm B5 measure, 10 pt text, generous chapter opening,
quiet furniture, and compact but breathable supporting matter. Do not copy a
single value while discarding the system around it.

## Language variants

All three editions use the same trim, margins, hierarchy, display face, code
style, gray/blue restrained palette, figure and table rules, and cover sequence.

- **Chinese-only:** use `Noto Serif CJK SC` at 10 pt as the baseline. Verify CJK
  punctuation, line-breaking, and the actual printed color; adjust leading only
  as a named project token after raster and print-size inspection.
- **English-only:** use Libertinus Serif at 10 pt and deliberately enable the
  appropriate English hyphenation and quotation rules. Do not force CJK-style
  breaks or spacing on English text.
- **Bilingual:** set English and Chinese in adjacent full semantic blocks at
  the same 10 pt, leading, and paragraph spacing. English normally precedes
  Chinese. Use a shared semantic heading and caption pair; do not use coloured
  translation boxes. A small-size CJK optical adjustment may apply only to the
  specifically tested component and font pairing.

## Cover sequence

Both cover pages use the selected trim, full bleed only when the printer and
source asset support it, and never carry running furniture or folios.

1. **Page 1 — source cover.** If an original cover exists, place the exact
   highest-resolution reproduction-permitted original cover without rebranding.
   Preserve aspect ratio; document dimensions, checksum, source, and rights.
   If no original cover exists, make a calm fallback with no illustration: title,
   original author, and precise original-source/version statement on the shared
   palette and grid.
2. **Page 2 — 伯流出版社 cover.** This is a clearly separate publisher-edition
   statement, not an imitation of page 1. It prominently includes `伯流出版社`,
   the work title, original author, source/version, edition/language statement,
   and a relevant historical subject. The principal visual is a black or
   restrained single-accent line drawing: either a famous historical figure's
   portrait or a known scene in which that figure took part. Select a subject
   that illuminates the book's intellectual context, credit it, and use only an
   image with documented legal reuse or a documented public-domain basis. Do
   not use living people, fabricated portraits, anonymous decorative stock, or
   misleading historical claims.

The publisher cover should privilege white space, a single strong vertical or
horizontal rule, disciplined typography, and one line-art visual. It should
look recognisably related to the DDIA calibrated cover while remaining about
the book in hand.

## Visual acceptance

Rasterize at 144–288 PPI and inspect at actual size. Test a chapter opener,
dense prose, a long heading, a footnote page, a code page, a dense table, a
large figure, and both cover pages. Reject the release for overflow, a heading
separated from its following text, detached captions, weak table hierarchy,
unintended font fallback, text too close to trim, a distorted source cover, or
an undocumented publisher-cover subject or image source.
