---
name: pphc-typst-book
description: 把 markdown 书籍原稿排版成出版级中文 typst 图书并导出 PDF（DDIA 风格版式：设计封面、部分隔页、章节首页、running head、三线表、悬挂目录、图片本地化）。Use when 用户要把 markdown 书稿/系列文章制作成 typst 书籍、导出排版精良的 PDF、设计书籍封面，或提到 pphc/typst 排版/出书。
---

# pphc-typst-book

made by quboliu

将一组 markdown 章节文件排版为中文出版级图书 PDF。版式体系参照 ddia-v2-typest-zh（B5、章节首页、running head、三线表、sticky 标题）。流水线：`md → typst（scripts/md2typ.py）→ 主控 main.typ → typst compile → PDF`。

## 环境要求

- typst ≥ 0.15；Python 3（无第三方依赖）
- 字体：Noto Serif CJK SC（Regular+Bold）、Noto Sans CJK SC、DejaVu Sans Mono

## 快速开始

```bash
# 1. 模板放到项目根目录（typst 按模板文件所在目录解析图片相对路径，必须放根部）
cp templates/book.typ <项目根>/book.typ

# 2. 逐章转换（max_pt = 版心宽度，B5 默认边距下约 400pt）
python3 scripts/md2typ.py images 400 book.typ 第1章.md ch01.typ

# 3. 手写 main.typ（参考 templates/main-example.typ）：
#    cover → title-page → copyright-page → #show: book → 前言(罗马页码) → toc-page
#    → 重置阿拉伯页码 → part-page + 各章 include

# 4. 编译
typst compile --root <项目根> main.typ book.pdf
```

## 工作流程

1. **语料盘点**：grep 确认 md 特性。转换器覆盖：标题/粗体/链接/图片+图注/管道表格/引用块(含 `——` 署名)/围栏与缩进代码块。单 `*`、单 `_`、`$` 一律字面转义。
2. **逐章转换**：每章一个 `.typ`。转换器自动：`# 第 N 章 X` → `#chapter("N",[X])`，其它 H1 → `#frontchapter([X])`，`## N.i X` 节号剥除（typst 自动编号），图片 + 紧随 `<center>图 x-x …</center>` → `#fig(...)` 图注，`<center>代码清单/表 …</center>` → `#table-caption`，管道表格 → `#booktable`（三线表）。
3. **前言/附录**：内部小节不应编号，main.typ 里用作用域包裹：`#{ set heading(numbering: none); include "..." }`。
4. **封面**：`#cover(...)` 内置"单点拆分"节点图 motif；主题色改模板顶部 `ink/gold/accent`。
5. **编译质检循环**：零报错后导出关键页 PNG 目检（封面、目录、章节首页、代码密集页、图片页、表格页），并用脚本扫描文字超出版心的页面（`x1 > 页宽-外边距` 的 word）。发现问题改模板或转换器后重编译。

## 文件

- `scripts/md2typ.py` — markdown → typst 转换器（用法见文件头注释）
- `templates/book.typ` — 版式模板（编译时复制到项目根目录）：cover/title-page/copyright-page/part-page/chapter/frontchapter/toc-page/fig/booktable/table-caption/quoteblock/qattr + book() 全局版式
- `templates/main-example.typ` — main.typ 骨架
- `REFERENCE.md` — 版式参数、页眉页脚逻辑、常见排障
