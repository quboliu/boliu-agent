#import "core.typ": *
#import "matter.typ": *
#import "covers.typ": source-cover, boliu-cover

#let book = boliu-book.with(body-font: ("Libertinus Serif", "Noto Serif SC"), body-lang: "en")

#let dual(en, zh) = block(width: 100%, breakable: true)[
  #block(width: 100%)[#en#parbreak()]
  #block(width: 100%)[
    #set text(font: "Noto Serif SC", size: body-size, lang: "zh")
    #set par(first-line-indent: 0pt, justify: true, leading: 0.68em, spacing: 1.1em)
    #zh#parbreak()
  ]
]

#let dual-heading(level, en, zh) = heading(level: level)[
  #en
  #linebreak()
  #text(font: "Noto Serif SC", lang: "zh")[#zh]
]

#let dual-caption(en, zh) = [
  #en
  #linebreak()
  #text(font: "Noto Serif SC", lang: "zh")[#zh]
]

#let dual-note(en, zh) = book-note[
  #en
  #v(6pt)
  #text(font: "Noto Serif SC", lang: "zh")[#zh]
]

// Retain the shared 8pt note size. Optical reductions are book-specific.
#let dual-footnote(en, zh) = footnote[
  #en
  #v(2pt)
  #text(font: "Noto Serif SC", lang: "zh")[#zh]
]
