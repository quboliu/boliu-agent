// User-approved classic painting replaces the historical line-art house default.
#let boliu-cover(title, author, source-version, edition, artwork: none, artwork-credit: none, bilingual: false) = {
  page-role("front")
  set page(header: none, footer: none)
  set text(hyphenate: false)
  set par(justify: false, spacing: 0pt, leading: 0.4em)
  cover-export-stamp()
  let upper(title-size) = {
    v(3mm)
    text(font: ("Libertinus Serif", "Noto Serif CJK SC"), size: title-size, weight: "bold", fill: black)[#if text.lang == "zh" [系统性能] else [Systems Performance]]
    v(2mm)
    text(font: ("Libertinus Serif", "Noto Serif CJK SC"), size: 17pt, fill: ink-gray)[#if text.lang == "zh" [企业与云计算] else [Enterprise and the Cloud]]
    if bilingual {
      v(3mm)
      text(font: "Noto Serif CJK SC", size: 10.5pt, fill: ink-gray, lang: "zh")[系统性能：企业与云计算]
    }
    v(5mm)
    text(font: "Libertinus Serif", size: 11pt, fill: ink-gray)[#author]
    v(2mm)
    text(font: display-face, size: 7pt, tracking: 0.1em, fill: faint)[SECOND EDITION]
    v(8mm)
    align(center, image(artwork, width: 100%, height: 112mm, fit: "contain"))
    v(3mm)
    text(font: "Libertinus Serif", size: 7.5pt, fill: faint)[Claude Monet · The Japanese Footbridge · 1899]
  }
  let lower = {
    text(font: display-face, size: 8pt, fill: ink-gray)[#edition]
    v(2mm)
    text(font: "Libertinus Serif", size: 7pt, fill: faint)[Courtesy National Gallery of Art, Washington · CC0]
    v(4mm)
    align(center, move(dx: 1.5mm, text(font: display-face, size: 9pt, tracking: 0.14em, fill: accent)[伯流出版社]))
  }
  fitted-cover(upper, (28pt, 26pt, 24pt, 22pt), bottom: lower)
}
