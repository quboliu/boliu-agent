// Keep complete bilingual entries together without moving the native note marker.
#let shared-book = book
#let book(body) = {
  show footnote.entry: it => block(breakable: false, it)
  shared-book(body)
}
#let footnote-zh-size = 7pt
#let footnote-marker-body-gap = 0.4pt
#let dual-footnote(en, zh) = footnote[
  #set text(size: 8pt)
  #en
  #v(0.18em)
  // Match the first translated glyph to the first English glyph after the
  // native superscript marker. The marker width must be measured because it
  // changes for two- and three-digit footnote numbers.
  #context {
    let marker-width = measure(super(counter(footnote).display())).width
    block(inset: (left: 1em + marker-width + footnote-marker-body-gap))[
      #set text(size: 8pt)
      #set par(justify: false, spacing: 0pt, leading: 0.5em)
      #zh-content(cjk-size: footnote-zh-size)[#zh]
    ]
  }
]
