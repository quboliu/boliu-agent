#import "core.typ": *
#import "matter.typ": *
#import "covers.typ": source-cover, boliu-cover

#let book = boliu-book.with(body-font: ("Libertinus Serif", "Noto Serif CJK SC"), body-lang: "en")
#let dual-paragraph-gap = paragraph-gap
#let dual-zh-body-size = none
#let dual(en, zh, cjk-size: dual-zh-body-size) = [
  #en#parbreak()
  #zh-content(cjk-size: cjk-size)[#zh]
  #parbreak()
]
#let dual-list(en, zh) = [
  #en#linebreak()
  #zh-content(cjk-size: dual-zh-body-size)[#zh]
]
#let dual-heading(level, en, zh) = heading(level: level)[
  #show cjk-pattern: set text(style: "normal")
  #en#linebreak()
  #zh-content(cjk-font: "Noto Sans CJK SC")[#zh]
]
#let dual-caption(en, zh) = [
  #en#linebreak()
  #zh-content[#zh]
]
#let dual-note(en, zh) = book-note[
  #en#v(6pt)
  #zh-content[#zh]
]
#let dual-footnote(en, zh) = footnote[
  #en#v(2pt)
  #zh-content[#zh]
]
