// main-example.typ — 主控文件骨架（复制到书稿目录后按实际章节修改）
// 注意：book.typ 必须位于项目根目录（typst 按模板所在目录解析图片相对路径）
#import "book.typ": *

#cover(
  title: [高并发的哲学原理],
  title-en: [PHILOSOPHICAL PRINCIPLES OF HIGH CONCURRENCY],
  motto: [找出单点，进行拆分],
  author: [吕文翰 著],
  note: [开源版本 · CC BY-NC-ND 4.0],
)
#title-page(
  title: [高并发的哲学原理],
  title-en: [PHILOSOPHICAL PRINCIPLES OF HIGH CONCURRENCY],
  author: [吕文翰 著],
)
#copyright-page[
  本书版权归属于吕文翰，采用 CC BY-NC-ND 4.0 协议开源，仅供免费阅读。
]

#show: book

// 前置部分：罗马数字页码；前言小节不编号
#set page(numbering: "i")
#counter(page).update(1)
#{
  set heading(numbering: none)
  include "ch00-preface.typ"
}

#toc-page()

// 正文部分：重置为阿拉伯页码
#set page(numbering: "1")
#counter(page).update(1)
#part-page([第一部分], [通用设计方法], blurb: [高并发问题的通用设计方法])
#include "ch01.typ"

#part-page([第二部分], [计算资源高并发], blurb: [基础设施并发 · 编程语言性能瓶颈])
#include "ch02.typ"
// ……依此类推

// 附录：小节不编号
#part-page([附 录], [其它系列文章])
#{
  set heading(numbering: none)
  include "app-a.typ"
}
