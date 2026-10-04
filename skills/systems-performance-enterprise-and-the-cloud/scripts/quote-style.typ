// Quote attributions stay inside the quotation block and align to its right edge.
// The attribution is passed as source-faithful content, so language-specific
// dashes and punctuation are preserved instead of being synthesized here.
#let quote-attribution(body) = {
  v(2pt)
  block(width: 100%)[
    #set par(justify: false, spacing: 0pt, leading: 0.68em)
    #align(right)[#text(size: 9.5pt, fill: faint)[#body]]
  ]
}

#let quoteblock-attributed(body, attribution) = block(
  inset: (left: 14pt, right: 8pt), above: 9pt, below: 9pt,
  breakable: true,
)[
  #body
  #quote-attribution(attribution)
]
