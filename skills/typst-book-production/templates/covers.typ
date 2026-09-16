// The first two physical pages. Supply assets and documented provenance in the
// project contract before release; the publisher artwork placeholder is a hard
// release blocker.

#import "core.typ": accent, display-face, faint, page-role

// Test the whole composition at finite width before emitting one full page.
// Exhausting the reviewed type scale is an error, never a spill or tiny title.
#let fitted-cover(top, sizes, bottom: []) = layout(size => {
  set text(hyphenate: false)
  set par(justify: false)
  for title-size in sizes {
    let upper = top(title-size)
    let natural = measure(block(width: 100%)[#upper #v(6mm) #bottom], width: size.width)
    if natural.height <= size.height {
      return block(width: 100%, height: size.height, breakable: false)[
        #upper
        #v(1fr)
        #bottom
      ]
    }
  }
  panic("Cover exceeds one page; supply a reviewed cover layout instead of overflowing")
})

#let source-cover(title, author, source-version, original-cover: none) = {
  page-role("front")
  set page(header: none, footer: none)
  set text(hyphenate: false)
  set par(justify: false)
  if original-cover != none {
    align(center + horizon)[#image(original-cover, width: 100%, height: 100%, fit: "contain")]
  } else {
    fitted-cover(title-size => [
      #v(34mm)
      #align(center)[
      #text(font: display-face, size: 9pt, weight: "bold", fill: accent, tracking: 0.14em)[SOURCE EDITION]
      #v(18mm)
      #text(font: display-face, size: title-size, weight: "bold", fill: accent.darken(15%))[#title]
      #v(12mm)
      #text(size: 12pt)[#author]
      #v(7mm)
      #text(size: 9pt, fill: faint)[#source-version]
      ]
    ], (27pt, 24pt, 22pt, 20pt))
  }
  pagebreak()
}

#let boliu-cover(title, author, source-version, edition, artwork: none, artwork-credit: none) = {
  page-role("front")
  set page(header: none, footer: none)
  set text(hyphenate: false)
  set par(justify: false)
  let upper(title-size) = {
  let compact = title-size < 24pt
  let art-height = if compact { 70mm } else { 83mm }
  v(if compact { 12mm } else { 18mm })
  text(font: display-face, size: 9pt, weight: "bold", fill: accent, tracking: 0.16em)[伯流出版社]
  v(if compact { 5mm } else { 8mm })
  line(length: 100%, stroke: 1.2pt + accent)
  v(if compact { 8mm } else { 13mm })
  text(font: display-face, size: title-size, weight: "bold", fill: accent.darken(15%))[#title]
  v(5mm)
  text(size: 11pt)[#author]
  v(if compact { 5mm } else { 8mm })
  text(font: display-face, size: 8.5pt, fill: faint)[#edition]
  v(if compact { 5mm } else { 7mm })
  if artwork == none {
    block(width: 100%, height: art-height, fill: luma(245), inset: 10pt)[
      #align(center + horizon)[
        #text(font: display-face, size: 10pt, weight: "bold", fill: accent)[HISTORICAL LINE ART REQUIRED]
        #v(4pt)
        #text(size: 8.5pt, fill: faint)[NOT FOR RELEASE]
      ]
    ]
  } else {
    align(center)[#image(artwork, width: 68%, height: art-height, fit: "contain")]
  }
  }
  let lower = {
  line(length: 100%, stroke: 0.6pt + luma(190))
  v(4mm)
  text(size: 8.5pt, fill: faint)[#source-version]
  if artwork-credit != none { v(2pt); text(size: 7.5pt, fill: faint)[#artwork-credit] }
  }
  fitted-cover(upper, (24pt, 22pt, 20pt, 18pt), bottom: lower)
  // The next chapter/front-matter block owns the next page transition.
}
