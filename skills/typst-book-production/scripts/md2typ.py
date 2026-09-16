#!/usr/bin/env python3
"""Convert an explicitly ordered Markdown corpus to the shared book template.

Requires markdown-it-py and mdit-py-plugins. Unsupported semantics fail instead
of silently flattening content. No translation or network fetching is performed.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlsplit
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin


def string(value):
    return json.dumps(value, ensure_ascii=False)


def literal(value):
    return "#text(" + string(value) + ")"


def label(source, anchor=""):
    return "src-" + hashlib.sha256((source + "#" + anchor).encode()).hexdigest()[:20]


def slug(title):
    return re.sub(r"[^\w\s-]", "", title.lower()).strip().replace(" ", "-")


class Converter:
    def __init__(self, source, project, names, front=(), math="reject"):
        self.source, self.project = Path(source).resolve(), Path(project).resolve()
        self.names, self.front, self.math = names, set(front), math
        self.parser = MarkdownIt("commonmark", {"html": True}).enable("table").use(dollarmath_plugin)
        self.docs = {}
        self.targets = {}
        self.assets = {}
        for name in names:
            path = self.safe_source(name)
            tokens = self.parser.parse(path.read_text(encoding="utf-8"))
            self.docs[name] = tokens
            self.targets[(name, "")] = label(name)
            seen = set()
            for i, token in enumerate(tokens):
                if token.type == "heading_open":
                    title = tokens[i+1].content
                    anchor = slug(title)
                    if anchor in seen:
                        raise ValueError(f"{name}: duplicate heading anchor {anchor}; supply a source adapter")
                    seen.add(anchor)
                    self.targets[(name, anchor)] = label(name, anchor)

    def safe_source(self, name):
        path = (self.source / name).resolve()
        if not path.is_relative_to(self.source) or not path.is_file():
            raise ValueError(f"Missing or out-of-root source: {name}")
        return path

    def destination(self, source, url):
        parts = urlsplit(url)
        if parts.scheme in ("https", "http", "mailto"):
            return string(url)
        if parts.scheme or parts.netloc or parts.query:
            raise ValueError(f"Unsupported link: {url}")
        target = source
        if parts.path:
            target = self.safe_source(str(Path(source).parent / unquote(parts.path))).relative_to(self.source).as_posix()
        key = (target, unquote(parts.fragment))
        if key not in self.targets:
            raise ValueError(f"Unresolved internal link: {source} -> {url}")
        return "label(" + string(self.targets[key]) + ")"

    def image(self, source, token, caption=None):
        url = token.attrGet("src")
        parts = urlsplit(url)
        if parts.scheme or parts.netloc:
            raise ValueError("Localize and record remote images before conversion: " + url)
        src = self.safe_source(str(Path(source).parent / unquote(parts.path)))
        relative = src.relative_to(self.source)
        # Content-addressed names avoid clashes and enforce lowercase output paths.
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        asset = Path("assets/figures") / (digest[:20] + src.suffix.lower())
        self.assets[asset.as_posix()] = src
        description = token.content if caption is None else caption
        return '#fig(' + string("/" + asset.as_posix()) + ", width: 80%, caption: [" + literal(description) + "])"

    def inline(self, source, tokens):
        result = []
        for t in tokens or []:
            kind = t.type
            if kind == "text":
                result.append(literal(t.content))
            elif kind == "softbreak":
                result.append("\n")
            elif kind == "hardbreak":
                result.append("#linebreak()")
            elif kind == "code_inline":
                result.append("#raw(" + string(t.content) + ")")
            elif kind in ("em_open", "strong_open"):
                result.append("#" + ("emph" if kind == "em_open" else "strong") + "[")
            elif kind in ("em_close", "strong_close", "link_close"):
                result.append("]")
            elif kind == "link_open":
                result.append("#link(" + self.destination(source, t.attrGet("href")) + ")[")
            elif kind == "image":
                result.append(self.image(source, t))
            elif kind == "math_inline":
                if self.math != "typst":
                    raise ValueError("Dollar math needs an explicit math adapter or --math typst for verified Typst syntax")
                result.append("$" + t.content + "$")
            else:
                raise ValueError(f"Unsupported inline construct {kind} in {source}")
        return "".join(result)

    def render(self, source, tokens, chapter_number):
        out = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t.type == "heading_open":
                title = tokens[i+1].content
                level = int(t.tag[1:])
                body = self.inline(source, tokens[i+1].children)
                # Remove only recognized literal numbering, leaving original
                # title/anchor data in the map. Never flatten styled headings.
                plain = all(c.type == "text" for c in tokens[i+1].children or [])
                prefix = re.match(r"^第\s*(\d+)\s*章[：:\s]+(.*)$", title) if level == 1 else re.match(r"^(\d+(?:\.\d+)+)\s+(.*)$", title)
                if prefix and plain:
                    if source not in self.front and int(prefix[1].split(".")[0]) != chapter_number:
                        raise ValueError(f"{source}: heading number disagrees with reading order")
                    body = literal(prefix[2])
                tag = self.targets[(source, slug(title))]
                if level == 1:
                    # Each input is one chapter/frontchapter; validate before rendering.
                    if source in self.front:
                        out.append("#frontchapter([" + body + "])[\n")
                    else:
                        out.append(f'#chapter("{chapter_number}", [{body}])')
                    out.append("#metadata(" + string(title) + ") <" + self.targets[(source, "")] + ">")
                else:
                    out.append(f"#heading(level: {level})[{body}]")
                out.append("#metadata(" + string(title) + ") <" + tag + ">")
                i += 3
                continue
            if t.type == "paragraph_open":
                children = tokens[i+1].children or []
                following = tokens[i+3] if i+3 < len(tokens) else None
                cap = re.fullmatch(r"\s*<center>(图\s*[\d-]+.*?)</center>\s*", following.content, re.S) if following and following.type == "html_block" else None
                if len(children) == 1 and children[0].type == "image" and cap:
                    out.append(self.image(source, children[0], cap[1]))
                    i += 4
                else:
                    out.append(self.inline(source, children))
                    i += 3
                continue
            if t.type in ("fence", "code_block"):
                lang = t.info.strip().split()[0] if t.info.strip() else "text"
                out.append("#raw(" + string(t.content) + ", block: true, lang: " + string(lang) + ")")
                i += 1
                continue
            if t.type == "math_block":
                if self.math != "typst":
                    raise ValueError("Display math needs an explicit adapter or --math typst")
                out.append("#math.equation(block: true, numbering: none)[$" + t.content + "$]")
                i += 1
                continue
            if t.type in ("bullet_list_open", "ordered_list_open", "list_item_open", "blockquote_open", "table_open"):
                closing = t.type.replace("_open", "_close")
                depth, j = 1, i + 1
                while j < len(tokens):
                    if tokens[j].type == t.type:
                        depth += 1
                    elif tokens[j].type == closing:
                        depth -= 1
                    if depth == 0:
                        break
                    j += 1
                inside = tokens[i+1:j]
                if t.type == "table_open":
                    headers, cells, row, in_header, cell_align = [], [], [], False, "left"
                    for k, cell in enumerate(inside):
                        if cell.type == "thead_open":
                            in_header = True
                        elif cell.type == "thead_close":
                            in_header = False
                        elif cell.type == "tr_open":
                            row = []
                        elif cell.type in ("th_open", "td_open"):
                            style = cell.attrGet("style") or ""
                            cell_align = next((a for a in ("right", "center") if a in style), "left")
                        elif cell.type == "inline":
                            row.append("table.cell(align: " + cell_align + ")[" + self.inline(source, cell.children) + "]")
                        elif cell.type == "tr_close":
                            if in_header:
                                headers = row
                            else:
                                if len(row) != len(headers):
                                    raise ValueError("Ragged table requires an adapter")
                                cells.extend(row)
                    columns = "(" + "1fr," * len(headers) + ")"
                    out.append("#book-table(" + columns + ", header: (" + ",".join(headers) + ",), " + ",".join(cells) + ")")
                elif t.type == "list_item_open":
                    out.append("[" + self.render(source, inside, chapter_number) + "],")
                elif t.type == "blockquote_open":
                    # Preserve a final attribution as its own semantic component.
                    attr = None
                    if len(inside) >= 3 and inside[-3].type == "paragraph_open":
                        match = re.fullmatch(r"(?:——|--)\s*(.+)", inside[-2].content)
                        if match:
                            attr = match[1]
                            inside = inside[:-3]
                    body = self.render(source, inside, chapter_number)
                    out.append("#quoteblock([" + body + "]" + (", attribution: [" + literal(attr) + "]" if attr else "") + ")")
                else:
                    fn = "list" if t.type == "bullet_list_open" else "enum"
                    start = "" if fn == "list" else "start: " + str(t.attrGet("start") or 1) + ","
                    out.append("#" + fn + "(" + start + self.render(source, inside, chapter_number) + ")")
                i = j + 1
                continue
            if t.type == "hr":
                out.append("#line(length: 30%, stroke: 0.5pt)")
            elif t.type == "html_block":
                match = re.fullmatch(r"\s*<center>((?:代码清单|表)\s*[\d-]+.*?)</center>\s*", t.content, re.S)
                if not match:
                    raise ValueError("Unsupported HTML requires a source adapter: " + t.content[:80])
                out.append("#table-caption[" + literal(match[1]) + "]")
            else:
                raise ValueError(f"Unsupported block {t.type} in {source}")
            i += 1
        return "\n\n".join(out)

    def run(self):
        generated, manifest, number = {}, [], 0
        for order, name in enumerate(self.names, 1):
            tokens = self.docs[name]
            if sum(t.type == "heading_open" and t.tag == "h1" for t in tokens) != 1 or tokens[0].type != "heading_open" or tokens[0].tag != "h1":
                raise ValueError(f"{name}: require one leading H1; adapt source explicitly")
            if name not in self.front:
                number += 1
            content = self.render(name, tokens, number)
            if name in self.front:
                content += "\n]\n"
            output = Path("book/chapters") / (f"{order:03d}.typ")
            generated[output] = '#import "/book/template.typ": *\n// Derived by md2typ.py; regenerate from source.\n' + content + "\n"
            manifest.append({"source": name, "output": output.as_posix(), "order": order,
                             "source_sha256": hashlib.sha256(self.safe_source(name).read_bytes()).hexdigest()})
        # Render every chapter successfully before writing any output.
        self.project.mkdir(parents=True, exist_ok=True)
        for relative, content in generated.items():
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        assets = []
        import pymupdf
        for relative, src in self.assets.items():
            target = self.project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
            if src.suffix.lower() == ".svg":
                with pymupdf.open(src) as image_doc:
                    width, height = image_doc[0].rect.width, image_doc[0].rect.height
            else:
                pix = pymupdf.Pixmap(src)
                width, height = pix.width, pix.height
            assets.append({"asset": relative, "width": round(width), "height": round(height),
                           "sha256": hashlib.sha256(src.read_bytes()).hexdigest()})
        result = {"chapters": manifest, "images": assets}
        return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-dir", required=True, type=Path)
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--front", nargs="*", default=[])
    p.add_argument("--math", choices=("reject", "typst"), default="reject")
    p.add_argument("chapters", nargs="+", help="Explicit reading order; paths relative to source-dir")
    args = p.parse_args()
    canonical_source = args.project.resolve() / "source"
    if args.source_dir.resolve() != canonical_source:
        p.error("Place authoritative source under <project>/source first")
    if len(set(args.chapters)) != len(args.chapters):
        p.error("Duplicate chapter")
    converter = Converter(args.source_dir, args.project, args.chapters, args.front, args.math)
    manifest = converter.run()
    (canonical_source / "source-map.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Converted {len(manifest['chapters'])} chapters; review images, math and semantic coverage before release.")


if __name__ == "__main__":
    main()
