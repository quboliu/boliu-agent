// Book-local publishing policy: colored lossless listings and separate tables.
#import "core.typ": *

#let publication-mark(kind, id, language: none, phase: "start") = context {
  [#metadata((kind: kind, id: id, language: language, phase: phase, page: here().page())) <publication-mark>]
}

#let source-anchor(target) = if target != none { [#metadata("source-anchor") #label(target)] }

#let technical-code(path, language, id, target: none) = {
  let rows = json(path)
  block(width: 100%, fill: luma(247), inset: (x: 9pt, y: 7pt),
        above: 7pt, below: 7pt, breakable: true)[
    #set text(font: (mono-face, "Noto Serif CJK SC"), size: 8pt, hyphenate: false, top-edge: "ascender", bottom-edge: "descender")
    #set par(justify: false, leading: 0.5em, spacing: 0pt, linebreaks: "simple")
    #source-anchor(target)
    #publication-mark("code", id, language: language)
    #block(width: 100%, sticky: true, above: 0pt, below: 3pt)[
      #align(right, text(font: display-face, size: 6.5pt, fill: faint, if language == "console" { "shell / output" } else if language == "bash" { "shell" } else if language == "text" { "output / notation" } else { language }))
    ]
    #for row in rows {
      if row.len() == 0 { v(12pt, weak: false) } else {
        block(width: 100%, above: 0pt, below: 0pt, breakable: true, inset: (y: 2pt))[
          #for token in row {
            let value = token.at(1)
            if value.len() > 74 and value.contains(regex("^[─━=+_-]+$")) {
              let display = ""
              for (i, ch) in value.clusters().enumerate() {
                display += ch
                if calc.rem(i + 1, 64) == 0 { display += "\u{200b}" }
              }
              value = display
            }
            text(fill: rgb(token.at(0)), value)
          }
        ]
      }
    }
    #publication-mark("code", id, language: language, phase: "end")
  ]
}

#let table-identity(caption, language, id) = {
  let untitled = (
    "table-001": ([Typographic Conventions], [排版约定]),
    "table-091": ([USE Method: Physical Resources], [USE 方法：物理资源]),
    "table-092": ([USE Method: Software Resources], [USE 方法：软件资源]),
    "table-093": ([sar Summary], [sar 摘要]),
  )
  if caption == none {
    if untitled.keys().contains(id) { untitled.at(id).at(if language == "zh" { 1 } else { 0 }) }
    else { if language == "zh" { [表格] } else { [Table] } }
  } else { caption }
}

#let table-heading(caption, language, id, continued: false) = {
  set text(font: ("Libertinus Serif", "Noto Serif CJK SC"), lang: language)
  set par(justify: false, leading: 0.5em, spacing: 0pt)
  text(size: 8.5pt, fill: ink-gray)[
    #table-identity(caption, language, id)
    #if continued { if language == "zh" { [（续）] } else { [ (continued)] } }
    #text(size: 7.5pt)[#if language == "zh" { [ — 中文] } else { [ — English] }]
  ]
}

#let edition-table(widths, rows, cells, caption: none, language: "en", id: "table", target: none, numeric: none, header-height: auto) = {
  set text(font: ("Libertinus Serif", "Noto Serif CJK SC"), size: 9pt, lang: language)
  set par(justify: false, leading: 0.5em, spacing: 0pt)
  let own-label = label("continued-" + id + "-" + language)
  block(width: 100%, breakable: true, above: 6pt, below: 6pt)[
    #source-anchor(target)
    #publication-mark("table", id, language: language)
    #table(columns: widths, rows: if rows == auto { auto } else { (header-height, ..rows) }, stroke: none, inset: (x: 6pt, y: 5pt),
      align: (x, y) => if numeric != none and numeric.at(x) { right } else { left },
      table.header(repeat: true,
        table.cell(colspan: widths.len(), align: left, inset: (x: 0pt, top: 0pt, bottom: 6pt))[
          #context {
            let first-page = query(own-label).first().location().page()
            table-heading(caption, language, id, continued: here().page() > first-page)
          }
        ],
        table.hline(stroke: 1pt + luma(120)),
        ..cells.slice(0, widths.len()),
        table.hline(stroke: 0.6pt + luma(120)),
      ),
      ..cells.slice(widths.len()),
      table.hline(stroke: 1pt + luma(120)),
    )#own-label
    #publication-mark("table", id, language: language, phase: "end")
  ]
}

#let paired-tables(weights, en, zh, caption-en: none, caption-zh: none, id: "table", target: none, numeric: none) = layout(size => {
  let n = weights.len()
  let total = weights.sum()
  let widths = weights.map(w => size.width * w / total)
  // Both copies share column widths and the maximum measured height of each row.
  let heights = ()
  for y in range(int(en.len() / n)) {
    let height = 0pt
    for x in range(n) {
      let index = y * n + x
      for (language, body) in (("en", en.at(index)), ("zh", zh.at(index))) {
        let cell = [
          #set text(font: ("Libertinus Serif", "Noto Serif CJK SC"), size: 9pt, lang: language)
          #set par(justify: false, leading: 0.5em, spacing: 0pt)
          #body
        ]
        height = calc.max(height, measure(block(width: widths.at(x) - 12pt, cell), width: widths.at(x) - 12pt).height + 10pt)
      }
    }
    heights.push(height)
  }
  let header-height = 0pt
  for (language, caption) in (("en", caption-en), ("zh", caption-zh)) {
    for continued in (false, true) {
      let measured = measure(block(width: size.width)[#table-heading(caption, language, id, continued: continued)], width: size.width).height + 6pt
      header-height = calc.max(header-height, measured)
    }
  }
  edition-table(widths, heights, en, caption: caption-en, language: "en", id: id, target: target, numeric: numeric, header-height: header-height)
  edition-table(widths, heights, zh, caption: caption-zh, language: "zh", id: id, numeric: numeric, header-height: header-height)
})

// Float numbered figures to a nearby page edge; keep the original image scale
// and complete caption together while following paragraphs fill the body.
#let fig(path, caption: none, width: 100%, floating: true) = context {
  let live-width = trim-width - margin-inside - margin-outside
  let live-height = trim-height - margin-top - margin-bottom
  let full-image-height = measure(image(path, width: live-width)).height
  let caption-height = if caption == none { 0pt } else {
    measure(block(width: live-width * 92%)[
      #set text(size: 8.5pt, fill: ink-gray)
      #set par(justify: false)
      #caption
    ], width: live-width * 92%).height
  }
  let scale = 1.0
  for candidate in (1.0, 0.8, 0.6) {
    scale = candidate
    if full-image-height * candidate + caption-height + 28pt <= live-height { break }
  }
  figure(
    placement: if caption == none or not floating { none } else { top },
    scope: if caption == none or not floating { "column" } else { "parent" }, numbering: none, supplement: none, outlined: false,
    block(width: 100%, breakable: false, above: 8pt, below: 8pt)[
      #publication-mark("figure", path)
      #metadata((kind: "figure-size", asset: path, scale: scale)) <figure-size>
      #align(center, image(path, width: width * scale))
      #if caption != none [
        #v(4pt)
        #pad(left: 4%, right: 4%)[
          #set text(size: 8.5pt, fill: ink-gray)
          #set par(justify: false)
          #align(center, caption)
        ]
      ]
      #publication-mark("figure", path, phase: "end")
    ],
  )
}

// Index is a separate supporting component, never a body-prose spacing override.
#let index-size = 9pt
#let index-gap = 3pt
#let index-gutter = 12pt
#let book-index(body) = {
  set text(size: index-size, top-edge: "ascender", bottom-edge: "descender")
  set par(spacing: index-gap)
  show heading.where(level: 2): it => block(sticky: true, above: 8pt, below: 4pt)[#text(size: 11pt, weight: "bold", it.body)]
  columns(2, gutter: index-gutter, body)
}

// Native current-edition folios, with original print-page provenance preserved.
#let index-page(target, original) = context {
  let location = query(label(target)).first().location()
  link(location)[#counter(page).at(location).first()#text(size: 7pt, fill: faint)[〔#original〕]]
}
