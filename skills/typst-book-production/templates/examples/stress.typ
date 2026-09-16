#import "../bilingual.typ": *
#show: book

// Native vector test artwork, deliberately not a historical cover asset.
#source-cover("Production proof", "Fixture author", "Layout fixture only",
  original-cover: if sys.inputs.at("original", default: "false") == "true" {
    "/examples/cover-fixture.svg"
  } else { none })
#boliu-cover("Production proof", "Fixture author", "Layout fixture only", "Proof")
#chapter("1", "Paragraphs and notation", running: "Paragraphs and notation")
#dual[
  A paragraph begins at the left edge. This proof checks the rhythm of multiple
  paragraphs and the transition between languages. #lorem(40)

  Another paragraph begins at the same left edge. #lorem(40)
][
  正文每一段都从版心左边开始。段落间距承担分段作用，保持全书一致的阅读节奏。
  标点应自然换行，不应在中文内部插入多余空格。

  第二段仍然没有首行缩进。中英文保持相同字号，双语内容相邻排列。
]
#dual-heading(2, "Code and mathematical expressions", "代码与数学公式")
Inline code: `request timeout identifier`. Native math $x_i^2 + y_i^2$.

```python
def total(values):
    # preserve indentation and literal symbols
    return sum(values)
```

#display-equation($ sum_(i=1)^n i = (n(n+1))/2 $) <eq-sum>
See @eq-sum. #footnote[Footnote typography remains independent of body size.]
#dual-footnote[One shared bilingual note.][一条共享的双语脚注。]
#book-note[Short editorial note without a colored panel.]
#dual-note[Shared bilingual note.][中英文说明保留在同一容器内。]

#for i in range(5) [
  #lorem(95)

]
#chapter("2", "Tables and illustrations", running: "Tables and illustrations")
#dual-heading(2, "A deliberately long heading that wraps while its number remains separate", "长标题换行与编号对齐测试")
#table-caption[Table 2.1. A repeating header and a restrained three-rule structure.]
#book-table((1fr, 3fr), header: ([Key], [Description]),
  ..range(35).map(i => ([#i], [A measured row with readable content.])).flatten())

#figure(
  rect(width: 80%, height: 30mm, stroke: 0.5pt)[#align(center + horizon)[Vector fixture]],
  caption: dual-caption("A native vector fixture.", "原生矢量示例。"),
) <fig-proof>
See @fig-proof.

#chapter("3", "Final chapter", running: "Final chapter")
== Final section
This section must be numbered 3.1 and the chapter must start on an odd page.

#chapter("4", "Blank verso proof", running: "Blank verso proof")
== Final check
The previous automatic verso must be entirely blank, without a running head.
