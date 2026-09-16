#import "core.typ": *
#import "covers.typ": source-cover, boliu-cover

#show: boliu-book.with(body-font: "Libertinus Serif", body-lang: "en")

#let dual(en, zh) = block(width: 100%, breakable: true)[
  #block(width: 100%)[#en]
  #block(width: 100%)[
    #set text(font: "Noto Serif SC", size: body-size, lang: "zh")
    #set par(justify: true, leading: 0.68em, spacing: 1.1em)
    #zh
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
