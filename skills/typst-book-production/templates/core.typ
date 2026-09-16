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
#let display-face = ("DejaVu Sans", "Noto Serif SC")
#let mono-face = "DejaVu Sans Mono"
#let math-face = "New Computer Modern Math"
#let body-leading = 0.68em
#let paragraph-gap = 1.1em

// Only content-bearing pages and chapter openers get furniture.
#let page-kind() = {
  let p = here().page()
  let heads = query(heading.where(level: 1))
  if heads.any(h => h.location().page() == p) { return "opener" }
  let marks = query(metadata.where(value: "recto")).filter(m => m.location().page() <= p)
  if marks.len() > 0 {
    let m = marks.last()
    let mp = m.location().page()
    let next = heads.filter(h => h.location().page() > mp or
      (h.location().page() == mp and h.location().position().y > m.location().position().y))
    if (next.len() > 0 and p < next.first().location().page() and
      (p > mp or m.location().position().y <= 23mm)) { return "blank" }
  }
  if not heads.any(h => h.location().page() < p) { return "front" }
  "body"
}

#let section-title(it, size, color) = context {
  grid(columns: (auto, 1fr), gutter: 6pt,
    if it.numbering != none { text(size: size, fill: color, counter(heading).display("1.1")) },
    text(font: display-face, size: size, weight: "bold", fill: color, it.body))
}

#let boliu-book(body, body-font: "Libertinus Serif", body-lang: "en") = {
  set page(
    width: trim-width,
    height: trim-height,
    margin: (top: margin-top, bottom: margin-bottom, inside: margin-inside, outside: margin-outside),
    header: context {
      if page-kind() != "body" { return }
      let hs = query(heading.where(level: 1)).filter(h => h.location().page() < here().page())
      let h = hs.last()
      let running = if h.supplement == none { h.body } else { h.supplement }
      set text(font: display-face, size: 8pt, fill: faint)
      grid(
        columns: (1fr, auto),
        gutter: 12pt,
        [#running],
        [#counter(page).display()],
      )
      v(3pt)
      line(length: 100%, stroke: 0.4pt + luma(200))
    },
    footer: context {
      if page-kind() == "opener" {
        align(center, text(size: 8.5pt, fill: faint, counter(page).display()))
      }
    },
  )
  set text(font: body-font, size: body-size, lang: body-lang)
  set par(first-line-indent: 0pt, justify: true, leading: body-leading,
    spacing: paragraph-gap, linebreaks: "optimized")
  set text(hyphenate: auto)
  set list(indent: 0pt, body-indent: 1.2em, spacing: 0.4em)
  set enum(indent: 0pt, body-indent: 1.5em, spacing: 0.4em)
  show math.equation: set text(font: math-face)
  show math.equation.where(block: true): set block(above: 8pt, below: 8pt)
  set math.equation(numbering: none)
  set heading(numbering: "1.1")
  set footnote(numbering: "1")
  show heading: set block(sticky: true)
  show footnote.entry: set text(size: 8pt, font: body-font)
  show footnote.entry: set block(above: 0.65em)
  show link: set text(fill: accent)
  set raw(theme: none)
  show raw.where(block: true): set text(font: (mono-face, "Noto Serif SC"), size: 8pt)
  show raw.where(block: false): set text(font: (mono-face, "Noto Serif SC"), size: 8.6pt)
  set figure(gap: 4pt)
  show figure.caption: set text(size: 8.5pt, fill: ink-gray)
  show figure.caption: set par(justify: false)
  show figure.caption: it => align(center, block(width: 92%)[#align(left, it)])
  show raw.where(block: true): it => block(
    fill: luma(247),
    inset: (x: 9pt, y: 7pt),
    radius: 0pt,
    width: 100%,
    breakable: true,
    {
      set par(justify: false, leading: 0.5em)
      set raw(theme: none)
      text(font: (mono-face, "Noto Serif SC"), size: 8pt, hyphenate: false, it)
    },
  )
  show raw.where(block: false): it => {
    set raw(theme: none)
    text(font: (mono-face, "Noto Serif SC"), size: 8.6pt, hyphenate: false, it)
  }
  show heading.where(level: 1): it => block(sticky: true)[
    #set par(justify: false)
    #text(font: display-face, size: 22pt, weight: "bold", hyphenate: false)[#it.body]
  ]
  show heading.where(level: 2): it => block(sticky: true)[
    #set par(justify: false)
    #v(1.8em, weak: true)
    #section-title(it, 13pt, accent.darken(10%))
    #v(1.05em)
  ]
  show heading.where(level: 3): it => block(sticky: true)[
    #set par(justify: false)
    #v(1.3em, weak: true)
    #section-title(it, 11pt, black)
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

#let chapter(number, title, running: title) = context {
  metadata("recto")
  pagebreak(to: "odd")
  counter(footnote).update(0)
  counter(heading).update((int(number) - 1,))
  v(30mm)
  text(font: display-face, size: 12pt, weight: "bold", fill: accent)[
    #if text.lang == "zh" [第 #number 章] else [CHAPTER #number]
  ]
  v(2mm)
  heading(level: 1, numbering: "1", supplement: running)[#title]
  v(3mm)
  line(length: 100%, stroke: 1.2pt + accent)
  v(10mm)
}

#let fig(path, caption: none, width: 100%) = {
  v(8pt)
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
  v(8pt)
}

#let book-table(columns, header: none, ..children) = {
  v(6pt)
  set text(size: 9pt)
  table(
    columns: columns,
    stroke: none,
    inset: (x: 6pt, y: 5pt),
    align: left,
    table.hline(stroke: 1pt + luma(120)),
    ..if header == none { () } else {
      (table.header(repeat: true, ..header), table.hline(stroke: 0.6pt + luma(120)))
    },
    ..children,
    table.hline(stroke: 1pt + luma(120)),
  )
  v(6pt)
}

// Label the returned equation for native references. Preserve source numbers
// with number: "(3.7)"; otherwise the numbered equations count automatically.
#let display-equation(body, number: "(1)") = math.equation(
  block: true, numbering: number, number-align: right, body)

#let book-note(body) = block(
  above: 10pt, below: 10pt, inset: (left: 10pt),
  stroke: (left: 0.5pt + luma(160)), breakable: true,
)[#set text(size: 9.5pt); #body]

#let table-caption(body) = block(width: 100%, sticky: true)[
  #text(size: 8.5pt, fill: ink-gray)[#body]
]
