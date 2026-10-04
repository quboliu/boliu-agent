// Bilingual quote sources share one right edge while keeping the two language
// lines in source order and using the established Chinese optical size.
#let dual-quote-attribution(en, zh) = quote-attribution([
  #en#linebreak()
  #zh-content(cjk-size: dual-zh-body-size)[#zh]
])

#let dual-quoteblock-attributed(body, attribution-en, attribution-zh) = block(
  inset: (left: 14pt, right: 8pt), above: 9pt, below: 9pt,
  breakable: true,
)[
  #body
  #dual-quote-attribution(attribution-en, attribution-zh)
]
