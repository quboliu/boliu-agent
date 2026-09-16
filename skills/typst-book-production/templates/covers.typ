// The first two physical pages. Supply assets and documented provenance in the
// project contract before release; the publisher artwork placeholder is a hard
// release blocker.

#import "core.typ": accent, display-face, faint

#let source-cover(title, author, source-version, original-cover: none) = {
  set page(header: none, footer: none)
  if original-cover != none {
    align(center + horizon)[#image(original-cover, width: 100%, height: 100%, fit: "contain")]
  } else {
    v(34mm)
    align(center)[
      #text(font: display-face, size: 9pt, weight: "bold", fill: accent, tracking: 0.14em)[SOURCE EDITION]
      #v(18mm)
      #text(font: display-face, size: 27pt, weight: "bold", fill: accent.darken(15%))[#title]
      #v(12mm)
      #text(size: 12pt)[#author]
      #v(7mm)
      #text(size: 9pt, fill: faint)[#source-version]
    ]
  }
  pagebreak()
}

#let boliu-cover(title, author, source-version, edition, artwork: none, artwork-credit: none) = {
  set page(header: none, footer: none)
  v(18mm)
  text(font: display-face, size: 9pt, weight: "bold", fill: accent, tracking: 0.16em)[伯流出版社]
  v(8mm)
  line(length: 100%, stroke: 1.2pt + accent)
  v(13mm)
  text(font: display-face, size: 24pt, weight: "bold", fill: accent.darken(15%))[#title]
  v(5mm)
  text(size: 11pt)[#author]
  v(8mm)
  text(font: display-face, size: 8.5pt, fill: faint)[#edition]
  v(7mm)
  if artwork == none {
    block(width: 100%, height: 83mm, fill: luma(245), inset: 10pt)[
      #align(center + horizon)[
        #text(font: display-face, size: 10pt, weight: "bold", fill: accent)[HISTORICAL LINE ART REQUIRED]
        #v(4pt)
        #text(size: 8.5pt, fill: faint)[NOT FOR RELEASE]
      ]
    ]
  } else {
    align(center)[#image(artwork, width: 68%, height: 83mm, fit: "contain")]
  }
  v(1fr)
  line(length: 100%, stroke: 0.6pt + luma(190))
  v(4mm)
  text(size: 8.5pt, fill: faint)[#source-version]
  if artwork-credit != none { v(2pt); text(size: 7.5pt, fill: faint)[#artwork-credit] }
  // The next chapter/front-matter block owns the next page transition.
}
