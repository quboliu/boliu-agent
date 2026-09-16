// book.typ — 中文技术书籍排版模板（pphc-typst-book skill）
// 设计参照 ddia-v2-typest-zh：B5 纸型、章节首页、running head、三线表、
// 悬挂式目录、行间代码分盒、sticky 标题块、recto 空白页抑制页眉页脚。
// 适用：typst 0.15+，无外部包依赖。
// 章节文件首行需 #import "templates/book.typ": *（相对路径按实际调整）。

// ── 字体与色彩 ──────────────────────────────────────────────
#let serif = "Noto Serif CJK SC"
#let sans = "Noto Sans CJK SC"
#let mono = ("DejaVu Sans Mono", "Noto Sans CJK SC")

#let accent = rgb("1a5276")       // 深蓝：章节号/标题/链接
#let accent-warm = rgb("9c4a00")  // 暖棕
#let ink = rgb("14213a")          // 墨蓝：封面/部分隔页底色
#let gold = rgb("c9a054")         // 暗金：封面点缀
#let ink-gray = luma(70)
#let faint = luma(120)

#let body-size = 10pt

// B5
#let page-w = 176mm
#let page-h = 250mm
#let text-width = 400pt           // 版心宽度近似值，供图片换算

// ── recto 过渡标记：自动补出的空白偶数页不显示页眉页脚 ──────
#let recto-break() = {
  metadata("recto-break")
  pagebreak(to: "odd")
}

#let on-auto-verso(current-page) = {
  let markers = query(metadata.where(value: "recto-break")).filter(
    m => m.location().page() <= current-page,
  )
  if markers.len() == 0 { return false }
  let marker = markers.last()
  let marker-page = marker.location().page()
  let marker-at-top = marker.location().position().y <= 23mm
  let l1 = selector(heading.where(level: 1))
  let after = query(l1).filter(
    h => h.location().page() > marker-page or (
      h.location().page() == marker-page and
      h.location().position().y > marker.location().position().y
    ),
  )
  if after.len() == 0 { return false }
  let heading-page = after.first().location().page()
  (marker-page < current-page and current-page < heading-page) or (
    marker-page == current-page and marker-at-top
  )
}

// ── 行内代码：多词代码按词分盒，允许在空格处折行 ────────────
#let inline-code(it) = {
  let code-box(body) = box(
    fill: luma(243),
    outset: (x: 2.5pt),
    radius: 2pt,
    text(font: mono, size: 8.6pt, hyphenate: false, body),
  )
  if not it.text.contains(" ") {
    code-box(it)
  } else {
    set smartquote(enabled: false)
    for (i, word) in it.text.split(" ").enumerate() {
      if i > 0 { text(font: mono, size: 8.6pt, " ") }
      code-box(word)
    }
  }
}

// ── 图片 ────────────────────────────────────────────────────
#let fig(path, width, caption) = {
  v(0.8em)
  block(breakable: false)[
    #align(center)[
      #image(path, width: width)
      #if caption != none [
        #v(4pt)
        #block(width: 92%)[
          #set text(size: 8.5pt, fill: ink-gray)
          #set par(justify: false)
          #align(center, caption)
        ]
      ]
    ]
  ]
  v(0.8em)
}

// ── 代码清单 / 表格标题（吸住后续块） ───────────────────────
#let table-caption(body) = block(width: 100%, sticky: true, above: 0.6em, below: 0.3em)[
  #align(center, text(size: 8.5pt, fill: ink-gray, body))
]

// ── 三线表 ──────────────────────────────────────────────────
#let booktable(cols, header-cells, body-cells) = {
  v(0.6em)
  set text(size: 9pt)
  align(center, table(
    columns: cols,
    stroke: none,
    inset: (x: 6pt, y: 5pt),
    align: left,
    fill: (x, y) => if y > 0 and calc.even(y) { luma(248) },
    table.hline(stroke: 1pt + luma(120)),
    table.header(..header-cells),
    table.hline(stroke: 0.6pt + luma(120)),
    ..body-cells.flatten(),
    table.hline(stroke: 1pt + luma(120)),
  ))
  v(0.6em)
}

// ── 引用块与署名 ────────────────────────────────────────────
#let quoteblock(body) = block(
  inset: (left: 14pt, right: 8pt),
  above: 0.9em,
  below: 0.9em,
  breakable: true,
)[
  #set text(fill: ink-gray)
  #body
]

#let qattr(body) = {
  v(2pt)
  align(right, text(size: 9.5pt, fill: faint)[—— #body])
}

// ── 章节首页 ────────────────────────────────────────────────
#let chapter(num, title) = {
  recto-break()
  counter(heading).update((int(num) - 1,))
  v(30mm)
  text(font: sans, size: 12pt, weight: "bold", fill: accent, tracking: 0.2em)[第 #num 章]
  v(2mm)
  heading(level: 1, numbering: n => [第 #num 章], supplement: [第 #num 章 #title])[#title]
  v(3mm)
  line(length: 100%, stroke: 1.2pt + accent)
  v(10mm)
}

#let frontchapter(title) = {
  recto-break()
  v(30mm)
  heading(level: 1, numbering: none, supplement: title)[#title]
  v(3mm)
  line(length: 100%, stroke: 1.2pt + accent)
  v(10mm)
}

// ── 部分隔页（深色满版） ────────────────────────────────────
#let part-page(num, title, blurb: []) = {
  recto-break()
  page(width: page-w, height: page-h, margin: 0mm, fill: ink, header: none, footer: none)[
    #align(center + horizon)[
      #text(font: sans, size: 13pt, fill: gold, tracking: 0.5em, num)
      #v(8mm)
      #rect(width: 30mm, height: 0.7pt, fill: gold, stroke: none)
      #v(8mm)
      #text(font: serif, size: 30pt, weight: "bold", fill: rgb("fffdf8"), tracking: 0.1em, title)
      #v(10mm)
      #text(font: sans, size: 10pt, fill: rgb("aab3c5"), blurb)
    ]
  ]
}

// ── 单点拆分 motif（封面装饰） ──────────────────────────────
#let split-diagram() = box(width: page-w, height: 78mm, {
  let a = (28mm, 39mm)
  let bs = ((82mm, 12mm), (82mm, 39mm), (82mm, 66mm))
  let ys = range(9).map(i => 5.5mm + i * 8.5mm)
  for b in bs {
    place(line(start: a, end: b, stroke: 0.7pt + gold))
  }
  for (j, b) in bs.enumerate() {
    for k in range(3) {
      place(line(start: b, end: (140mm, ys.at(j * 3 + k)), stroke: 0.5pt + rgb("7a6a48")))
    }
  }
  place(dx: a.at(0) - 4.2mm, dy: a.at(1) - 4.2mm, circle(radius: 4.2mm, fill: gold))
  for b in bs {
    place(dx: b.at(0) - 2.6mm, dy: b.at(1) - 2.6mm, circle(radius: 2.6mm, fill: ink, stroke: 1.1pt + gold))
  }
  for y in ys {
    place(dx: 140mm - 1.5mm, dy: y - 1.5mm, circle(radius: 1.5mm, fill: rgb("e8dcc0"), stroke: none))
  }
})

// ── 封面 ────────────────────────────────────────────────────
#let cover(title: [], title-en: [], motto: [], author: [], note: []) = {
  page(width: page-w, height: page-h, margin: 0mm, fill: ink, header: none, footer: none)[
    #place(top + left, dx: 9mm, dy: 9mm,
      rect(width: page-w - 18mm, height: page-h - 18mm, stroke: 0.6pt + gold, fill: none))
    #align(center)[
      #v(18mm)
      #text(font: sans, size: 8.5pt, fill: gold, tracking: 0.16em, title-en)
      #v(3mm)
      #split-diagram()
      #v(1mm)
      #text(font: serif, size: 38pt, weight: "bold", fill: rgb("fffdf8"), tracking: 0.06em, title)
      #v(5mm)
      #rect(width: 40mm, height: 0.8pt, fill: gold, stroke: none)
      #v(5mm)
      #text(font: sans, size: 11.5pt, fill: rgb("d9cfae"), tracking: 0.35em, motto)
      #v(1fr)
      #text(font: serif, size: 13.5pt, fill: rgb("fffdf8"), tracking: 0.2em, author)
      #v(3mm)
      #text(font: sans, size: 8.5pt, fill: rgb("9aa3b8"), note)
      #v(14mm)
    ]
  ]
}

// ── 扉页（浅色极简） ────────────────────────────────────────
#let title-page(title: [], title-en: [], author: []) = {
  page(width: page-w, height: page-h, header: none, footer: none)[
    #v(40mm)
    #grid(
      columns: (7pt, 1fr),
      gutter: 13pt,
      [#rect(width: 5pt, height: 60mm, fill: accent)],
      [
        #text(font: sans, size: 8.5pt, weight: "bold", fill: accent, tracking: 0.16em, title-en)
        #v(8mm)
        #text(font: serif, size: 25pt, weight: "bold", fill: accent.darken(15%), hyphenate: false, title)
        #v(10mm)
        #text(font: serif, size: 11pt, fill: ink-gray, author)
      ],
    )
  ]
}

// ── 版权页 ──────────────────────────────────────────────────
#let copyright-page(body) = {
  page(width: page-w, height: page-h,
    margin: (inside: 19mm, outside: 16mm, top: 22mm, bottom: 20mm),
    header: none, footer: none)[
    #v(1fr)
    #set text(size: 8.5pt, fill: rgb("555555"))
    #set par(leading: 0.9em)
    #body
    #v(12mm)
  ]
}

// ── 目录页 ──────────────────────────────────────────────────
#let toc-page() = {
  pagebreak(weak: true, to: "odd")
  set page(header: context {
    set text(font: sans, size: 8pt, fill: faint)
    grid(columns: (1fr, auto), gutter: 12pt,
      [目 录], [#counter(page).display()])
    v(3pt)
    line(length: 100%, stroke: 0.4pt + luma(200))
  })
  text(font: serif, size: 22pt, weight: "bold")[目 录]
  v(8mm)
  outline(title: none, depth: 2, indent: auto)
}

// ── 全书版式 ────────────────────────────────────────────────
#let book(body) = {
  set page(
    width: page-w,
    height: page-h,
    margin: (top: 22mm, bottom: 20mm, inside: 19mm, outside: 16mm),
    header: context {
      let current-page = here().page()
      let onpage = query(heading.where(level: 1)).filter(
        h => h.location().page() == current-page,
      )
      if onpage.len() > 0 { return }
      if on-auto-verso(current-page) { return }
      let hs = query(heading.where(level: 1)).filter(
        h => h.location().page() < current-page,
      )
      if hs.len() == 0 { return }
      let h = hs.last()
      let running = if h.supplement == none { h.body } else { h.supplement }
      set text(font: sans, size: 8pt, fill: faint)
      grid(
        columns: (1fr, auto),
        gutter: 12pt,
        [#smallcaps[#running]],
        [#counter(page).display()],
      )
      v(3pt)
      line(length: 100%, stroke: 0.4pt + luma(200))
    },
    footer: context {
      let current-page = here().page()
      let onpage = query(heading.where(level: 1)).filter(
        h => h.location().page() == current-page,
      )
      if onpage.len() > 0 {
        return align(center, text(size: 8.5pt, fill: faint, counter(page).display()))
      }
      if on-auto-verso(current-page) { return }
    },
  )
  set text(font: serif, size: body-size, lang: "zh", region: "cn")
  set par(justify: true, leading: 0.68em, spacing: 1.1em)
  set heading(numbering: "1.1")
  show heading: set block(sticky: true)
  show link: set text(fill: accent)

  // 中文标点后紧跟的 ASCII 空格折叠
  show regex("([，。！？；：、）》】」』])\\s+([\\p{Han}])"): it => (
    it.text.replace(regex("\\s+"), "")
  )

  // 代码
  show raw.where(block: true): it => block(
    fill: luma(247),
    inset: (x: 9pt, y: 7pt),
    radius: 3pt,
    width: 100%,
    breakable: true,
    text(font: mono, size: 8pt, it),
  )
  show raw.where(block: false): inline-code

  // 标题层级
  show heading.where(level: 1): it => block(sticky: true)[
    #set par(justify: false)
    #text(font: serif, size: 22pt, weight: "bold", hyphenate: false, it.body)
  ]
  show heading.where(level: 2): it => block(sticky: true)[
    #set par(justify: false)
    #v(1.8em, weak: true)
    #if it.numbering == none {
      text(font: serif, size: 13pt, weight: "bold", fill: accent.darken(10%), it.body)
    } else {
      grid(
        columns: (auto, 1fr),
        gutter: 0.6em,
        align: (left, top),
        text(font: sans, size: 13pt, weight: "bold", fill: accent.darken(10%),
          counter(heading).display("1.1")),
        text(font: serif, size: 13pt, weight: "bold", fill: accent.darken(10%), it.body),
      )
    }
    #v(1.05em)
  ]
  show heading.where(level: 3): it => block(sticky: true)[
    #set par(justify: false)
    #v(1.3em, weak: true)
    #if it.numbering == none {
      text(font: serif, size: 11pt, weight: "bold", it.body)
    } else {
      grid(
        columns: (auto, 1fr),
        gutter: 0.6em,
        align: (left, top),
        text(font: sans, size: 11pt, weight: "bold", fill: accent,
          counter(heading).display("1.1.1")),
        text(font: serif, size: 11pt, weight: "bold", it.body),
      )
    }
    #v(0.65em)
  ]
  show heading.where(level: 4): it => block(sticky: true)[
    #set par(justify: false)
    #v(1em, weak: true)
    #text(font: serif, size: 10.5pt, weight: "bold", style: "italic", it.body)
    #v(0.5em)
  ]
  show heading.where(level: 5): it => block(sticky: true)[
    #set par(justify: false)
    #v(0.8em, weak: true)
    #text(font: sans, size: 10pt, weight: "bold", fill: rgb("444444"), it.body)
    #v(0.4em)
  ]

  // 四级及以下不编号
  show heading.where(level: 4): set heading(numbering: none)
  show heading.where(level: 5): set heading(numbering: none)

  // 目录条目：悬挂编号列
  show outline.entry.where(level: 1): it => block(
    width: 100%, above: 12pt, below: 6pt, breakable: false,
  )[
    #strong(link(it.element.location(), text(fill: luma(0))[
      #if it.element.numbering != none [#it.prefix() #h(0.55em)]#it.inner()
    ]))
  ]
  show outline.entry.where(level: 2): it => block(
    width: 100%, above: 2pt, below: 8pt, breakable: false,
  )[
    #link(it.element.location(), text(font: sans, size: 9pt, fill: accent.darken(15%))[
      #pad(left: 12pt)[
        #grid(
          columns: (23pt, 1fr),
          gutter: 4pt,
          align: (left, top),
          if it.element.numbering == none { [] } else { it.prefix() },
          it.inner(),
        )
      ]
    ])
  ]

  body
}
