#import "core.typ": *
#import "matter.typ": *
#import "covers.typ": source-cover, boliu-cover

#let book = boliu-book.with(body-font: ("Libertinus Serif", "Noto Serif CJK SC"), body-lang: "en")

#let dual-paragraph-gap = paragraph-gap

#let dual(en, zh, pair-height: trim-height - margin-top - margin-bottom) = block(
  width: 100%, above: dual-paragraph-gap, below: dual-paragraph-gap,
  layout(size => {
  let pair = [
  #block(width: 100%, above: 0pt, below: 0pt)[#en#parbreak()]
  #v(dual-paragraph-gap, weak: true)
  #block(width: 100%, above: 0pt, below: 0pt)[
    #set text(font: "Noto Serif CJK SC", size: body-size, lang: "zh")
    #set par(first-line-indent: 0pt, justify: true, leading: body-leading, spacing: paragraph-gap)
    #zh#parbreak()
  ]
  ]
  // Measure at the actual column width, not at the remaining page height.
  // Short pairs move together; overheight pairs retain normal paragraph flow.
  let height = measure(block(width: 100%, pair), width: size.width).height
  block(width: 100%, above: 0pt, below: 0pt,
        breakable: height > pair-height, pair)
}))

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
