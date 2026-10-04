// DDIA hierarchy: black chapters, blue sans sections, gray nested entries.
// Native inner() retains leaders, physical folios and the actual destinations.
let contents-label(it) = [
  #if it.element.numbering != none [#it.prefix() #h(0.55em)]
  #it.inner()
]
let contents-hanging(it, indent, number-width) = pad(left: indent)[
  #grid(columns: (number-width, 1fr), gutter: 4pt, align: (left, top),
    if it.element.numbering == none { [] } else { it.prefix() },
    it.inner())
]
  show outline.entry: it => context {
    let major = it.level == 1
    let section = it.level == 2
    block(width: 100%, breakable: false, sticky: major,
      above: if major { 12pt } else if section { 2pt } else { 0pt },
      below: if major { 6pt } else { 8pt })[
      #set par(justify: false, spacing: 0pt, leading: 0.4em)
      #set text(font: if section { display-face } else { ("Libertinus Serif", "Noto Serif CJK SC") },
        size: if major { 11pt } else if section { 9pt } else { 8.4pt },
        fill: if major { black } else if section { accent.darken(15%) } else { ink-gray },
        weight: if major { "bold" } else { "regular" }, hyphenate: false)
      #show cjk-pattern: set text(
        font: if major or section { "Noto Sans CJK SC" } else { "Noto Serif CJK SC" },
        weight: if major or section { "bold" } else { "regular" }, style: "normal")
      #show link: set text(fill: if major { black } else if section { accent.darken(15%) } else { ink-gray })
      #link(it.element.location())[
        #if major {
          if it.element.numbering == none {
            block(width: 100%)[#contents-label(it)]
          } else {
            // Keep both title languages in one column after the chapter number.
            // measure() includes the active bold face and handles double digits.
            contents-hanging(it, 0pt, measure(it.prefix()).width)
          }
        } else {
          contents-hanging(it, if section { 12pt } else if it.level == 3 { 24pt } else { 36pt },
            if section { 23pt } else if it.level == 3 { 32pt } else { 42pt })
        }
      ]
    ]
  }
