# 版式参数与排障

## 版式参数（book.typ 顶部集中可调）

| 项 | 默认值 | 说明 |
| --- | --- | --- |
| 纸型 | B5（176mm × 250mm） | `page-w` / `page-h` |
| 页边距 | 上 22mm 下 20mm 内 19mm 外 16mm | 奇偶页镜像 |
| 正文 | Noto Serif CJK SC 10pt，两端对齐，段距 1.1em，行距 0.68em | 块式段落（参照 DDIA 中文版） |
| 节标题 | 章节号 Noto Sans 深蓝 + 标题 Noto Serif | 二/三级自动编号（1.1 / 1.1.1），四级以下不编号 |
| 代码块 | DejaVu Sans Mono 8pt，luma(247) 底，breakable | 长块自动跨页 |
| 行内代码 | 8.6pt 灰底小盒，多词按词分盒可在空格折行 | 避免 CJK 两端对齐撑爆 |
| 主题色 | accent 深蓝 `1a5276`、ink 墨蓝 `14213a`（封面/隔页）、gold 暗金 `c9a054` | |
| 版心宽度 | 176 − 19 − 16 = 141mm ≈ 400pt | md2typ 的 max_pt 参数用它 |

## 页眉页脚逻辑（参照 DDIA）

- 章节首页：无页眉，页码居中放页脚。
- 普通页：页眉左侧 smallcaps 章名（heading supplement）、右侧页码，下加 0.4pt 细线。
- `recto-break()` 强制奇数页起章；自动补出的空白偶数页由 metadata 标记识别，页眉页脚全空。
- 目录页有自己的页眉（"目 录" + 页码），由 `toc-page()` 局部设置。

## 重要结构约定

- **book.typ 必须放项目根目录**：typst 按模板文件所在目录解析 `#image()` 相对路径，放子目录会导致图片找不到。
- 章节文件首行 `#import "book.typ": *`，由转换器自动写入。
- `# 第 N 章 X` 由转换器变成 `#chapter("N", [X])`（自动重置 heading 计数器，节号 N.i 自动生成）；前言/附录的 H1 变成 `#frontchapter([X])`。
- 前言/附录内部小节需无编号：main.typ 中用 `#{ set heading(numbering: none); include "..." }` 作用域包裹。

## 常见排版问题

- **代码行超宽**：raw 块不换行。8pt DejaVu Mono 在 B5 版心约容 79 列；超长行在转换后手工折行或写章节专用后处理脚本（本书第 8 章 hexdump 用 `scripts/fix_ch08.py` 按逗号折行）。
- **图片过宽/过窄**：md2typ 按像素宽度换算（96dpi），封顶 400pt。异常图直接改 `.typ` 里 `#fig("...", Npt, ...)` 的宽度。
- **图片找不到**：见上面"结构约定"第一条；`--root` 必须指向项目根。
- **目录缺条目**：`toc-page()` 里 outline depth=2；要收三级改 depth。
- **标点后多余空格**：模板内置正则 show 规则折叠"中文标点 + ASCII 空格 + 汉字"。

## 转换器行为约定（md2typ.py）

- 只做 `**粗体**` → `*粗体*`；单 `*`、单 `_` 一律字面转义。
- `![..](..)` 独立成段 + 紧随 `<center>图 x-x …</center>` → `#fig` 带图注；`<center>代码清单/表 x-x …</center>` → `#table-caption`（sticky 吸住后续块）。
- `[文字](http…)` → `#link`；书内相对链接 → 纯文字。
- 管道表格 → `#booktable`（三线表 + 斑马纹）。
- `>` 引用块 → `#quoteblock`，末尾 `—— xxx` 行 → `#qattr` 右对齐署名。
- 4 空格缩进且前接空行的连续行 → 代码块（html2text 产物形态）。
- markdown 反斜杠转义（`\.`、`\[` 等）先还原再做 typst 转义。
