#!/usr/bin/env python3
"""Recover the supplied Systems Performance EPUB into the canonical Markdown layer.

The EPUB is a UTF-8 XHTML package whose files omit a reliable charset declaration.
This converter deliberately decodes bytes before parsing and keeps the raw package
untouched.  It emits semantic Markdown, an image inventory, and a source manifest;
the Typst editions are generated from this Markdown boundary only.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import urllib.parse
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from lxml import etree, html

try:
    import pymupdf
except ImportError:  # pragma: no cover - the release environment supplies it
    pymupdf = None


BOOK_SLUG = "systems-performance-enterprise-and-the-cloud"
EPUB_ROOT = "OEBPS/xhtml/"
GRAPHICS_ROOT = EPUB_ROOT + "graphics/"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_xhtml(data: bytes):
    # The package is UTF-8, but most documents do not carry a charset meta tag.
    # Decode first; lxml's HTML byte sniffing otherwise treats UTF-8 punctuation
    # as Latin-1 and emits mojibake.
    text = data.decode("utf-8")
    text = re.sub(r"^\s*<\?xml[^>]*\?>", "", text)
    return html.fromstring(text)


def local_attr(el, name: str, default: str | None = None) -> str | None:
    for key, value in el.attrib.items():
        if key == name or key.endswith("}" + name) or key.endswith(":" + name):
            return value
    return default


def classes(el) -> set[str]:
    return set((el.get("class") or "").split())


def text_content(el) -> str:
    return "".join(el.itertext())


def squash_text(value: str) -> str:
    value = value.replace("\xa0", " ")
    return re.sub(r"\s+", " ", value)


def escape_markdown(value: str, table_cell: bool = False) -> str:
    # Escape only Markdown punctuation.  Typst-sensitive characters are handled
    # at the Markdown-to-Typst boundary, not by corrupting the source-language text.
    value = value.replace("\\", "\\\\")
    value = re.sub(r"([`*_\[\]<>])", r"\\\1", value)
    if table_cell:
        value = value.replace("|", r"\|")
        value = value.replace("\n", " ")
    return value


def safe_name(value: str) -> str:
    value = urllib.parse.unquote(value).replace("\\", "/")
    value = Path(value).name.lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "asset"


def safe_label(value: str) -> str:
    value = value.lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "target"


def is_pagebreak(el) -> bool:
    return local_attr(el, "type") == "pagebreak"


def first_text(el) -> str:
    return squash_text(text_content(el)).strip()


class EpubConverter:
    def __init__(self, root: Path):
        self.root = root
        self.raw = root / f"{BOOK_SLUG}-raw"
        self.markdown = root / f"{BOOK_SLUG}-markdown"
        self.chapters_dir = self.markdown / "chapters"
        self.images_dir = self.markdown / "images"
        self.skill_dir = root / ".agents" / "skills" / BOOK_SLUG
        self.references_dir = self.skill_dir / "references"
        self.epub = self._find_one("*.epub")
        self.zip: zipfile.ZipFile | None = None
        self.docs: dict[str, object] = {}
        self.doc_bytes: dict[str, bytes] = {}
        self.href_to_stem: dict[str, str] = {}
        self.id_labels: dict[tuple[str, str], str] = {}
        self.footnote_labels: dict[tuple[str, str], str] = {}
        self.footnote_defs: dict[str, tuple[str, object]] = {}
        self.unresolved_links: list[dict[str, str]] = []
        self.image_map: dict[str, str] = {}
        self.plate_image_map: dict[tuple[str, str], str] = {}
        self.image_records: list[dict[str, object]] = []
        self.stats = Counter()
        self.spine: list[str] = []
        self.output_docs: list[dict[str, object]] = []

    def _find_one(self, pattern: str) -> Path:
        found = sorted(self.raw.glob(pattern))
        if len(found) != 1:
            raise SystemExit(f"expected exactly one {pattern} in {self.raw}, found {len(found)}")
        return found[0]

    def load_package(self) -> None:
        self.zip = zipfile.ZipFile(self.epub)
        container = etree.fromstring(self.zip.read("META-INF/container.xml"))
        opf_path = container.xpath("string(//*[local-name()='rootfile']/@full-path)")
        if not opf_path:
            raise SystemExit("EPUB has no OPF rootfile")
        opf = etree.fromstring(self.zip.read(opf_path))
        ns = {"o": "http://www.idpf.org/2007/opf"}
        manifest = {
            item.get("id"): item.get("href")
            for item in opf.xpath("//o:manifest/o:item", namespaces=ns)
            if item.get("id") and item.get("href")
        }
        base = str(Path(opf_path).parent).replace("\\", "/")
        self.spine = []
        for itemref in opf.xpath("//o:spine/o:itemref", namespaces=ns):
            href = manifest.get(itemref.get("idref"))
            if not href:
                continue
            full = str(Path(base) / urllib.parse.unquote(href)).replace("\\", "/")
            if full.endswith(".xhtml"):
                self.spine.append(full)
        for full in self.spine:
            data = self.zip.read(full)
            stem = Path(full).stem.lower()
            self.docs[stem] = parse_xhtml(data)
            self.doc_bytes[stem] = data
            self.href_to_stem[Path(full).name.lower()] = stem

    def recover_images(self) -> None:
        assert self.zip is not None
        self.images_dir.mkdir(parents=True, exist_ok=True)
        used: dict[str, str] = {}
        for name in sorted(self.zip.namelist()):
            if not name.startswith(GRAPHICS_ROOT):
                continue
            ext = Path(name).suffix.lower()
            if ext not in {".jpg", ".jpeg", ".png", ".gif", ".svg"}:
                continue
            data = self.zip.read(name)
            out = safe_name(Path(name).name)
            if out in used and used[out] != name:
                out = f"{Path(out).stem}-{sha256(data)[:8]}{Path(out).suffix}"
            used[out] = name
            (self.images_dir / out).write_bytes(data)
            self.image_map[name] = out
            rec: dict[str, object] = {
                "asset": out,
                "source": "epub:" + name,
                "bytes": len(data),
                "sha256": sha256(data),
            }
            if pymupdf is not None and ext != ".svg":
                try:
                    pix = pymupdf.Pixmap(data)
                    rec["width"] = pix.width
                    rec["height"] = pix.height
                except Exception:
                    rec["width"] = None
                    rec["height"] = None
            self.image_records.append(rec)
        # The print PDF contains a larger exact source-cover image than the EPUB
        # cover in this supplied set. Preserve it as a separate derived asset and
        # use it only after visual identity is confirmed by the audit script.
        if pymupdf is not None:
            for pdf in sorted(self.raw.glob("*.pdf")):
                try:
                    doc = pymupdf.open(pdf)
                    if doc.page_count != 929:
                        continue
                    images = doc[0].get_images(full=True)
                    if not images:
                        continue
                    info = doc.extract_image(images[0][0])
                    ext = info.get("ext", "jpg")
                    data = info["image"]
                    out = f"source-cover-print.{ext.lower()}"
                    (self.images_dir / out).write_bytes(data)
                    pix = pymupdf.Pixmap(data)
                    self.image_records.append(
                        {
                            "asset": out,
                            "source": "print-pdf-page-1",
                            "bytes": len(data),
                            "sha256": sha256(data),
                            "width": pix.width,
                            "height": pix.height,
                            "selected_as_source_cover": True,
                        }
                    )
                    break
                except Exception:
                    continue

    def build_targets(self) -> None:
        # First collect every source ID so links can be resolved independent of
        # document traversal order.
        for stem, doc in self.docs.items():
            for el in doc.xpath("//*[@id]"):
                ident = el.get("id")
                if not ident:
                    continue
                label = f"{stem}-{safe_label(ident)}"
                self.id_labels[(stem, ident)] = label
        # Footnote definitions and aliases (the visible marker and its anchor often
        # have different IDs in Pearson's XHTML export).
        for stem, doc in self.docs.items():
            n = 0
            for p in doc.xpath("//p"):
                if not classes(p).intersection({"footnote", "footnote1"}):
                    continue
                n += 1
                ident = p.get("id") or f"{stem}-footnote-{n}"
                key = f"fn-{stem}-{safe_label(ident)}"
                self.footnote_defs[key] = (stem, p)
                self.footnote_labels[(stem, ident)] = key
                for anchor in p.xpath(".//a[@id]"):
                    self.footnote_labels[(stem, anchor.get("id"))] = key
                    href = urllib.parse.unquote((anchor.get("href") or "").strip())
                    if "#" in href:
                        self.footnote_labels[(stem, href.split("#", 1)[1])] = key
        # The EPUB places print-fidelity code/configuration images in separate
        # ``*_images.xhtml`` plates.  Their links occur in the prose XHTML; map
        # each plate anchor to its graphic so the Markdown keeps the visual asset
        # instead of a dead link to an excluded navigation document.
        for stem, doc in self.docs.items():
            if not stem.endswith("_images"):
                continue
            anchors = doc.xpath("//a[@id]")
            images = doc.xpath("//img[@src]")
            for anchor, image in zip(anchors, images):
                ident = anchor.get("id")
                src = image.get("src") or ""
                asset = self.image_map.get(self._zip_path(src))
                if ident and asset:
                    self.plate_image_map[(stem, ident)] = asset

    def resolve_href(self, href: str, current_stem: str) -> str | None:
        href = urllib.parse.unquote((href or "").strip())
        if not href:
            return None
        if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//)", href, re.I):
            return href
        path, fragment = (href.split("#", 1) + [""])[:2] if "#" in href else (href, "")
        stem = current_stem
        if path:
            basename = Path(path).name.lower()
            stem = self.href_to_stem.get(basename, stem)
        if fragment:
            plate_asset = self.plate_image_map.get((stem, fragment))
            if plate_asset:
                return f"@image:{plate_asset}"
            key = self.footnote_labels.get((stem, fragment))
            if key:
                return f"#{key}"
            label = self.id_labels.get((stem, fragment))
            if label:
                return f"#{label}"
            self.unresolved_links.append(
                {"source": current_stem, "href": href, "target": fragment}
            )
            return None
        return f"#{stem}"

    def render_inline(self, el, current_stem: str, table_cell: bool = False, footnote_def: bool = False) -> str:
        out: list[str] = []

        def add_text(value: str) -> None:
            if value:
                out.append(escape_markdown(squash_text(value), table_cell=table_cell))

        add_text(el.text or "")
        for child in el:
            tag = child.tag.lower() if isinstance(child.tag, str) else ""
            if is_pagebreak(child):
                self.stats["pagebreak_spans"] += 1
            elif tag in {"strong", "b"}:
                self.stats["strong"] += 1
                out.append("**" + self.render_inline(child, current_stem, table_cell, footnote_def) + "**")
            elif tag in {"em", "i"}:
                self.stats["emphasis"] += 1
                out.append("*" + self.render_inline(child, current_stem, table_cell, footnote_def) + "*")
            elif tag == "code":
                self.stats["inline_code"] += 1
                raw = text_content(child).replace("\n", " ")
                ticks = "``" if "`" in raw else "`"
                out.append(ticks + raw + ticks)
            elif tag == "a":
                href = child.get("href") or ""
                target = self.resolve_href(href, current_stem)
                # Render the anchor's contents without treating the anchor itself as
                # another link (which would recurse forever on XHTML anchors).
                inner = self.render_inline_children(child, current_stem, table_cell, footnote_def)
                if target and target.startswith("#fn-"):
                    out.append(f"[^{target[1:]}]")
                    self.stats["footnote_refs"] += 1
                elif target and target.startswith("@image:"):
                    asset = target.split(":", 1)[1]
                    out.append(f"![{inner}](../images/{asset})")
                    self.stats["code_image_links"] += 1
                elif target:
                    out.append(f"[{inner}]({target})")
                    self.stats["links"] += 1
                else:
                    out.append(inner)
            elif tag == "sup":
                # Footnote anchors are already emitted as [^fn-...]. Other
                # superscripts remain explicit HTML so Markdown retains semantics.
                inner = self.render_inline(child, current_stem, table_cell, footnote_def)
                if inner.startswith("[^fn-"):
                    out.append(inner)
                else:
                    out.append(f"<sup>{inner}</sup>")
            elif tag == "br":
                out.append("  \n")
            elif tag == "img":
                src = child.get("src") or ""
                asset = self.image_map.get(self._zip_path(src), safe_name(src))
                out.append(f"![{escape_markdown(child.get('alt') or 'Image')}](../images/{asset})")
                self.stats["inline_images"] += 1
            elif tag == "span":
                out.append(self.render_inline(child, current_stem, table_cell, footnote_def))
            else:
                out.append(self.render_inline(child, current_stem, table_cell, footnote_def))
            add_text(child.tail or "")
        return "".join(out).strip()

    def render_inline_children(
        self, el, current_stem: str, table_cell: bool = False, footnote_def: bool = False
    ) -> str:
        """Render an inline element's contents, excluding the element wrapper."""
        out: list[str] = []

        if el.text:
            out.append(escape_markdown(squash_text(el.text), table_cell=table_cell))
        for child in el:
            out.append(self.render_inline(child, current_stem, table_cell, footnote_def))
            if child.tail:
                out.append(escape_markdown(squash_text(child.tail), table_cell=table_cell))
        return "".join(out).strip()

    def _zip_path(self, src: str) -> str:
        src = urllib.parse.unquote(src).replace("\\", "/")
        return GRAPHICS_ROOT + Path(src).name

    def source_comment(self, el, stem: str) -> str:
        ident = el.get("id")
        if ident:
            return f"<!-- source-id: {stem}#{ident} -->\n"
        return ""

    def footnote_text(self, p, stem: str) -> str:
        out: list[str] = []
        skipped_marker = False
        if p.text:
            out.append(escape_markdown(squash_text(p.text)))
        for child in p:
            if not skipped_marker and child.tag.lower() == "sup":
                skipped_marker = True
            else:
                out.append(self.render_inline(child, stem, footnote_def=True))
            if child.tail:
                out.append(escape_markdown(squash_text(child.tail)))
        return "".join(out).strip()

    def render_table(self, table, stem: str) -> str:
        rows = []
        for tr in table.xpath("./thead/tr|./tbody/tr|./tr"):
            cells = []
            for cell in tr.xpath("./th|./td"):
                cells.append(self.render_inline(cell, stem, table_cell=True))
            if cells:
                rows.append(cells)
        if not rows:
            return ""
        width = max(len(row) for row in rows)
        rows = [row + [""] * (width - len(row)) for row in rows]
        header = rows[0]
        lines = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
        lines.extend("| " + " | ".join(row) + " |" for row in rows[1:])
        self.stats["tables"] += 1
        self.stats["table_rows"] += len(rows)
        return "\n".join(lines)

    def render_list(self, el, stem: str, depth: int = 0) -> str:
        ordered = el.tag.lower() == "ol"
        lines: list[str] = []
        index = 1
        for li in el.xpath("./li"):
            prefix = f"{index}. " if ordered else "- "
            index += 1
            direct: list[str] = []
            nested: list[str] = []
            for child in li:
                tag = child.tag.lower() if isinstance(child.tag, str) else ""
                if tag in {"ul", "ol"}:
                    nested.append(self.render_list(child, stem, depth + 1))
                elif tag == "p" and classes(child).intersection({"footnote", "footnote1"}):
                    # Footnote definitions nested in list items are emitted once
                    # at the document end, never as visible list content.
                    continue
                elif tag == "p":
                    direct.append(self.render_inline(child, stem))
                else:
                    direct.append(self.render_inline(child, stem))
            if li.text:
                direct.insert(0, escape_markdown(squash_text(li.text)))
            value = " ".join(x for x in direct if x).strip()
            lines.append("  " * depth + prefix + value)
            for block in nested:
                lines.extend("  " * (depth + 1) + line if line else "" for line in block.splitlines())
        self.stats["list_items"] += len(lines)
        return "\n".join(lines)

    def render_figure(self, fig, stem: str) -> str:
        ident = fig.get("id") or ""
        imgs = fig.xpath(".//img[@src]")
        if not imgs:
            return ""
        img = imgs[0]
        src = self._zip_path(img.get("src") or "")
        asset = self.image_map.get(src, safe_name(src))
        captions = fig.xpath(".//figcaption//p")
        caption = self.render_inline(captions[0], stem) if captions else (img.get("alt") or "Image")
        caption = caption.strip() or "Image"
        self.stats["figures"] += 1
        self.stats["figure_images"] += len(imgs)
        return self.source_comment(fig, stem) + f"![{caption}](../images/{asset})"

    def render_block(self, el, stem: str, heading_override: str | None = None) -> str:
        tag = el.tag.lower() if isinstance(el.tag, str) else ""
        if tag in {"section", "article", "body", "div"}:
            if "image-p" in classes(el):
                return ""
            if "publisher" in classes(el) or "cover" in classes(el):
                return self.render_container(el, stem)
            return self.render_container(el, stem)
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = 1 if tag in {"h1", "h2"} else int(tag[1]) - 1
            title = heading_override or self.render_inline(el, stem)
            title = title.strip()
            if not title:
                return ""
            self.stats[f"heading_h{level}"] += 1
            return self.source_comment(el, stem) + "#" * level + " " + title
        if tag == "p":
            c = classes(el)
            if c.intersection({"footnote", "footnote1"}):
                return ""
            if c.intersection({"title-f", "title-t"}):
                return ""
            value = self.render_inline(el, stem)
            if not value:
                return ""
            if c.intersection({"bq", "bqi"}):
                return "\n".join("> " + line for line in value.splitlines())
            self.stats["paragraphs"] += 1
            return self.source_comment(el, stem) + value
        if tag == "figure":
            if "image-c" in classes(el):
                return self.render_figure(el, stem)
            if "table" in classes(el):
                caption_nodes = el.xpath(".//figcaption//p")
                # Pearson's table captions sometimes contain nested ``strong``
                # elements.  Wrapping that already-marked-up result in another
                # strong span produces ambiguous Markdown such as
                # ``**Table 14.1 **Ftrace profilers****``.  Captions are labels,
                # so preserve their exact visible text as one escaped emphasis
                # span and leave inline semantics to the table cells/body.
                caption = (
                    escape_markdown(squash_text(text_content(caption_nodes[0])))
                    if caption_nodes
                    else ""
                )
                table = el.xpath(".//table")
                body = self.render_table(table[0], stem) if table else ""
                return self.source_comment(el, stem) + ((f"**{caption}**\n\n" if caption else "") + body)
            return self.render_container(el, stem)
        if tag == "table":
            return self.render_table(el, stem)
        if tag in {"ul", "ol"}:
            return self.render_list(el, stem)
        if tag == "pre":
            raw = text_content(el).replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
            self.stats["code_blocks"] += 1
            fence = "````" if "```" in raw else "```"
            return self.source_comment(el, stem) + fence + "text\n" + raw + "\n" + fence
        if tag == "hr":
            return "---"
        if tag == "img":
            src = self._zip_path(el.get("src") or "")
            asset = self.image_map.get(src, safe_name(src))
            return f"![{escape_markdown(el.get('alt') or 'Image')}](../images/{asset})"
        if tag == "nav":
            return ""
        return self.render_inline(el, stem)

    def render_container(self, container, stem: str) -> str:
        children = [x for x in container if isinstance(x.tag, str)]
        blocks: list[str] = []
        i = 0
        while i < len(children):
            el = children[i]
            tag = el.tag.lower()
            # Pearson separates a chapter label (h2) from its title (chap_ttl).
            # Combine them in the normalized Markdown while retaining the exact
            # source wording and source ID.
            if tag == "h2" and i + 1 < len(children):
                nxt = children[i + 1]
                if nxt.tag.lower() == "p" and "chap_ttl" in classes(nxt):
                    label = self.render_inline(el, stem).strip()
                    title = self.render_inline(nxt, stem).strip()
                    blocks.append(self.source_comment(el, stem) + f"# {label} — {title}")
                    self.stats["chapter_titles"] += 1
                    i += 2
                    continue
            rendered = self.render_block(el, stem)
            if rendered.strip():
                blocks.append(rendered.strip())
            i += 1
        return "\n\n".join(blocks)

    def render_document(self, stem: str, title: str, include: bool = True) -> str:
        doc = self.docs[stem]
        pagebreaks = [s.get("id") for s in doc.xpath("//span") if is_pagebreak(s) and s.get("id")]
        header = [
            "<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->",
            f"<!-- source-xhtml: {stem}.xhtml -->",
            f"<!-- source-pages: {', '.join(pagebreaks)} -->",
        ]
        body = self.render_container(doc.xpath("//body")[0], stem)
        if not body:
            body = f"# {title}"
        result = "\n".join(header)
        if body:
            result += "\n\n" + body
        definitions = []
        for key, (fn, p) in self.footnote_defs.items():
            if fn != stem:
                continue
            value = self.footnote_text(p, stem)
            if value:
                definitions.append(f"[^{key}]: {value}")
        if definitions:
            result += "\n\n<!-- source footnotes; consumed by the Typst generator -->\n" + "\n".join(definitions)
        return result.rstrip() + "\n"

    def render_front_matter(self) -> str:
        """Combine all semantic front-matter XHTML into one stable Markdown file."""
        stems = ["halftitle", "title", "copyright", "ded01", "pref00", "pref01", "pref02", "pref03"]
        header = [
            "<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->",
            "<!-- source-xhtml: halftitle.xhtml, title.xhtml, copyright.xhtml, ded01.xhtml, pref00.xhtml, pref01.xhtml, pref02.xhtml, pref03.xhtml -->",
            "<!-- source-pages: " + ", ".join(
                pagebreak
                for stem in stems
                for pagebreak in [
                    s.get("id")
                    for s in self.docs[stem].xpath("//span")
                    if is_pagebreak(s) and s.get("id")
                ]
            ) + " -->",
        ]
        chunks: list[str] = []
        definitions: list[str] = []
        for stem in stems:
            if stem not in self.docs:
                continue
            body = self.render_container(self.docs[stem].xpath("//body")[0], stem)
            if body:
                chunks.append(f"<!-- source-xhtml: {stem}.xhtml -->\n{body}")
            for key, (fn, p) in self.footnote_defs.items():
                if fn == stem:
                    value = self.footnote_text(p, stem)
                    if value:
                        definitions.append(f"[^{key}]: {value}")
        result = "\n".join(header)
        if chunks:
            result += "\n\n" + "\n\n".join(chunks)
        if definitions:
            result += "\n\n<!-- source footnotes; consumed by the Typst generator -->\n" + "\n".join(definitions)
        return result.rstrip() + "\n"

    def document_plan(self) -> list[tuple[str, str, str]]:
        # Output names are lowercase ASCII as required by the workspace policy.
        plan: list[tuple[str, str, str]] = []
        plan.append(("pref00", "000-front-matter.md", "Front Matter"))
        for i in range(1, 17):
            plan.append((f"ch{i:02}", f"{i:03}-chapter-{i:02}.md", f"Chapter {i}"))
        for offset, letter, title in [
            (17, "a", "Appendix A"),
            (18, "b", "Appendix B"),
            (19, "c", "Appendix C"),
            (20, "d", "Appendix D"),
            (21, "e", "Appendix E"),
        ]:
            plan.append((f"app{letter}", f"{offset:03}-appendix-{letter}.md", title))
        plan.extend([
            ("gloss", "022-glossary.md", "Glossary"),
            ("index", "023-index.md", "Index"),
            ("bm01", "024-back-matter-01.md", "Back Matter"),
            ("bm02", "025-back-matter-02.md", "Back Matter"),
            ("bm03", "026-back-matter-03.md", "Back Matter"),
        ])
        return plan

    def write_markdown(self) -> None:
        self.chapters_dir.mkdir(parents=True, exist_ok=True)
        self.references_dir.mkdir(parents=True, exist_ok=True)
        plan = self.document_plan()
        for stem, filename, title in plan:
            if stem not in self.docs:
                raise SystemExit(f"planned XHTML document is missing: {stem}")
            data = self.render_front_matter() if stem == "pref00" else self.render_document(stem, title)
            (self.chapters_dir / filename).write_text(data, encoding="utf-8")
            self.output_docs.append(
                {
                    "source": (
                        "halftitle.xhtml, title.xhtml, copyright.xhtml, ded01.xhtml, pref00.xhtml, pref01.xhtml, pref02.xhtml, pref03.xhtml"
                        if stem == "pref00"
                        else f"{stem}.xhtml"
                    ),
                    "output": f"chapters/{filename}",
                    "title": title,
                    "bytes": len(data.encode("utf-8")),
                    "sha256": sha256(data.encode("utf-8")),
                    "source_pagebreaks": [
                        s.get("id")
                        for s in self.docs[stem].xpath("//span")
                        if is_pagebreak(s) and s.get("id")
                    ],
                }
            )
        excluded = [
            {"source": "cover.xhtml", "reason": "rendered by mandatory source-cover macro"},
            {"source": "toc.xhtml", "reason": "native Typst contents replaces web navigation; source retained in raw"},
            {"source": "bk01-toc.xhtml", "reason": "native Typst outline replaces duplicate detailed navigation"},
        ]
        excluded.extend(
            {"source": Path(s).name, "reason": "image-only EPUB plate; referenced graphics are copied to images"}
            for s in self.spine
            if Path(s).stem.endswith("_images")
        )
        manifest = {
            "generator": "systems-performance-enterprise-and-the-cloud.extract_epub.py",
            "generator_version": "1.0.0",
            "source_epub": self.epub.name,
            "source_epub_sha256": sha256(self.epub.read_bytes()),
            "source_encoding": "utf-8 (explicit decode before XHTML parse)",
            "documents": self.output_docs,
            "images": self.image_records,
            "excluded_sources": excluded,
            "unresolved_links": self.unresolved_links,
            "stats": dict(self.stats),
            "spine": [Path(s).name for s in self.spine],
            "notes": [
                "Source pagebreak IDs are provenance only; generated pagination is intentionally reflowed.",
                "The 929-page print PDF is the visual/page-landmark authority; the 2161-page Calibre PDF is an independent cross-check.",
            ],
        }
        (self.references_dir / "source-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        anomaly = {
            "encoding": {
                "observed": "XHTML bytes are UTF-8 but omit a reliable charset declaration",
                "decision": "decode UTF-8 before parsing",
                "test": "curly quotes and apostrophes remain U+2018/U+2019 rather than mojibake",
            },
            "web_navigation": {
                "observed": "toc.xhtml and bk01-toc.xhtml are navigation views",
                "decision": "use native Typst outline and record these as excluded source navigation",
            },
            "image_plates": {
                "observed": "*_images.xhtml contains image-only links to pg*.jpg assets",
                "decision": "copy every graphic once; do not duplicate plate pages as prose chapters",
            },
        }
        (self.references_dir / "source-anomalies.json").write_text(
            json.dumps(anomaly, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def run(self) -> None:
        self.load_package()
        self.recover_images()
        self.build_targets()
        self.write_markdown()
        print(json.dumps({"documents": len(self.output_docs), "images": len(self.image_records), "stats": dict(self.stats), "unresolved_links": len(self.unresolved_links)}, ensure_ascii=False, indent=2))
        if self.unresolved_links:
            raise SystemExit("unresolved internal links remain; inspect source-manifest.json")


def main() -> int:
    root = Path(__file__).resolve().parents[4]
    EpubConverter(root).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
