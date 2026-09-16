#!/usr/bin/env python3
"""md2typ.py — 把 markdown 书籍章节转换为 typst 标记（配合 book.typ 模板）。

输出文件首行自动带 `#import "<template>": *`，因此章节文件可以直接调用
模板函数（chapter/frontchapter/fig/quoteblock/qattr/booktable/table-caption）。

转换规则：
- `# 第 N 章 X` → #chapter("N", [X])；其它 H1 → #frontchapter([...])
- `## N.i X` 节号前缀自动剥除（编号由 typst 自动生成）；H4+ 不编号
- ``` 围栏代码块、4 空格缩进代码块 → typst 代码块
- **粗体** → *粗体*；单 * 、单 _ 、$ 一律按字面转义
- [链接](url)、<https://autolink> → #link(...)；书内相对链接转纯文字
- 独立图片 + 紧随的 <center>图 x-x ...</center> → #fig(path, width, [caption])
- <center>代码清单/表 x-x ...</center> → #table-caption[...]
- markdown 管道表格 → #booktable(...)（三线表）
- > 引用块 → #quoteblock[...]，末尾 `—— xxx` 署名行 → #qattr[...]
- 图片宽度按像素尺寸换算（96dpi），封顶版心宽度

用法: md2typ.py <images_dir> <版心宽度pt> <模板import路径> <input.md> [output.typ]
"""
import re, struct, sys, os

# ---------- 图片尺寸探测（无第三方依赖） ----------

def png_size(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])

def jpg_size(data):
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        seg = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg
    return None

def image_width_pt(path, max_pt):
    try:
        data = open(path, "rb").read(65536)
        size = png_size(data) or jpg_size(data)
        if not size:
            return max_pt
        return min(size[0] * 0.75, max_pt)  # 96dpi → pt
    except OSError:
        return max_pt

# ---------- 行内元素 ----------

PLACE = "\x00%d\x00"
JUNK_ALT = re.compile(
    r"^([0-9a-f]{8,}|alt\s*text|whiteboard_exported_image|image|[a-z0-9_\-]*\d[\w\-]*\.(jpe?g|png|gif|webp))$",
    re.I,
)

def clean_alt(alt):
    return "" if JUNK_ALT.match(alt.strip()) else alt.strip()

def process_inline(s, images_dir, max_pt, stash=None):
    # stash 在递归调用间共享；占位符合一由最外层调用完成
    top = stash is None
    if top:
        stash = []

    def keep(typ):
        stash.append(typ)
        return PLACE % (len(stash) - 1)

    # 1. 行内代码
    s = re.sub(r"`([^`\n]+)`", lambda m: keep("`" + m.group(1).replace("`", "\\`") + "`"), s)
    # 2. 图片（独立图片在块级阶段才包 fig，这里仅生成 image 调用）
    def img_repl(m):
        alt, url = clean_alt(m.group(1)), m.group(2)
        alt = process_inline(alt, images_dir, max_pt, stash) if alt else ""
        w = image_width_pt(os.path.join(images_dir, os.path.basename(url)), max_pt)
        return keep(f'IMG\x01{url}\x01{w:.0f}\x01{alt}')
    s = re.sub(r"!\[([^]]*)\]\(([^)\s]+)\)", img_repl, s)
    # 3. 链接（允许 <url> 尖括号形式与空文字）
    def link_repl(m):
        text, url = m.group(1), m.group(2).strip("<>")
        if url.startswith("http"):
            if not text.strip():
                return keep(f'#link("{url}")')
            return keep(f'#link("{url}")[{process_inline(text, images_dir, max_pt, stash)}]')
        return keep(process_inline(text, images_dir, max_pt, stash) if text.strip() else "")
    s = re.sub(r"\[([^]]*)\]\(<([^>\s]+)>\)", link_repl, s)          # [t](<url>)
    s = re.sub(r"\[([^]]*)\]\(([^)\s]+)[^)]*\)", link_repl, s)       # [t](url)
    # 4. autolink <http://...>
    s = re.sub(r"<((?:https?|mailto):[^>\s]+)>", lambda m: keep(f'#link("{m.group(1)}")'), s)
    # 4b. 裸 URL（html2text 常把链接转成裸文本）
    def bare_url(m):
        url = m.group(0)
        trail = ""
        while url and url[-1] in "，。、；：）】》!?,.;":
            trail = url[-1] + trail
            url = url[:-1]
        return keep(f'#link("{url}")') + trail
    s = re.sub(r"https?://[^\s<>\]\)）【】「」\"']+", bare_url, s)
    # 5. 粗体
    s = re.sub(r"\*\*([^*]+)\*\*", lambda m: keep("*" + process_inline(m.group(1), images_dir, max_pt, stash) + "*"), s)
    s = re.sub(r"__([^_]+)__", lambda m: keep("*" + process_inline(m.group(1), images_dir, max_pt, stash) + "*"), s)
    # 6. html 实体残留
    for a, b in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'"), ("&copy;", "©"), ("&nbsp;", " ")]:
        s = s.replace(a, b)
    # 7. markdown 反斜杠转义还原
    s = re.sub(r"\\([\\`*_{}\[\]()#+\-.!~<>|])", r"\1", s)
    # 8. typst 特殊字符转义
    s = s.replace("\\", "\\\\")
    for c in "#$@[]*_`~<>":
        s = s.replace(c, "\\" + c)
    # 9. 最外层：循环放回 stash（相邻同 URL 链接去重）
    if top:
        def restore(m):
            item = stash[int(m.group(1))]
            if item.startswith("IMG\x01"):
                _, url, w, alt = item.split("\x01", 3)
                if alt:
                    return f'#fig("{url}", {w}pt, [{alt}])'
                return f'#fig("{url}", {w}pt, none)'
            return item
        while "\x00" in s:
            s = re.sub("\x00(\\d+)\x00", restore, s)
        s = re.sub(r'(#link\("([^"]+)"\))(?:\[\])?(?:\1(?:\[\])?)+', r"\1", s)
    return s

# ---------- 表格 ----------

def convert_table(lines, images_dir, max_pt):
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        rows.append(cells)
    if not rows:
        return ""
    ncols = max(len(r) for r in rows)
    header = ", ".join(f"[*{process_inline(c, images_dir, max_pt)}*]" for c in rows[0])
    body = []
    for r in rows[1:]:
        r += [""] * (ncols - len(r))
        body.append("(" + ", ".join(f"[{process_inline(c, images_dir, max_pt)}]" for c in r) + ",)")
    cols = "(" + ", ".join(["1fr"] * ncols) + ",)"
    return (f"#booktable({cols},\n  ({header},),\n  (\n    " + ",\n    ".join(body) + ",\n  ),\n)")

# ---------- 主流程 ----------

def convert(text, images_dir, max_pt, template):
    lines = text.split("\n")
    out = [f'#import "{template}": *', ""]
    i = 0
    para = []
    h1_done = False

    def flush_para():
        if para:
            out.append(process_inline(" ".join(x.strip() for x in para), images_dir, max_pt))
            para.clear()

    while i < len(lines):
        ln = lines[i]
        # 围栏代码块
        m = re.match(r"^```(\w*)\s*$", ln)
        if m:
            flush_para()
            buf = [ln]
            i += 1
            while i < len(lines) and not re.match(r"^```\s*$", lines[i]):
                buf.append(lines[i])
                i += 1
            buf.append("```")
            out.append("\n".join(buf))
            i += 1
            continue
        # 缩进代码块（4+ 空格，前一行是空行且不在段落中；列表项不算代码）
        if re.match(r"^    \S", ln) and not re.match(r"^\s*([-+*]|\d+[.)])\s", ln) and not para and (i == 0 or lines[i - 1].strip() == ""):
            buf = []
            while i < len(lines) and (re.match(r"^    ", lines[i]) or lines[i].strip() == ""):
                if lines[i].strip() == "" and i + 1 < len(lines) and not re.match(r"^    ", lines[i + 1]):
                    break
                buf.append(lines[i][4:] if lines[i].startswith("    ") else "")
                i += 1
            while buf and buf[-1] == "":
                buf.pop()
            if buf:
                flush_para()
                out.append("```\n" + "\n".join(buf) + "\n```")
                continue
        if ln.strip() == "":
            flush_para()
            i += 1
            continue
        # 表格
        if ln.lstrip().startswith("|"):
            flush_para()
            tbl = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            out.append(convert_table(tbl, images_dir, max_pt))
            continue
        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            flush_para()
            level = len(m.group(1))
            title = m.group(2).strip()
            if level == 1 and not h1_done:
                h1_done = True
                cm = re.match(r"^第\s*(\d+)\s*章[：:\s]\s*(.*)$", title)
                if cm:
                    out.append(f'#chapter("{cm.group(1)}", [{process_inline(cm.group(2), images_dir, max_pt)}])')
                else:
                    out.append(f"#frontchapter([{process_inline(title, images_dir, max_pt)}])")
            else:
                if level == 2:
                    title = re.sub(r"^\d+\.\d+\s+", "", title)  # 剥除节号，由 typst 自动编号
                out.append("=" * level + " " + process_inline(title, images_dir, max_pt))
            i += 1
            continue
        # 引用块
        if re.match(r"^>\s?", ln):
            flush_para()
            buf = []
            while i < len(lines) and re.match(r"^>\s?", lines[i]):
                buf.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            # 末尾署名行（—— xxx / -- xxx）拆为 qattr
            attr = None
            while buf and not buf[-1].strip():
                buf.pop()
            if buf and re.match(r"^\\?(——|--)\s*", buf[-1].strip()):
                attr = re.sub(r"^\\?(——|--)\s*", "", buf.pop().strip())
            # 逐行组装：标题行转粗体、列表行保留结构、其余合成段落
            blocks, para_lines = [], []
            LIST_RE = re.compile(r"^(\s*)([-+*]|\d+[.)])\s+(.*)$")
            for bl in buf:
                s = bl.strip()
                hm = re.match(r"^#{1,6}\s+(.*)$", s)
                lm = LIST_RE.match(bl) if s and not s.startswith("**") else None
                if hm:
                    if para_lines:
                        blocks.append(" ".join(x.strip() for x in para_lines)); para_lines = []
                    blocks.append("**" + hm.group(1) + "**")
                elif lm:
                    if para_lines:
                        blocks.append(" ".join(x.strip() for x in para_lines)); para_lines = []
                    marker = "-" if lm.group(2) in "-+*" else lm.group(2)
                    blocks.append(lm.group(1) + marker + " " + lm.group(3))
                elif s:
                    para_lines.append(bl)
                else:
                    if para_lines:
                        blocks.append(" ".join(x.strip() for x in para_lines)); para_lines = []
            if para_lines:
                blocks.append(" ".join(x.strip() for x in para_lines))
            inner = "\n\n".join(process_inline(b, images_dir, max_pt) for b in blocks)
            q = "#quoteblock[" + inner
            if attr:
                q += "\n\n#qattr[" + process_inline(attr, images_dir, max_pt) + "]"
            out.append(q + "]")
            continue
        # <center> 行
        m = re.match(r"^<center>(.*?)</center>\s*$", ln.strip())
        if m:
            flush_para()
            cap = process_inline(m.group(1), images_dir, max_pt)
            # 紧随图片的“图 x-x”→ 正式图注（替换掉 alt 图注）；代码清单/表 → table-caption
            fm = re.search(r'#fig\("([^"]+)", (\d+)pt(?:, \[[^]]*\]|, none)?\)$', out[-1]) if out else None
            if fm and re.match(r"^图\s*[\d\-]", m.group(1)):
                out[-1] = f'#fig("{fm.group(1)}", {fm.group(2)}pt, [{cap}])'
            elif re.match(r"^(代码清单|表)\s*[\d\-]", m.group(1)):
                out.append(f"#table-caption[{cap}]")
            else:
                out.append(f"#align(center)[#text(size: 9pt, fill: ink-gray)[{cap}]]")
            i += 1
            continue
        # 独立图片行
        if re.fullmatch(r"!\[[^]]*\]\([^)]+\)", ln.strip()):
            flush_para()
            out.append(process_inline(ln.strip(), images_dir, max_pt))
            i += 1
            continue
        # 列表行（-、*、+、1. 标记；星号标记不允许紧跟 * 以免误吃粗体行）
        if re.match(r"^\s*([-+]|\d+[.)])\s", ln) or (re.match(r"^\s*\*\s", ln) and not ln.lstrip().startswith("**")):
            flush_para()
            mm = re.match(r"^(\s*)([-+*]|\d+[.)])\s+(.*)$", ln)
            indent, marker, body = mm.group(1), mm.group(2), mm.group(3)
            tmarker = "-" if marker in "-+*" else marker
            out.append(indent + tmarker + " " + process_inline(body, images_dir, max_pt))
            i += 1
            continue
        para.append(ln)
        i += 1
    flush_para()
    return "\n\n".join(x for x in out if x.strip()) + "\n"

def main():
    images_dir, max_pt, template = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    src = open(sys.argv[4], encoding="utf-8").read()
    result = convert(src, images_dir, max_pt, template)
    if len(sys.argv) > 5:
        open(sys.argv[5], "w", encoding="utf-8").write(result)
    else:
        sys.stdout.write(result)

if __name__ == "__main__":
    main()
