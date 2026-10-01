#import "core.typ": *
#import "matter.typ": *
#import "covers.typ": source-cover, boliu-cover

#let book = boliu-book.with(body-font: ("Libertinus Serif", "Noto Serif CJK SC"), body-lang: "en")

#let dual-paragraph-gap = paragraph-gap

#let dual(en, zh, text-size: body-size) = [
  #en#parbreak()
  #text(font: "Noto Serif CJK SC", size: text-size, lang: "zh")[#zh]
  #parbreak()
]

#let dual-heading(level, en, zh) = heading(level: level)[
  #en
  #linebreak()
  #text(font: "Noto Serif CJK SC", lang: "zh")[#zh]
]

#let dual-caption(en, zh) = [
  #en
  #linebreak()
  #text(font: "Noto Serif CJK SC", lang: "zh")[#zh]
]

#let dual-note(en, zh) = book-note[
  #en
  #v(6pt)
  #text(font: "Noto Serif CJK SC", lang: "zh")[#zh]
]

// Retain the shared 8pt note size. Optical reductions are book-specific.
#let dual-footnote(en, zh) = footnote[
  #en
  #v(2pt)
  #text(font: "Noto Serif CJK SC", lang: "zh")[#zh]
]
