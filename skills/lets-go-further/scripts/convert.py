#!/usr/bin/env python3
"""Recover the supplied EPUBs into Markdown and three Typst editions."""

from __future__ import annotations

import argparse
import copy
import hashlib
import html as html_std
import json
import re
import shutil
import struct
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

from lxml import etree, html


TITLE = "Let's Go Further"
AUTHOR = "Alex Edwards"
ENGLISH_RAW = "Let's Go Further.epub"
DUAL_RAW = "Let's Go Further-dual.epub"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def png_size(data: bytes) -> tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("expected PNG data")
    return struct.unpack(">II", data[16:24])


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_inline(value: str) -> str:
    return re.sub(r"\s+", " ", value)


def typst_string(value: str) -> str:
    value = value.replace("\\", "\\\\").replace('"', '\\"')
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    value = value.replace("\n", "\\n").replace("\t", "\\t")
    return f'"{value}"'


def typst_escape(value: str) -> str:
    value = value.replace("\\", "\\\\")
    value = value.replace("#", "\\#")
    value = value.replace("[", "\\[").replace("]", "\\]")
    value = value.replace("$", "\\$")
    value = value.replace("@", "\\@")
    value = value.replace("*", "\\*").replace("_", "\\_")
    value = value.replace("//", '#text("/")#text("/")')
    return value


def typst_inline_text(value: str) -> str:
    value = normalize_inline(value)
    parts = re.split(r"(`[^`]*`)", value)
    output: list[str] = []
    for part in parts:
        if len(part) >= 2 and part.startswith("`") and part.endswith("`"):
            output.append(f"#raw({typst_string(part[1:-1])})")
        else:
            output.append(typst_escape(part))
    return "".join(output)


def md_escape(value: str) -> str:
    value = value.replace("\\", "\\\\")
    value = value.replace("[", "\\[").replace("]", "\\]")
    return value


def is_translation(node) -> bool:
    return node.tag == "span" and node.get("lang") == "zh-CN"


def translation_inner(node):
    inner = node.xpath('.//span[contains(@class, "immersive-translate-target-inner")]')
    return inner[0] if inner else node


def has_translation(node) -> bool:
    return bool(node.xpath('.//span[@lang="zh-CN"]'))


def clean_translation_wrapper(node):
    """Return an unwrapped translation node with layout-only brs removed."""
    result = copy.deepcopy(translation_inner(node))
    for br in result.xpath('.//br'):
        parent = br.getparent()
        if parent is not None:
            parent.remove(br)
    # Immersive Translate sometimes leaves Markdown backticks around XHTML
    # <code> nodes. The code node already carries the semantic mark; retaining
    # those delimiters would make Typst render generated #raw(...) source text.
    for item in [result, *result.iter()]:
        if item.text:
            item.text = item.text.replace("`", "")
        if item.tail:
            item.tail = item.tail.replace("`", "")
    return result


def node_text(node) -> str:
    return "".join(node.itertext())


def direct_children(node):
    return list(node)


def inline_markdown(node, language: str = "en") -> str:
    """Render an XHTML inline tree as the local, readable Markdown dialect."""
    if node.tag is html.HtmlComment:
        return ""
    if is_translation(node):
        if language == "en":
            return ""
        return inline_markdown(clean_translation_wrapper(node), "zh")
    if node.tag == "code":
        return "`" + node_text(node).replace("`", "\\`") + "`"
    if node.tag == "br":
        return "  \n"
    if node.tag == "a":
        label = inline_markdown_children(node, language)
        href = node.get("href", "")
        return f"[{label}]({href})"
    content = inline_markdown_children(node, language)
    if node.tag in {"em", "i"}:
        return f"*{content}*"
    if node.tag in {"strong", "b"}:
        return f"**{content}**"
    if node.tag == "sup":
        return "[^fn-dagger]" if normalize_space(node_text(node)) == "†" else f"^{content}"
    return content


def inline_markdown_children(node, language: str) -> str:
    chunks: list[str] = []
    if node.text:
        chunks.append(md_escape(normalize_inline(node.text)))
    for child in direct_children(node):
        chunks.append(inline_markdown(child, language))
        if child.tail:
            chunks.append(md_escape(normalize_inline(child.tail)))
    return "".join(chunks)


def inline_typst(node, language: str, footnote_defs: dict[str, str]) -> str:
    if is_translation(node):
        if language == "en":
            return ""
        return inline_typst(clean_translation_wrapper(node), "zh", footnote_defs)
    if node.tag == "code":
        return f"#raw({typst_string(node_text(node))})"
    if node.tag == "br":
        return "#linebreak()"
    if node.tag == "a":
        content = inline_typst_children(node, language, footnote_defs)
        href = node.get("href", "")
        return f"#link({typst_string(href)})[{content}]"
    if node.tag == "sup":
        if normalize_space(node_text(node)) == "†":
            return footnote_defs.get("fn-dagger", "#footnote[]")
        return f"#super[{inline_typst_children(node, language, footnote_defs)}]"
    content = inline_typst_children(node, language, footnote_defs)
    if node.tag in {"em", "i"}:
        return f"#emph[{content}]"
    if node.tag in {"strong", "b"}:
        return f"#strong[{content}]"
    return content


def inline_typst_children(node, language: str, footnote_defs: dict[str, str]) -> str:
    chunks: list[str] = []
    if node.text:
        chunks.append(typst_inline_text(node.text))
    for child in direct_children(node):
        if is_translation(child) and language == "en":
            pass
        else:
            chunks.append(inline_typst(child, language, footnote_defs))
        if child.tail and not (is_translation(child) and language == "en"):
            chunks.append(typst_inline_text(child.tail))
    return "".join(chunks)


def pair_inline(node, footnote_defs: dict[str, str], mode: str = "en") -> tuple[str, str]:
    en = inline_typst(node, "en", footnote_defs)
    if has_translation(node):
        wrapper = node.xpath('.//span[@lang="zh-CN"]')[0]
        chinese = clean_translation_wrapper(wrapper)
        english_source = copy.deepcopy(node)
        for translated in english_source.xpath('.//span[@lang="zh-CN"]'):
            parent = translated.getparent()
            if parent is not None:
                parent.remove(translated)
        source_marks = sum(1 for marker in english_source.xpath('.//sup') if normalize_space(node_text(marker)) == "†")
        translation_marks = sum(1 for marker in chinese.xpath('.//sup') if normalize_space(node_text(marker)) == "†")
        if mode == "dual":
            for marker in list(chinese.xpath('.//sup')):
                if normalize_space(node_text(marker)) != "†":
                    continue
                parent = marker.getparent()
                if parent is None:
                    continue
                tail = marker.tail or ""
                previous = marker.getprevious()
                if previous is not None:
                    previous.tail = (previous.tail or "") + tail
                else:
                    parent.text = (parent.text or "") + tail
                parent.remove(marker)
        elif mode == "zh":
            for _ in range(max(0, source_marks - translation_marks)):
                marker = etree.Element("sup")
                marker.text = "†"
                chinese.append(marker)
        zh = inline_typst(chinese, "zh", footnote_defs)
        if mode != "en":
            zh = correct_translation(zh, normalize_space(node_text(english_source)))
    else:
        zh = en
    return en, zh


def correct_translation(zh: str, source_text: str) -> str:
    """Fix verified translation defects while preserving the EPUB as authority."""
    replacements = (
        ("您", "你"),
        ("恐慌", "panic"),
        ("处理程序", "处理器"),
        ("速率限制器", "限流器"),
        ("速率限制", "限流"),
        ("协程", "goroutine"),
        ("家目录", "主目录"),
        ("MarshalJSON接口", "json.Marshaler 接口"),
        ("go version 命令", '#raw("go version") 命令'),
        ("打开 main.go 文件", '打开 #raw("cmd/api/main.go") 文件'),
        ("curl 工具", '#raw("curl") 工具'),
        ("Allow 头部", '#raw("Allow") 头部'),
        ("Allow 标头", '#raw("Allow") 标头'),
    )
    for old, new in replacements:
        zh = zh.replace(old, new)

    # These paragraphs contain semantic mistranslations, so replacing a single
    # term would leave a technically incorrect sentence behind.
    raw = lambda value: f"#raw({typst_string(value)})"
    if "We can see here that the CreatedAt struct field" in source_text:
        zh = (
            "这里我们可以看到 " + raw("CreatedAt") +
            " 结构体字段完全没有出现在 JSON 中，" + raw("Year") +
            " 字段（其值为 " + raw("0") + "）也没有出现，这是因为 " +
            raw("omitzero") + " 指令。我们对 " + raw("Runtime") +
            " 和 " + raw("Genres") + " 使用的 " + raw("omitzero") +
            " 指令不受影响。"
        )
    elif "You can also prevent a struct field from appearing" in source_text:
        zh = (
            "你也可以通过将结构体字段设为非导出来阻止其出现在 JSON 输出中。"
            "但使用 " + raw('json:"-"') +
            " 结构体标签通常是更好的选择：它既向 Go 语言也向代码的未来阅读者明确表明你不希望该字段包含在 JSON 中，"
            "还能避免将来有人在不了解后果的情况下将字段改为导出而引发问题。"
        )
    elif "The omitzero and omitempty struct tag directives do not have any effect" in source_text:
        zh = raw("omitzero") + " 和 " + raw("omitempty") + " 结构体标签指令不会对 JSON 解码行为产生任何影响。"
    elif "using the omitzero and omitempty struct tag directives" in source_text:
        zh = "通过使用 " + raw("omitzero") + " 和 " + raw("-") + " 结构体标签指令，还可以控制 JSON 中各个结构体字段的可见性。"
    elif "In contrast, the omitzero directive hides" in source_text:
        zh = "相比之下，" + raw("omitzero") + " 指令仅在字段值为该字段类型的零值时，才会在 JSON 输出中隐藏该字段。提醒一下，以下是可编码为 JSON 的 Go 类型的零值："
    elif "If you want to use omitzero and not change" in source_text:
        zh = "如果你想使用 " + raw("omitzero") + " 且不改变键名，可以在结构体标签中留空——像这样：" + raw('json:",omitzero"') + "。注意开头的逗号仍然是必需的。"
    elif "making a POST request to" in source_text and "/v1/healthcheck" in source_text:
        zh = (
            "你还可以尝试使用不支持的 HTTP 方法请求特定 URL。例如，我们尝试向 " +
            raw("/v1/healthcheck") + " 端点发起 " + raw("POST") + " 请求："
        )
    elif "The httprouter package has automatically sent" in source_text:
        zh = (
            "效果非常理想。" + raw("httprouter") + " 包已自动为我们发送 " +
            raw("405 Method Not Allowed") + " 响应，其中包含 " + raw("Allow") +
            " 头部，列出了该端点支持的 HTTP 方法。"
        )
    elif "add a new recoverPanic() middleware" in source_text:
        zh = "并在该文件中添加新的 " + raw("recoverPanic()") + " 中间件："

    return zh


def pair_block_text(node, footnote_defs: dict[str, str], mode: str = "en") -> tuple[str, str]:
    return pair_inline(node, footnote_defs, mode)


def is_footnote_definition(node) -> bool:
    if node.tag != "p":
        return False
    return normalize_space(node_text(node)).startswith("†")


def footnote_definition(node, language: str, footnote_defs: dict[str, str]) -> None:
    if not is_footnote_definition(node):
        return
    clone = copy.deepcopy(node)
    if clone.text and "†" in clone.text:
        clone.text = clone.text.replace("†", "", 1)
    footnote_defs["fn-dagger"] = inline_typst(clone, language, footnote_defs).strip()


def code_text(figure) -> str:
    pre = figure.xpath("./pre")
    return "" if not pre else "".join(pre[0].itertext()).rstrip("\n")


def code_language(figure) -> str:
    classes = (figure.get("class") or "").split()
    return next((item for item in classes if item != "code"), "text")


def code_title(figure) -> str | None:
    caption = figure.xpath("./figcaption")
    return normalize_space(node_text(caption[0])) if caption else None


def image_name(figure) -> str | None:
    images = figure.xpath(".//img[@src]")
    if not images:
        return None
    return Path(images[0].get("src")).name.lower()


def md_table(table) -> list[str]:
    rows = table.xpath(".//tr")
    if not rows:
        return []
    values = [[normalize_space(inline_markdown(cell)) for cell in row.xpath("./th|./td")] for row in rows]
    width = max(len(row) for row in values)
    values = [row + [""] * (width - len(row)) for row in values]
    lines = ["| " + " | ".join(values[0]) + " |", "| " + " | ".join("---" for _ in range(width)) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in values[1:])
    return lines


def md_list(node, depth: int = 0) -> list[str]:
    ordered = node.tag == "ol"
    output: list[str] = []
    index = 1
    for item in node.xpath("./li"):
        prefix = f"{index}. " if ordered else "- "
        content_parts: list[str] = []
        for child in item:
            if child.tag in {"ul", "ol"}:
                continue
            if child.tag == "p":
                content_parts.append(inline_markdown_children(child, "en"))
            else:
                content_parts.append(inline_markdown(child, "en"))
        if item.text:
            content_parts.insert(0, md_escape(normalize_space(item.text)))
        output.append("  " * depth + prefix + " ".join(x for x in content_parts if x))
        for child in item:
            if child.tag in {"ul", "ol"}:
                output.extend(md_list(child, depth + 1))
        index += 1
    return output


def document_footnotes(body, mode: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for paragraph in body.xpath(".//p"):
        if is_footnote_definition(paragraph):
            english = copy.deepcopy(paragraph)
            if english.text and "†" in english.text:
                english.text = english.text.replace("†", "", 1)
            en = inline_typst(english, "en", {}).strip()

            wrappers = paragraph.xpath('.//span[@lang="zh-CN"]')
            if wrappers:
                chinese = clean_translation_wrapper(wrappers[0])
                if chinese.text and "†" in chinese.text:
                    chinese.text = chinese.text.replace("†", "", 1)
                zh = inline_typst(chinese, "zh", {}).strip()
            else:
                zh = en

            if mode == "dual":
                result["fn-dagger"] = f"#dual-footnote([{en}], [{zh}])"
            elif mode == "zh":
                result["fn-dagger"] = f"#footnote[{zh}]"
            else:
                result["fn-dagger"] = f"#footnote[{en}]"
    return result


def normalized_heading_levels(body) -> dict[int, int]:
    """Normalize the first section heading so EPUB quirks do not create 1.0.x."""
    levels: dict[int, int] = {}
    saw_section = False
    for index, element in enumerate(body):
        if element.tag not in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            continue
        level = int(element.tag[1])
        if level == 1:
            levels[index] = level
            continue
        if not saw_section:
            level = 2
            saw_section = True
        levels[index] = level
    return levels


def xhtml_to_markdown(doc, source_name: str) -> str:
    body = doc.xpath("//body")[0]
    heading_levels = normalized_heading_levels(body)
    lines = [f"<!-- source: {source_name} -->", ""]
    for index, element in enumerate(body):
        tag = element.tag
        if tag in {"script", "style"} or tag == "div":
            continue
        if is_footnote_definition(element):
            text = inline_markdown(element, "en").replace("[^fn-dagger]", "", 1).strip()
            lines.extend([f"[^fn-dagger]: {text.lstrip('†').strip()}", ""])
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            title = normalize_space(inline_markdown_children(element, "en"))
            ident = element.get("id")
            suffix = f" {{#{ident}}}" if ident else ""
            lines.extend([f"{'#' * heading_levels.get(index, int(tag[1]))} {title}{suffix}", ""])
        elif tag == "p":
            lines.extend([normalize_space(inline_markdown_children(element, "en")), ""])
        elif tag == "figure":
            if "code" in (element.get("class") or "").split():
                lang = code_language(element)
                title = code_title(element)
                fence = "```" + lang + (f' title="{title}"' if title else "")
                lines.extend([fence, code_text(element), "```", ""])
            elif image_name(element):
                name = image_name(element)
                lines.extend([f"![{name}](../images/{name})", ""])
        elif tag == "aside":
            kind = (element.get("class") or "note").split()[0]
            paragraphs = [normalize_space(inline_markdown_children(p, "en")) for p in element.xpath("./p")]
            content = " ".join(x for x in paragraphs if x)
            lines.extend([f"> [!{kind}] {content}", ""])
        elif tag == "table":
            lines.extend(md_table(element) + [""])
        elif tag in {"ul", "ol"}:
            lines.extend(md_list(element) + [""])
        elif tag == "blockquote":
            content = " ".join(normalize_space(inline_markdown_children(p, "en")) for p in element.xpath("./p"))
            lines.extend(["> " + content, ""])
        elif tag == "hr":
            lines.extend(["---", ""])
    return "\n".join(lines).rstrip() + "\n"


def translation_pair(node, footnote_defs: dict[str, str], mode: str = "en") -> tuple[str, str]:
    en, zh = pair_block_text(node, footnote_defs, mode)
    return en.strip(), zh.strip()


def dual_cell(cell, footnote_defs: dict[str, str], mode: str) -> str:
    en, zh = translation_pair(cell, footnote_defs, mode)
    if mode == "en":
        return en
    if mode == "zh":
        return zh
    if en == zh:
        return en
    return f"{en}#linebreak()#text(font: \"Noto Serif CJK SC\", lang: \"zh\")[{zh}]"


def render_table(table, mode: str, footnote_defs: dict[str, str]) -> str:
    rows = table.xpath(".//tr")
    if not rows:
        return ""
    data = [[dual_cell(cell, footnote_defs, mode) for cell in row.xpath("./th|./td")] for row in rows]
    width = max(len(row) for row in data)
    data = [row + [""] * (width - len(row)) for row in data]
    column_shapes = {
        3: ("0.9fr", "1fr", "1.5fr"),
        4: ("0.7fr", "1.25fr", "1.1fr", "1.9fr"),
    }
    columns = ", ".join(column_shapes.get(width, ("1fr",) * width))
    header = ", ".join(f"[{cell}]" for cell in data[0])
    cells = ", ".join(f"[{cell}]" for row in data[1:] for cell in row)
    return f"#book-table(({columns}), header: ({header}), {cells})"


def render_list(node, mode: str, footnote_defs: dict[str, str], depth: int = 0) -> str:
    marker = "+" if node.tag == "ol" else "-"
    lines: list[str] = []
    for item in node.xpath("./li"):
        blocks = [child for child in item if child.tag in {"ul", "ol"}]
        inline_children = [child for child in item if child.tag not in {"ul", "ol"}]
        if inline_children:
            first = inline_children[0]
            if first.tag == "p":
                content = dual_cell(first, footnote_defs, mode)
            else:
                content = dual_cell(item, footnote_defs, mode)
        else:
            content = dual_cell(item, footnote_defs, mode)
        lines.append("  " * depth + f"{marker} {content}")
        for nested in blocks:
            lines.append(render_list(nested, mode, footnote_defs, depth + 1))
    return "\n".join(lines)


def render_aside(element, mode: str, footnote_defs: dict[str, str]) -> str:
    kind = (element.get("class") or "note").split()[0]
    paragraphs = element.xpath("./p")
    if not paragraphs:
        return ""
    en, zh = translation_pair(paragraphs[0], footnote_defs, mode)
    label = {"important": "Important", "hint": "Hint", "note": "Note"}.get(kind, kind.title())
    en = re.sub(r"^#strong\[(?:Important|Hint|Note):?\]\s*", "", en)
    zh = re.sub(r"^#strong\[(?:重要|提示|注释)：?\]\s*", "", zh)
    en = re.sub(r"^\s*" + re.escape(label) + r"\s*:\s*", "", en)
    en = re.sub(r"^\s*[:：]\s*", "", en)
    zh = re.sub(r"^\s*(?::|：)?\s*(?:重要|提示|注释|注意)?\s*[:：]?\s*", "", zh)
    if mode == "en":
        return f"#book-note[#strong[{typst_escape(label + ':')}] {en}]"
    if mode == "zh":
        return f"#book-note[#strong[{typst_escape({'important': '重要', 'hint': '提示', 'note': '注释'}.get(kind, label + ':'))}] {zh}]"
    return f"#dual-note([#strong[{typst_escape(label + ':')}] {en}], [#strong[{typst_escape({'important': '重要', 'hint': '提示', 'note': '注释'}.get(kind, label + ':'))}] {zh}])"


def render_heading(element, mode: str, footnote_defs: dict[str, str], level: int | None = None) -> str:
    level = int(element.tag[1]) if level is None else level
    en, zh = translation_pair(element, footnote_defs, mode)
    if mode == "en":
        return f"{'=' * level} {en}"
    if mode == "zh":
        return f"{'=' * level} {zh}"
    return f"#dual-heading({level}, [{en}], [{zh}])"


def render_paragraph(element, mode: str, footnote_defs: dict[str, str]) -> str:
    en, zh = translation_pair(element, footnote_defs, mode)
    if mode == "en":
        return en
    if mode == "zh":
        return zh
    return f"#dual([{en}], [{zh}])"


def render_figure(element, mode: str, footnote_defs: dict[str, str]) -> str:
    if "code" in (element.get("class") or "").split():
        lang = code_language(element)
        title = code_title(element)
        source = code_text(element)
        title_arg = f"[{typst_escape(title)}]" if title else "none"
        return f"#code-block({typst_string(lang)}, {title_arg}, {typst_string(source)})"
    name = image_name(element)
    if not name:
        return ""
    return f'#fig("/assets/figures/{name}", width: 80%)'


def render_document(doc, source_name: str, mode: str) -> str:
    body = doc.xpath("//body")[0]
    heading_levels = normalized_heading_levels(body)
    footnote_defs = document_footnotes(body, mode)
    output: list[str] = [
        f"// derived from {source_name}; regenerate with convert.py",
        '#import "../template.typ": *',
        "",
    ]
    chapter_match = re.match(r"(\d+)\.00[-.]", source_name)
    chapter_number = int(chapter_match.group(1)) if chapter_match else None
    opener_title = None
    for candidate in body:
        if candidate.tag == "h1":
            opener_title = candidate
            break
    if chapter_number is not None and opener_title is not None and 1 <= chapter_number <= 21:
        en, zh = translation_pair(opener_title, footnote_defs, mode)
        if mode == "en":
            title = f"[{en}]"
        elif mode == "zh":
            title = f"[{zh}]"
        else:
            title = f"[{en} #linebreak() #text(font: \"Noto Serif CJK SC\", lang: \"zh\")[{zh}]]"
        running = en if mode != "zh" else zh
        output.append(f'#chapter("{chapter_number}", {title}, running: [{running}])')
        output.append("")
    elif chapter_number == 22 and opener_title is not None:
        en, zh = translation_pair(opener_title, footnote_defs, mode)
        if mode == "en":
            title = f"[{en}]"
        elif mode == "zh":
            title = f"[{zh}]"
        else:
            title = f"[{en} #linebreak() #text(font: \"Noto Serif CJK SC\", lang: \"zh\")[{zh}]]"
        output.append(f"#frontchapter({title})[")
        output.append("")
    for index, element in enumerate(body):
        tag = element.tag
        if tag in {"script", "style", "div"}:
            continue
        if is_footnote_definition(element):
            continue
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if element is opener_title:
                continue
            output.append(render_heading(element, mode, footnote_defs, heading_levels.get(index)))
        elif tag == "p":
            output.append(render_paragraph(element, mode, footnote_defs))
        elif tag == "figure":
            output.append(render_figure(element, mode, footnote_defs))
        elif tag == "aside":
            output.append(render_aside(element, mode, footnote_defs))
        elif tag == "table":
            output.append(render_table(element, mode, footnote_defs))
        elif tag in {"ul", "ol"}:
            output.append(render_list(element, mode, footnote_defs))
        elif tag == "blockquote":
            paragraphs = element.xpath("./p")
            lists = element.xpath("./ul|./ol")
            if lists:
                output.append(f"#quoteblock[{render_list(lists[0], mode, footnote_defs)}]")
            elif mode == "dual":
                en, zh = translation_pair(paragraphs[0], footnote_defs, mode)
                output.append(f"#quoteblock[#dual([{en}], [{zh}])]" )
            else:
                text = translation_pair(paragraphs[0], footnote_defs, mode)[0 if mode == "en" else 1]
                output.append(f"#quoteblock[{text}]")
        elif tag == "hr":
            output.append("#line(length: 100%, stroke: 0.4pt + luma(190))")
        output.append("")
    if chapter_number == 22 and opener_title is not None:
        output.append("]")
    return "\n".join(output).rstrip() + "\n"


@dataclass
class Chapter:
    name: str
    english: object
    dual: object
    markdown: Path
    typst_name: str


def chapter_names(z: ZipFile) -> list[str]:
    names = [
        Path(name).name
        for name in z.namelist()
        if name.endswith(".xhtml") and re.match(r"\d+\.\d+[-.]", Path(name).name)
        and not Path(name).name.startswith("00.")
    ]
    return sorted(names)


def load_document(z: ZipFile, name: str):
    return html.fromstring(z.read(name))


def copy_assets(workspace: Path, english: ZipFile) -> list[dict[str, object]]:
    markdown_images = workspace / "lets-go-further-markdown" / "images"
    figures: list[dict[str, object]] = []
    for member in sorted(english.namelist()):
        if not member.startswith("assets/img/") or not member.lower().endswith(".png"):
            continue
        name = Path(member).name.lower()
        if name == "cover.png":
            continue
        data = english.read(member)
        (markdown_images / name).write_bytes(data)
        width, height = png_size(data)
        figures.append({"asset": name, "width": width, "height": height, "sha256": sha256_bytes(data)})
    cover = english.read("assets/img/cover.png")
    for edition in ("en", "dual", "zh"):
        dest = workspace / f"lets-go-further-typst-{edition}" / "assets" / "covers" / "source" / "source-cover.png"
        dest.write_bytes(cover)
        edition_figures = workspace / f"lets-go-further-typst-{edition}" / "assets" / "figures"
        for item in figures:
            shutil.copy2(markdown_images / str(item["asset"]), edition_figures / str(item["asset"]))
    return figures


def write_contract(workspace: Path, edition: str, chapter_entries: list[dict], figures: list[dict]) -> None:
    project = f"lets-go-further-typst-{edition}"
    mode = {"en": "monolingual-en", "dual": "bilingual", "zh": "monolingual-zh"}[edition]
    primary = "en" if edition in {"en", "dual"} else "zh"
    secondary = "zh" if edition == "dual" else ""
    edition_dir = workspace / project
    output = f"output/build/{project}.pdf"
    status_content = "complete"
    status_translation = "complete" if edition != "en" else "not-applicable"
    toml = f'''edition = "{mode}"
project_name = "{project}"
book_slug = "lets-go-further"
source_language = "en"
primary_language = "{primary}"
secondary_language = "{secondary}"
raw_authority = "../lets-go-further-raw/"
markdown_authority = "../lets-go-further-markdown/"
markdown_chapters = "../lets-go-further-markdown/chapters/"
markdown_images = "../lets-go-further-markdown/images/"
source_map = "source-map.json"
local_skill = "../.agents/skills/lets-go-further/"
publisher_profile = "boliu-b5-2"
paragraph_style = "flush-left-spaced"
binding = "left"
duplex = true
flip_edge = "long"
pdf_page_order = "reading"
recto_basis = "physical-pdf-page"
print_scale = "100%"
typst_version = "0.15.1"
typst_entry = "book/main.typ"
template = "book/template.typ"
output_pdf = "{output}"
build_command = 'export_epoch=$(date -u +%s); export_stamp=$(date -u -d "@$export_epoch" "+%Y-%m-%d %H:%M:%S UTC"); typst compile --root . --font-path assets/fonts --creation-timestamp "$export_epoch" --input "export-timestamp=$export_stamp" book/main.typ {output}'
source_cover_status = "supplied-original-private-use"
source_cover_path = "assets/covers/source/source-cover.png"
source_cover_sha256 = "fc7c7c1ecf32165f74c30fda31650ed5c6ccb2483945088bfe11184e62106d21"
fonts = ["DejaVu Serif", "DejaVu Sans", "DejaVu Sans Mono", "Noto Serif CJK SC"]
font_license_record = "assets/fonts/readme.md"
gutter_allowance_mm = 19
physical_proof = "not-run"

[status]
structure = "complete"
content = "{status_content}"
translation = "{status_translation}"
build = "complete"
visual_proof = "representative-passed"
rights = "user-authorized-private-use"
physical_proof = "not-run"
release = "private-use-ready"
'''
    (edition_dir / "book.toml").write_text(toml, encoding="utf-8")
    manifest = {"generator": "lets-go-further/scripts/convert.py", "title": TITLE, "chapters": chapter_entries, "images": [{"asset": f"assets/figures/{item['asset']}", "width": item["width"], "height": item["height"], "sha256": item["sha256"]} for item in figures], "excluded_sources": [], "excluded_assets": []}
    (edition_dir / "source-map.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_main(workspace: Path, edition: str, chapters: list[Chapter]) -> None:
    project = f"lets-go-further-typst-{edition}"
    edition_dir = workspace / project
    if edition == "en":
        title = "Let's Go Further"
        source_version = "Original source: Alex Edwards, version 1.24.0"
    elif edition == "dual":
        title = "Let's Go Further / 更进一步"
        source_version = "Original source: Alex Edwards, version 1.24.0"
    else:
        title = "更进一步"
        source_version = "Original source: Alex Edwards, version 1.24.0"
    includes = "\n".join(f'#include "chapters/{chapter.typst_name}"' for chapter in chapters)
    copyright_text = {
        "en": "Source: Let's Go Further by Alex Edwards, version 1.24.0. Source EPUB and PDF supplied in the raw authority. Typeset as a boliu-b5-2 private-use production proof; the supplied original cover is retained at the user's direction.",
        "dual": "Source: Let's Go Further by Alex Edwards, version 1.24.0. English–Chinese text is derived from the supplied dual EPUB. Typeset as a boliu-b5-2 private-use production proof; the supplied original cover is retained at the user's direction.",
        "zh": "原作：《Let's Go Further》，Alex Edwards，1.24.0 版本。中文内容来自随附双语 EPUB。本文件为 boliu-b5-2 私人制作校样，按用户要求保留随附原书封面。",
    }[edition]
    language_label = {"en": "English", "dual": "English / Chinese", "zh": "中文"}[edition]
    toc_title = {"en": "Contents", "dual": "Contents / 目录", "zh": "目录"}[edition]
    main = f'''#import "template.typ": *
#show: book

#source-cover(
  "{title}",
  "{AUTHOR}",
  "{source_version}",
  original-cover: "/assets/covers/source/source-cover.png",
)

#copyright-page[
  {copyright_text}
  \n\nEdition: {language_label}. Publisher profile: boliu-b5-2. Binding: left, long-edge duplex.
]
#toc-page(title: [{toc_title}], depth: 3)
{includes}
'''
    (edition_dir / "book" / "main.typ").write_text(main, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    raw = workspace / "lets-go-further-raw"
    markdown = workspace / "lets-go-further-markdown" / "chapters"
    for path in markdown.glob("*.md"):
        path.unlink()
    for edition in ("en", "dual", "zh"):
        for path in (workspace / f"lets-go-further-typst-{edition}" / "book" / "chapters").glob("*.typ"):
            path.unlink()
    with ZipFile(raw / ENGLISH_RAW) as english, ZipFile(raw / DUAL_RAW) as dual:
        names = chapter_names(english)
        chapters: list[Chapter] = []
        for name in names:
            stem = Path(name).stem.lower()
            md_path = markdown / f"{stem}.md"
            english_doc = load_document(english, name)
            dual_doc = load_document(dual, name)
            md_path.write_text(xhtml_to_markdown(english_doc, name), encoding="utf-8")
            chapters.append(Chapter(name, english_doc, dual_doc, md_path, f"{stem}.typ"))
        figures = copy_assets(workspace, english)
        for edition in ("en", "dual", "zh"):
            chapter_entries = []
            edition_chapters = workspace / f"lets-go-further-typst-{edition}" / "book" / "chapters"
            for chapter in chapters:
                mode = edition
                source_doc = chapter.dual if edition in {"dual", "zh"} else chapter.english
                content = render_document(source_doc, chapter.name, mode)
                (edition_chapters / chapter.typst_name).write_text(content, encoding="utf-8")
                chapter_entries.append({"source": chapter.markdown.name, "output": f"book/chapters/{chapter.typst_name}", "order": len(chapter_entries) + 1, "source_sha256": sha256_bytes(chapter.markdown.read_bytes())})
            write_contract(workspace, edition, chapter_entries, figures)
            make_main(workspace, edition, chapters)
    print(f"generated {len(chapters)} chapters and {len(figures)} figures for en/dual/zh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
