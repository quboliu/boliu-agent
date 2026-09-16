#import "../bilingual.typ": *
#show: book
#source-cover("Structure proof", "Fixture author", "Test edition")
#boliu-cover("Structure proof", "Fixture author", "Test edition", "Bilingual")
#copyright-page[Copyright and source record. Fixture only.]
#frontchapter([Preface / 前言])[
  == Purpose / 目的
  This unnumbered section must not acquire a chapter number.
]
#toc-page(title: [Contents / 目录])
#part-page([PART I / 第一部分], [Foundations / 基础], blurb: [A quiet divider.])
#chapter("1", "Reading structure")
== A long section title demonstrating hanging alignment in the contents
#quoteblock[Preserve the complete quotation.]
#quoteblock([A quotation with attribution.], attribution: [Original author])
#for i in range(24) [
  #heading(level: 2)[A deliberately long section title for contents wrapping #i]
  A short paragraph for the outline fixture.
]
#frontchapter([Appendix / 附录])[
  == Supplementary material
  This section is unnumbered as well.
]
