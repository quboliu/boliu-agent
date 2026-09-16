// Shared 伯流出版社 B5 book mechanics. Project templates import this file;
// project content should use its semantic helpers instead of local spacing.

#let trim-width = 176mm
#let trim-height = 250mm
#let margin-top = 22mm
#let margin-bottom = 20mm
#let margin-inside = 19mm
#let margin-outside = 16mm
#let body-size = 10pt
#let accent = rgb("#1a5276")
#let ink-gray = luma(70)
#let faint = luma(120)
#let display-face = "DejaVu Sans"
#let mono-face = "DejaVu Sans Mono"

#let boliu-book(body, body-font: "Libertinus Serif", body-lang: "en") = {
  set page(
    width: trim-width,
    height: trim-height,
    margin: (top: margin-top, bottom: margin-bottom, inside: margin-inside, outside: margin-outside),
    header: context {
      set text(font: display-face, size: 8pt, fill: faint)
      grid(
        columns: (1fr, auto),
        gutter: 12pt,
        [#smallcaps[伯流出版社]],
        [#counter(page).display()],
      )
      v(3pt)
      line(length: 100%, stroke: 0.4pt + luma(200))
    },
  )
  set text(font: body-font, size: body-size, lang: body-lang)
  set par(justify: true, leading: 0.68em, spacing: 1.1em)
  set heading(numbering: "1.1")
  set footnote(numbering: "1")
  show heading: set block(sticky: true)
  show footnote.entry: set text(size: 8pt, font: body-font)
  show footnote.entry: set block(above: 0.65em)
  show link: set text(fill: accent)
  show raw.where(block: true): it => block(
    fill: luma(247),
    inset: (x: 9pt, y: 7pt),
    radius: 3pt,
    width: 100%,
    breakable: true,
    text(font: mono-face, size: 8pt, it),
  )
  show raw.where(block: false): it => box(
    fill: luma(243),
    outset: (x: 2.5pt),
    radius: 2pt,
    text(font: mono-face, size: 8.6pt, it),
  )
  show heading.where(level: 1): it => block(sticky: true)[
    #set par(justify: false)
    #text(font: display-face, size: 22pt, weight: "bold", hyphenate: false)[#it.body]
  ]
  show heading.where(level: 2): it => block(sticky: true)[
    #set par(justify: false)
    #v(1.8em, weak: true)
    #text(font: display-face, size: 13pt, weight: "bold", fill: accent.darken(10%))[#counter(heading).display("1.1") #h(0.6em)#it.body]
    #v(1.05em)
  ]
  show heading.where(level: 3): it => block(sticky: true)[
    #set par(justify: false)
    #v(1.3em, weak: true)
    #text(font: display-face, size: 11pt, weight: "bold")[#counter(heading).display("1.1") #h(0.6em)#it.body]
    #v(0.65em)
  ]
  show heading.where(level: 4): it => block(sticky: true)[
    #set par(justify: false)
    #v(1em, weak: true)
    #text(size: 10.5pt, weight: "bold", style: "italic")[#it.body]
    #v(0.5em)
  ]
  body
}

#let chapter(number, title) = {
  pagebreak(to: "odd")
  counter(footnote).update(0)
  v(30mm)
  text(font: display-face, size: 12pt, weight: "bold", fill: accent, tracking: 0.15em)[CHAPTER #number]
  v(2mm)
  heading(level: 1, numbering: none)[#title]
  v(3mm)
  line(length: 100%, stroke: 1.2pt + accent)
  v(10mm)
}

#let fig(path, caption: none, width: 100%) = {
  v(0.8em)
  block(breakable: false)[
    #align(center)[
      #image(path, width: width)
      #if caption != none [
        #v(4pt)
        #block(width: 92%)[
          #set text(size: 8.5pt, fill: ink-gray)
          #set par(justify: false)
          #caption
        ]
      ]
    ]
  ]
  v(0.8em)
}

#let book-table(columns, ..children) = {
  v(0.6em)
  set text(size: 9pt)
  table(
    columns: columns,
    stroke: none,
    inset: (x: 6pt, y: 5pt),
    align: left,
    fill: (x, y) => if y > 0 and calc.even(y) { luma(248) },
    table.hline(stroke: 1pt + luma(120)),
    ..children,
    table.hline(stroke: 1pt + luma(120)),
  )
  v(0.6em)
}

#let table-caption(body) = block(width: 100%, sticky: true)[
  #text(size: 8.5pt, fill: ink-gray)[#body]
]
