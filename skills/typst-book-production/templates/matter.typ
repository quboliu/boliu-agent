// Book structure adapted from pphc; visuals follow the shared house profile.
#import "core.typ": *

#let frontchapter(title, body, running: title) = {
  metadata("recto")
  pagebreak(to: "odd")
  counter(footnote).update(0)
  set heading(numbering: none)
  v(30mm)
  heading(level: 1, numbering: none, supplement: running)[#title]
  v(3mm)
  line(length: 100%, stroke: 1.2pt + accent)
  v(10mm)
  body
}

// A semantic unnumbered opener; the next numbered chapter resets its counter.
#let part-page(number, title, blurb: []) = {
  metadata("recto")
  pagebreak(to: "odd")
  v(45mm)
  text(font: display-face, size: 12pt, fill: accent)[#number]
  v(10mm)
  heading(level: 1, numbering: none, supplement: title)[#title]
  v(6mm)
  line(length: 30mm, stroke: 0.6pt + accent)
  v(8mm)
  blurb
}

// Optional matter follows the mandatory two covers; never replaces page 2.
#let title-page(title, author, edition: []) = {
  pagebreak(weak: true)
  set page(header: none, footer: none)
  v(35mm)
  text(font: display-face, size: 25pt, weight: "bold", hyphenate: false)[#title]
  v(10mm)
  text(size: 11pt)[#author]
  v(6mm)
  edition
  pagebreak()
}

#let copyright-page(body) = {
  pagebreak(weak: true)
  set page(header: none, footer: none)
  v(1fr)
  set text(size: 8.5pt, fill: ink-gray)
  set par(justify: false)
  body
  v(12mm)
  pagebreak()
}

#let toc-page(title: [Contents], depth: 3) = {
  pagebreak(weak: true)
  set page(
    header: context {
      if page-kind() == "blank" { return }
      set text(font: display-face, size: 8pt, fill: faint)
      if calc.odd(here().page()) {
        grid(columns: (1fr, auto), title, counter(page).display())
      } else {
        grid(columns: (auto, 1fr), counter(page).display(), align(right, title))
      }
      v(3pt)
      line(length: 100%, stroke: 0.4pt + luma(200))
    },
    footer: none,
  )
  text(font: display-face, size: 22pt, weight: "bold")[#title]
  v(8mm)
  outline(title: none, depth: depth, indent: auto)
  // The next structural component owns the page transition.
}

#let qattr(body) = {
  v(2pt)
  align(right, text(size: 9.5pt, fill: faint)[— #body])
}

#let quoteblock(body, attribution: none) = block(
  inset: (left: 14pt, right: 8pt), above: 9pt, below: 9pt,
  breakable: true,
)[
  #body
  #if attribution != none { qattr(attribution) }
]
