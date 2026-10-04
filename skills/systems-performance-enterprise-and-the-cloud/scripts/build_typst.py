#!/usr/bin/env python3
"""Build the three canonical Typst edition trees from the shared Markdown layer.

The converter intentionally has a small, explicit Markdown grammar matching the
output of ``extract_epub.py``.  Literal prose is emitted through ``#text`` so shell
syntax, URLs, dollar signs, brackets, and identifiers cannot accidentally become
Typst code.  Code is stored as separate raw assets and read by Typst at build time.
"""

from __future__ import annotations

import argparse
import os
import hashlib
import json
import re
import shutil
import zipfile
from lxml import html
from pathlib import Path

from code_highlight import classify, highlight
from release_policy import release_status


BOOK_SLUG = "systems-performance-enterprise-and-the-cloud"
BOOK_TITLE = "Systems Performance: Enterprise and the Cloud"
AUTHOR = "Brendan Gregg"
TEMPLATES = Path(os.environ.get("BOLIU_TEMPLATES", "/home/xuntingmu/.agents/skills/typst-book-production/templates"))
ARTWORK = Path(__file__).resolve().parents[1] / "references/cover-art/monet-the-japanese-footbridge-1899.jpg"

SOURCE_FILES = [
    "000-front-matter.md",
    *[f"{i:03}-chapter-{i:02}.md" for i in range(1, 17)],
    *[f"{i:03}-appendix-{c}.md" for i, c in zip(range(17, 22), "abcde")],
    "022-glossary.md",
    "023-index.md",
    "024-back-matter-01.md",
    "025-back-matter-02.md",
    "026-back-matter-03.md",
]

# Physical opener pages are measured independently for each edition.  Chinese
# and dual-language prose reflows the front matter and every later chapter, so
# reusing the English furniture list would leave stale running-head suppression
# and make the layout audit fail after a legitimate translation change.
OPENER_PAGES = {
    "en": (31, 33, 41, 45, 47, 71, 147, 191, 235, 287, 381, 441, 509, 591, 679, 749, 781, 817, 867, 903, 915, 927, 931, 939, 941, 947, 959),
    "zh": (31, 33, 39, 41, 43, 63, 123, 161, 211, 263, 363, 425, 499, 587, 683, 751, 779, 831, 901, 943, 959, 969, 973, 987, 989, 993, 1003),
    "dual": (49, 51, 65, 71, 73, 111, 231, 305, 375, 461, 607, 703, 809, 937, 1073, 1183, 1239, 1289, 1361, 1415, 1433, 1455, 1461, 1471, 1475, 1483, 1501),
}
PDF_PAGES = {"en": 1106, "zh": 1149, "dual": 1760}

# These source blocks are emitted separately by ``main.typ``.  Keeping them
# out of the aggregated front-matter stream avoids duplicating the legal page
# and dedication while preserving the raw source in Markdown.
SKIP_FRONT_SOURCES = {"halftitle", "title", "copyright", "ded01", "pref00"}
FRONT_TOP_TITLES = {"Preface", "Acknowledgments", "About the Author"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def typst_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def literal(value: str) -> str:
    return f"#text({typst_string(value)})" if value else ""


def safe_label(value: str) -> str:
    value = value.lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-") or "target"


def find_unescaped(value: str, needle: str, start: int) -> int:
    pos = start
    while True:
        pos = value.find(needle, pos)
        if pos < 0:
            return -1
        backslashes = 0
        j = pos - 1
        while j >= 0 and value[j] == "\\":
            backslashes += 1
            j -= 1
        if backslashes % 2 == 0:
            return pos
        pos += len(needle)


def find_bracket(value: str, start: int) -> int:
    depth = 0
    pos = start
    while pos < len(value):
        if value[pos] == "\\":
            pos += 2
            continue
        if value[pos] == "[":
            depth += 1
        elif value[pos] == "]":
            depth -= 1
            if depth == 0:
                return pos
        pos += 1
    return -1


def find_paren(value: str, start: int) -> int:
    depth = 0
    pos = start
    while pos < len(value):
        if value[pos] == "\\":
            pos += 2
            continue
        if value[pos] == "(":
            depth += 1
        elif value[pos] == ")":
            depth -= 1
            if depth == 0:
                return pos
        pos += 1
    return -1


class TypstRenderer:
    def __init__(self, workspace: Path, edition: str):
        self.workspace = workspace
        self.edition = edition
        self.markdown_dir = workspace / f"{BOOK_SLUG}-markdown" / "chapters"
        self.translation_dir = (
            workspace
            / ".agents"
            / "skills"
            / BOOK_SLUG
            / "references"
            / "translations"
            / "zh"
        )
        self.edition_dir = workspace / f"{BOOK_SLUG}-typst-{edition}"
        self.chapter_dir = self.edition_dir / "book" / "chapters"
        self.code_dir = self.edition_dir / "assets" / "code"
        self.footnotes_en: dict[str, str] = {}
        self.footnotes_zh: dict[str, str] = {}
        self.footnotes: dict[str, str] = {}
        self.footnote_renderer = None
        self.labels: set[str] = set()
        self.page_reference_targets: dict[str, str] = {}
        self.code_index = 0
        self.code_plate_assets: set[str] = set()
        self.code_records = []
        self.table_index = 0
        self.table_records = []
        self.current_context = ""
        self.current_source_name = ""
        self.files: list[dict[str, object]] = []
        self.image_manifest: list[dict[str, object]] = []
        self.annotation_path = workspace / f"{BOOK_SLUG}-typst-dual" / "editorial/content-audit/annotations.json"
        self.annotations = []
        self.annotation_emissions: dict[str, int] = {}
        if self.annotation_path.exists():
            notes = json.loads(self.annotation_path.read_text(encoding="utf-8"))["notes"]
            ids = [note["id"] for note in notes]
            if len(ids) != len(set(ids)):
                raise ValueError("Duplicate editorial annotation IDs")
            for note in notes:
                if note["verdict"] != "accepted":
                    continue
                source = self.markdown_dir / note["source"]
                text = source.read_text(encoding="utf-8")
                if digest(source) != note["source_sha256"]:
                    raise ValueError(f"Editorial annotation source drift: {note['id']}")
                anchor = note["anchor"]
                comments = [self.source_label(line) for line in text.splitlines() if line.startswith("<!-- source-id:")]
                if comments.count(anchor) != 1 or any(text.count(quote) != 1 for quote in note["source_quotes"]):
                    raise ValueError(f"Editorial annotation anchor/quote mismatch: {note['id']}")
                if note["placement"] not in ("after-complete-table", "after-complete-paragraph") or note["expected_occurrences"] != 1:
                    raise ValueError(f"Unsupported editorial annotation placement: {note['id']}")
                if note["placement"] == "after-complete-paragraph" and len(note["source_quotes"]) != 1:
                    raise ValueError(f"Paragraph annotation needs one exact quote: {note['id']}")
                self.annotations.append(note)
                self.annotation_emissions[note["id"]] = 0

    def editorial_note(self, source_name: str, anchor: str | None, *, placement: str = "after-complete-table") -> str:
        matched = [n for n in self.annotations if n["source"] == source_name and n["anchor"] == anchor and n["placement"] == placement]
        rendered = []
        for note in matched:
            self.annotation_emissions[note["id"]] += 1
            if self.edition == "dual":
                body = self.inline(note["text_en"]) + "#parbreak()" + self.inline(note["text_zh"])
            else:
                body = self.inline(note["text_zh"] if self.edition == "zh" else note["text_en"])
            evidence = " · ".join(f'#link("{e["url"]}")[{self.inline(e["title"])}]' for e in note["evidence"])
            rendered.append(f'#block(breakable: false, above: 10pt, below: 10pt, inset: (left: 10pt), stroke: (left: 0.5pt + rgb("#999999")))[#set text(size: 9.5pt)\n{body}\n#parbreak()#text(size: 8pt)[{evidence}]\n] <editorial-{note["id"]}>')
        return "\n".join(rendered)

    def paragraph_editorial_note(self, source_name: str, paragraph: list[str]) -> str:
        rendered = []
        for note in self.annotations:
            if note["source"] != source_name or note["placement"] != "after-complete-paragraph":
                continue
            quote = note["source_quotes"][0]
            if self.edition == "zh":
                english = (self.markdown_dir / source_name).read_text().splitlines()
                chinese = (self.translation_dir / source_name).read_text().splitlines()
                if len(english) != len(chinese):
                    raise ValueError("Paragraph annotation translation alignment drift")
                quote = chinese[english.index(quote)]
            if "\n".join(paragraph) == quote:
                rendered.append(self.editorial_note(source_name, note["anchor"], placement="after-complete-paragraph"))
        return "\n".join(rendered)

    def collect_footnotes(self) -> None:
        def collect(directory: Path) -> dict[str, str]:
            notes: dict[str, str] = {}
            for source_name in SOURCE_FILES:
                path = directory / source_name
                if not path.exists():
                    raise SystemExit(f"missing {directory.name} translation/source: {source_name}")
                lines = path.read_text(encoding="utf-8").splitlines()
                for line in lines:
                    match = re.match(r"^\[\^([^\]]+)\]:\s*(.*)$", line)
                    if match:
                        key, value = match.groups()
                        # Older machine-translation batches could retain a
                        # second footnote marker with a full-width colon.  Be
                        # tolerant while the sidecar is repaired in place.
                        value = re.sub(rf"^\[\^{re.escape(key)}\]\s*[:：]\s*", "", value)
                        if key in notes and notes[key] != value:
                            raise SystemExit(f"conflicting footnote definition: {key}")
                        notes[key] = value
            return notes

        self.footnotes_en = collect(self.markdown_dir)
        if self.edition in {"dual", "zh"}:
            self.footnotes_zh = collect(self.translation_dir)
            if set(self.footnotes_en) != set(self.footnotes_zh):
                missing_en = sorted(set(self.footnotes_en) - set(self.footnotes_zh))
                missing_zh = sorted(set(self.footnotes_zh) - set(self.footnotes_en))
                raise SystemExit(f"footnote key mismatch: zh missing={missing_en}, en missing={missing_zh}")
        else:
            self.footnotes_zh = dict(self.footnotes_en)
        self.footnotes = self.footnotes_zh if self.edition == "zh" else self.footnotes_en

        # Labels are always derived from the immutable English Markdown.  The
        # translated sidecar preserves source-id comments byte-for-byte, but
        # using the English boundary here makes labels independent of prose.
        for source_name in SOURCE_FILES:
            path = self.markdown_dir / source_name
            lines = path.read_text(encoding="utf-8").splitlines()
            for line_index, line in enumerate(lines):
                code_plate = re.fullmatch(r"!\[Click here to view code image\]\(\.\./images/([^\)]+)\)", line, re.I)
                if code_plate:self.code_plate_assets.add(code_plate.group(1))
                source = re.match(r"^<!-- source-id:\s*([^#]+)#([^ ]+)\s*-->$", line)
                if source:
                    if source_name == "023-index.md":
                        self.labels.add(safe_label(f"{source.group(1)}-{source.group(2)}"))
                    # Typst labels must attach to block-level material.  Page
                    # spans and ordinary glossary paragraphs are still preserved
                    # in Markdown, but their source anchors are represented as
                    # visible text rather than unattached Typst labels.
                    next_index = line_index + 1
                    while next_index < len(lines) and (not lines[next_index].strip() or lines[next_index].startswith("<!--")):
                        next_index += 1
                    if next_index < len(lines):
                        candidate = lines[next_index]
                        if (
                            candidate.startswith("#")
                            or candidate.startswith("!")
                            or candidate.startswith("|")
                            or candidate.startswith("```")
                            or candidate.startswith("> ")
                            or candidate == "---"
                            or re.match(r"^\\s*(?:[-*+] |\\d+\\. )", candidate)
                            or candidate.startswith("**Table ")
                        ):
                            self.labels.add(safe_label(f"{source.group(1)}-{source.group(2)}"))

        # Preserve original print-page index numbers while restoring navigation.
        # Page spans were omitted by extraction; resolve each to the preceding
        # retained semantic anchor in the authoritative EPUB document order.
        epub = next((self.workspace / f"{BOOK_SLUG}-raw").rglob("*.epub"))
        with zipfile.ZipFile(epub) as archive:
            for name in archive.namelist():
                if not name.endswith(".xhtml"):
                    continue
                stem = Path(name).stem.lower()
                doc = html.fromstring(re.sub(r"^\s*<\?xml[^>]*\?>", "", archive.read(name).decode("utf-8")))
                previous = None
                pending = []
                for element in doc.iter():
                    ident = element.get("id")
                    if not ident:
                        continue
                    label = safe_label(f"{stem}-{ident}")
                    if label in self.labels:
                        previous = label
                        for page in pending:
                            self.page_reference_targets[page] = label
                        pending = []
                    elif ident.startswith("page_"):
                        if previous:
                            self.page_reference_targets[label] = previous
                        else:
                            pending.append(label)

    def inline(self, value: str, table_cell: bool = False) -> str:
        """Render the controlled Markdown inline subset as safe Typst content."""
        table_cell = table_cell or self.current_source_name == "023-index.md"
        out: list[str] = []
        plain: list[str] = []

        def table_literal(text: str) -> str:
            if not table_cell:
                return literal(text)
            text = text.replace("、", "、\u200b").replace("；", "；\u200b")
            pieces: list[str] = []
            for token in re.split(r"(\s+)", text):
                if token and len(token) > 12 and re.search(r"[_./:-]", token):
                    for part in re.split(r"([_./:-])", token):
                        if not part:
                            continue
                        pieces.append(literal(part))
                        if part in {"_", ".", "/", ":", "-"}:
                            pieces.append(literal("\u200b"))
                elif token:
                    pieces.append(literal(token))
            return "".join(pieces)

        def flush_plain() -> None:
            if plain:
                out.append(table_literal("".join(plain)))
                plain.clear()

        pos = 0
        while pos < len(value):
            if value[pos] == "\\" and pos + 1 < len(value):
                # Markdown escaping from the EPUB converter; retain the literal
                # punctuation and let #text keep it inert in Typst.
                plain.append(value[pos + 1])
                pos += 2
                continue
            if value.startswith("<sup>", pos):
                end = value.find("</sup>", pos + 5)
                if end >= 0:
                    flush_plain()
                    out.append(f"#super[{self.inline(value[pos + 5:end], table_cell)}]")
                    pos = end + 6
                    continue
            if value.startswith("[^", pos):
                end = find_bracket(value, pos)
                if end >= 0:
                    key = value[pos + 2 : end]
                    flush_plain()
                    definition = self.footnotes.get(key)
                    if definition is None:
                        raise SystemExit(f"footnote reference has no definition: {key}")
                    if self.footnote_renderer is None:
                        out.append(f"#footnote[{self.inline(definition)}]")
                    else:
                        out.append(self.footnote_renderer(key, definition))
                    pos = end + 1
                    continue
            if value[pos] == "[":
                end = find_bracket(value, pos)
                if end >= 0 and end + 1 < len(value) and value[end + 1] == "(":
                    close = find_paren(value, end + 1)
                    if close >= 0:
                        flush_plain()
                        label = self.inline(value[pos + 1 : end], table_cell)
                        target = value[end + 2 : close]
                        if target.startswith("#") and re.fullmatch(r"#[a-z0-9-]+", target) and target[1:] in self.labels:
                            out.append("#link(<" + target[1:] + ">)[" + label + "]")
                        elif target.startswith("#") and target[1:] in self.page_reference_targets:
                            out.append("#index-page(\"" + self.page_reference_targets[target[1:]] + "\", [" + label + "])") if self.current_source_name == "023-index.md" else out.append("#link(<" + self.page_reference_targets[target[1:]] + ">)[" + label + "]")
                        elif re.match(r"^(?:https?|mailto):", target, re.I):
                            out.append("#link(" + typst_string(target) + ")[" + label + "]")
                        else:
                            # Non-web EPUB navigation targets should remain visible
                            # text, never become a filesystem dependency.
                            out.append(label)
                        pos = close + 1
                        continue
            if value[pos] == "`":
                end = find_unescaped(value, "`", pos + 1)
                if end >= 0:
                    flush_plain()
                    raw = value[pos + 1 : end]
                    if table_cell and len(raw) > 12 and re.search(r"[_./:-]", raw):
                        # Long identifiers in narrow reference tables cannot wrap
                        # as one raw span.  Preserve every character while adding
                        # reviewed discretionary breaks after separators.
                        pieces = re.split(r"([_./:-])", raw)
                        broken: list[str] = []
                        for piece in pieces:
                            if not piece:
                                continue
                            broken.append(f"#raw({typst_string(piece)})")
                            if piece in {"_", ".", "/", ":", "-"}:
                                broken.append(literal("\u200b"))
                        out.append("".join(broken))
                    else:
                        out.append(f"#raw({typst_string(raw)})")
                    pos = end + 1
                    continue
            if value.startswith("**", pos):
                end = find_unescaped(value, "**", pos + 2)
                if end >= 0:
                    flush_plain()
                    out.append(f"#strong[{self.inline(value[pos + 2:end], table_cell)}]")
                    pos = end + 2
                    continue
            if value[pos] == "*":
                end = find_unescaped(value, "*", pos + 1)
                if end >= 0:
                    flush_plain()
                    out.append(f"#emph[{self.inline(value[pos + 1:end], table_cell)}]")
                    pos = end + 1
                    continue
            plain.append(value[pos])
            pos += 1
        flush_plain()
        return "".join(out)

    def inline_with(self, value: str, footnotes: dict[str, str], table_cell: bool = False, footnote_renderer=None) -> str:
        """Render inline Markdown against an explicitly selected footnote map."""
        previous = self.footnotes
        previous_renderer = self.footnote_renderer
        self.footnotes = footnotes
        self.footnote_renderer = footnote_renderer
        try:
            return self.inline(value, table_cell=table_cell)
        finally:
            self.footnotes = previous
            self.footnote_renderer = previous_renderer

    def paragraph(self, lines: list[str]) -> str:
        parts: list[str] = []
        for index, raw in enumerate(lines):
            hard_break = raw.endswith("  ")
            text = raw[:-2] if hard_break else raw
            parts.append(self.inline(text))
            if hard_break:
                parts.append("#linebreak()")
            elif index + 1 < len(lines):
                parts.append(literal(" "))
        return "".join(parts)

    def paragraph_with(self, lines: list[str], footnotes: dict[str, str]) -> str:
        previous = self.footnotes
        self.footnotes = footnotes
        try:
            return self.paragraph(lines)
        finally:
            self.footnotes = previous

    def list_block(self, lines: list[str]) -> str:
        rendered: list[str] = []
        for line in lines:
            match = re.match(r"^(\s*)([-*+] |\d+\. )(.*)$", line)
            if not match:
                continue
            indent, marker, text = match.groups()
            typst_marker = "+ " if marker[0].isdigit() else "- "
            rendered.append(indent + typst_marker + self.inline(text))
        return "\n".join(rendered)

    @staticmethod
    def table_cells(line: str) -> list[str]:
        value = line.strip()
        if value.startswith("|"):
            value = value[1:]
        if value.endswith("|") and not value.endswith("\\|"):
            value = value[:-1]
        cells = []
        current = []
        escaped = False
        delimiter = None
        for part in re.split(r"(`+)", value):
            if re.fullmatch(r"`+", part or " "):
                if delimiter is None: delimiter = part
                elif delimiter == part: delimiter = None
                current.append(part)
                continue
            for char in part:
                if char == "|" and not escaped and delimiter is None:
                    cells.append("".join(current).strip())
                    current = []
                else:
                    current.append(char)
                escaped = char == "\\" and not escaped
                if char != "\\": escaped = False
        cells.append("".join(current).strip())
        return cells

    def table_weights(self, rows):
        n = max(map(len, rows))
        # Balance numeric/reference columns against description columns, using
        # the same source-English data in every edition.
        scores = []
        for x in range(n):
            values = [row[x] if x < len(row) else "" for row in rows]
            lengths = sorted(len(re.sub(r"[*`\\]", "", v)) for v in values)
            average = sum(lengths) / max(len(lengths), 1)
            scores.append(max(7.0, average ** 0.6))
        if n == 3 and re.search(r"description|meaning|purpose", rows[0][-1], re.I):
            scores[-1] = max(scores[-1], sum(scores[:-1]) * 0.9)
        return [round(x, 3) for x in scores]

    def parsed_table(self, lines):
        rows = [self.table_cells(line) for line in lines]
        rows = [row for row in rows if row and not all(re.fullmatch(r":?-{3,}:?", cell) for cell in row)]
        if not rows: return []
        n = len(rows[0])
        if any(len(row) != n for row in rows):
            raise SystemExit(f"inconsistent table columns in {self.current_source_name}")
        return rows

    @staticmethod
    def numeric_columns(rows):
        result = []
        for x in range(len(rows[0])):
            values = [r[x].strip().strip("`") for r in rows[1:] if r[x].strip() not in ("", "—", "-", "N/A")]
            result.append(bool(values) and all(re.fullmatch(r"[+−-]?\d[\d,.]*(?:%|[kKmMgG]|\s*[–-]\s*\d[\d,.]*)?", v) for v in values))
        return "(" + ", ".join(str(v).lower() for v in result) + ",)"

    def table_block(self, lines, label=None, caption=None):
        rows = self.parsed_table(lines)
        if not rows: return ""
        self.table_index += 1
        ident = f"table-{self.table_index:03}"
        source_rows = rows
        if self.edition == "zh":
            # Translation retains line alignment, so recover the source table
            # at the same ordinal within the current Markdown document.
            text = (self.markdown_dir / self.current_source_name).read_text()
            source_tables = re.findall(r"(?m)^\|.*(?:\n\|.*)*", text)
            ordinal = sum(r['source'] == self.current_source_name for r in self.table_records)
            source_rows = self.parsed_table(source_tables[ordinal].splitlines())
        weights = self.table_weights(source_rows)
        columns = "(" + ", ".join(f"{w}fr" for w in weights) + ",)"
        cells = ",\n".join(f"[{self.inline(cell, table_cell=True)}]" for row in rows for cell in row)
        self.table_records.append({'id': ident, 'source': self.current_source_name, 'rows': len(rows), 'columns': len(rows[0]), 'weights': weights, 'caption': caption is not None})
        prefix = f"<{label}>" if label else ""
        return f'{prefix}#edition-table({columns}, auto, ({cells},), caption: {caption or "none"}, numeric: {self.numeric_columns(source_rows)}, language: "{self.edition if self.edition == "zh" else "en"}", id: "{ident}")'

    def dual_inline(self, english: str, chinese: str, table_cell: bool = False) -> tuple[str, str]:
        """Render an English/Chinese inline pair with one shared footnote marker."""

        def render_footnote(key: str, definition: str) -> str:
            zh_definition = self.footnotes_zh.get(key, definition)
            en_body = self.inline_with(definition, self.footnotes_en)
            zh_body = self.inline_with(zh_definition, self.footnotes_zh)
            return f"#dual-footnote([{en_body}], [{zh_body}])"

        en = self.inline_with(
            english,
            self.footnotes_en,
            table_cell=table_cell,
            footnote_renderer=render_footnote,
        )
        # The English side owns the actual footnote marker; the Chinese side
        # carries the translated body through the shared dual-footnote block.
        zh = self.inline_with(
            chinese,
            self.footnotes_zh,
            table_cell=table_cell,
            footnote_renderer=lambda _key, _definition: "",
        )
        return en, zh

    def dual_caption(self, english: str, chinese: str, strong: bool = False) -> str:
        en, zh = self.dual_inline(english, chinese)
        if strong:
            en = f"#strong[{en}]"
            zh = f"#strong[{zh}]"
        return f"#dual-caption([{en}], [{zh}])"

    def dual_paragraph(self, english_lines: list[str], chinese_lines: list[str]) -> str:
        # Render each source side directly; parsing generated Typst as Markdown
        # would corrupt inline commands and footnote markers.
        def render_footnote(key: str, definition: str) -> str:
            zh_definition = self.footnotes_zh.get(key, definition)
            en_body = self.inline_with(definition, self.footnotes_en)
            zh_body = self.inline_with(zh_definition, self.footnotes_zh)
            return f"#dual-footnote([{en_body}], [{zh_body}])"

        en = self.paragraph_dual_side(english_lines, self.footnotes_en, render_footnote)
        zh = self.paragraph_dual_side(chinese_lines, self.footnotes_zh, lambda _key, _definition: "")
        return f"#dual([{en}], [{zh}])"

    def paragraph_dual_side(self, lines: list[str], footnotes: dict[str, str], renderer=None) -> str:
        previous = self.footnote_renderer
        self.footnote_renderer = renderer
        try:
            parts: list[str] = []
            for index, raw in enumerate(lines):
                hard_break = raw.endswith("  ")
                text = raw[:-2] if hard_break else raw
                parts.append(self.inline_with(text, footnotes, footnote_renderer=renderer))
                if hard_break:
                    parts.append("#linebreak()")
                elif index + 1 < len(lines):
                    parts.append(literal(" "))
            return "".join(parts)
        finally:
            self.footnote_renderer = previous

    def table_block_pair(self, english_lines, chinese_lines, label=None, captions=None):
        en_rows = self.parsed_table(english_lines)
        zh_rows = self.parsed_table(chinese_lines)
        if not en_rows: return ""
        if len(en_rows) != len(zh_rows) or any(len(a) != len(b) for a, b in zip(en_rows, zh_rows)):
            raise SystemExit(f"dual table dimensions mismatch: {self.current_source_name}")
        self.table_index += 1
        ident = f"table-{self.table_index:03}"
        weights = self.table_weights(en_rows)
        en_cells, zh_cells = [], []
        for en_row, zh_row in zip(en_rows, zh_rows):
            for a, b in zip(en_row, zh_row):
                en, zh = self.dual_inline(a, b, table_cell=True)
                en_cells.append(f"[{en}]")
                zh_cells.append(f"[{zh}]")
        captions = captions or ("none", "none")
        self.table_records.append({'id': ident, 'source': self.current_source_name, 'rows': len(en_rows), 'columns': len(en_rows[0]), 'weights': weights, 'caption': captions[0] != 'none', 'separate_languages': True})
        prefix = f"<{label}>" if label else ""
        return (f'{prefix}#paired-tables(({", ".join(map(str, weights))},), '
                f'({", ".join(en_cells)},), ({", ".join(zh_cells)},), '
                f'caption-en: {captions[0]}, caption-zh: {captions[1]}, numeric: {self.numeric_columns(en_rows)}, id: "{ident}")')

    def save_code(self, source_name: str, code: str) -> str:
        self.code_index += 1
        stem = safe_label(Path(source_name).stem)
        path = self.code_dir / f"{stem}-{self.code_index:04}.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code + "\n", encoding="utf-8")
        language, reason = classify(code, source_name, self.current_context)
        rows = highlight(code, language)
        tokens_path = path.with_suffix('.json')
        tokens_path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        self.code_records.append({'id': path.stem, 'source': source_name, 'asset': path.relative_to(self.edition_dir).as_posix(),
                                  'tokens': tokens_path.relative_to(self.edition_dir).as_posix(), 'sha256': digest(path),
                                  'language': language, 'classification': reason, 'lines': len(code.splitlines()),
                                  'token_bytes_preserved': ''.join(''.join(v for _, v in row) + ('\n' if i < len(rows)-1 else '') for i, row in enumerate(rows)) == code})
        return path.relative_to(self.edition_dir).as_posix()

    def code_block(self, path):
        record = self.code_records[-1]
        return f'#technical-code("/{record["tokens"]}", "{record["language"]}", "{record["id"]}")'

    def image_block(self, alt: str, asset: str, label: str | None = None) -> str:
        prefix = f"<{label}>" if label else ""
        caption = self.inline(alt) if alt and alt.lower() != "image" else "none"
        caption_arg = "none" if caption == "none" else f"[{caption}]"
        return f'{prefix}#fig("/assets/figures/{asset}", caption: {caption_arg}, width: 100%, floating: {str("[^" not in alt).lower()})'

    def source_label(self, comment: str) -> str | None:
        match = re.match(r"<!-- source-id:\s*([^#]+)#([^ ]+)\s*-->", comment)
        if not match:
            return None
        return safe_label(f"{match.group(1)}-{match.group(2)}")

    @staticmethod
    def is_quote_attribution(line: str, language: str) -> bool:
        """Return whether a line is the source attached to a block quotation.

        The normalized Markdown keeps quote sources as the first nonblank line
        after a blockquote.  Restrict the recognizer to the source forms that
        are present in this book so ordinary paragraphs and code output cannot
        accidentally become right-aligned attributions.
        """
        value = line.strip()
        if not value:
            return False
        if value.startswith("—"):
            return True
        if language == "en":
            return bool(re.match(r"^Chinese proverb(?:\s|$)", value, re.I))
        if language == "zh":
            return bool(re.match(r"^中国谚语(?:\s|[（(]|$)", value))
        raise ValueError(f"unsupported quote-attribution language: {language}")

    @classmethod
    def following_quote_attribution(cls, lines: list[str], start: int, language: str) -> int | None:
        """Find the first nonblank attribution line after a blockquote."""
        index = start
        while index < len(lines) and not lines[index].strip():
            index += 1
        if index < len(lines) and cls.is_quote_attribution(lines[index], language):
            return index
        return None

    @staticmethod
    def quote_emphasis_lines(lines: list[str]) -> tuple[list[str], bool]:
        """Remove emphasis delimiters that wrap a multi-line quotation.

        Markdown permits one emphasis pair to span hard-broken blockquote
        lines.  Rendering each line independently would leak the two literal
        asterisks into the PDF, so the delimiters are applied around the
        rendered multi-line content instead.
        """
        if len(lines) > 1 and lines[0].startswith("*") and lines[-1].endswith("*"):
            inner = list(lines)
            inner[0] = inner[0][1:]
            inner[-1] = inner[-1][:-1]
            return inner, True
        return lines, False

    def render_file(self, source_name: str, mode: str) -> str:
        source_dir = self.translation_dir if self.edition == "zh" else self.markdown_dir
        lines = (source_dir / source_name).read_text(encoding="utf-8").splitlines()
        self.current_source_name = source_name
        self.current_context = ""
        table_caption = None
        caption_label = None
        output: list[str] = []
        pending_label: str | None = None
        current_source = ""
        front_open = False
        chapter_started = False

        def close_front() -> None:
            nonlocal front_open
            if front_open:
                output.append("])" )
                front_open = False

        def emit(value: str) -> None:
            if value.strip():
                anchor = re.match(r"^<([a-z0-9-]+)>(.*)$", value, re.S)
                if anchor:
                    target, value = anchor.groups()
                    if value.startswith("#frontchapter("):
                        value += f'\n#metadata("source-anchor") <{target}>'
                    elif target.startswith("index-"):
                        value = f'#metadata("source-anchor") <{target}>\n' + value
                    elif value.startswith(("#technical-code(", "#edition-table(", "#paired-tables(")):
                        value = value[:-1] + f', target: "{target}")'
                    else:
                        value += f" <{target}>"
                output.append(value)

        def should_skip() -> bool:
            return mode == "front" and current_source in SKIP_FRONT_SOURCES

        index = 0
        while index < len(lines):
            line = lines[index]
            if line.startswith("<!--"):
                label = self.source_label(line)
                if label:
                    pending_label = label if label in self.labels else None
                source_match = re.match(r"<!-- source-xhtml:\s*([^, .]+)", line)
                if source_match:
                    current_source = Path(source_match.group(1)).stem.lower()
                index += 1
                continue
            if not line.strip() or line.startswith("[^"):
                index += 1
                continue
            if should_skip():
                pending_label = None
                index += 1
                continue

            fence = re.match(r"^```(?:([^\s]+))?\s*$", line)
            if fence:
                language = fence.group(1) or "text"
                code_lines: list[str] = []
                index += 1
                while index < len(lines) and not lines[index].startswith("```"):
                    code_lines.append(lines[index])
                    index += 1
                if index >= len(lines):
                    raise SystemExit(f"unterminated code fence in {source_name}")
                code_path = self.save_code(source_name, "\n".join(code_lines))
                value = self.code_block(code_path)
                if pending_label:
                    value = f"<{pending_label}>" + value
                pending_label = None
                emit(value)
                index += 1
                continue

            image_match = re.fullmatch(r"!\[(.*)\]\(\.\./images/([^\)]+)\)", line)
            if image_match:
                alt, asset = image_match.groups()
                # The EPUB's print-fidelity code image is immediately followed by
                # the equivalent semantic code block. Keep the Markdown image and
                # asset, but avoid duplicating every listing in the Typst edition.
                look = index + 1
                while look < len(lines) and (not lines[look].strip() or lines[look].startswith("<!--")):
                    look += 1
                if asset in self.code_plate_assets and look < len(lines) and lines[look].startswith("```"):
                    pending_label = None
                    index += 1
                    continue
                value = self.image_block(alt, asset, pending_label)
                pending_label = None
                emit(value)
                index += 1
                continue

            if line.startswith("|"):
                table_lines = [line]
                index += 1
                while index < len(lines) and lines[index].startswith("|"):
                    table_lines.append(lines[index])
                    index += 1
                emit(self.table_block(table_lines, caption_label or pending_label, table_caption))
                emit(self.editorial_note(source_name, caption_label or pending_label))
                table_caption = None
                caption_label = None
                pending_label = None
                continue

            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading:
                level = len(heading.group(1))
                title = heading.group(2).strip()
                self.current_context = title
                if mode == "chapter" and level == 1 and not chapter_started:
                    match = re.match(r"^Chapter\s+(\d+)\s+[—-]\s+(.+)$", title, re.I)
                    if not match:
                        match = re.match(r"^第\s*(\d+)\s*章\s+[—-]\s+(.+)$", title)
                    if match:
                        number, name = match.groups()
                        prefix = f"<{pending_label}>" if pending_label else ""
                        emit(f'{prefix}#chapter("{number}", [{self.inline(name)}], running: [{self.inline(name)}])')
                        pending_label = None
                        chapter_started = True
                        index += 1
                        continue
                if level == 1:
                    close_front()
                    if mode == "front" and (
                        title in FRONT_TOP_TITLES
                        or current_source in {"pref01", "pref02", "pref03"}
                    ):
                        prefix = f"<{pending_label}>" if pending_label else ""
                        emit(f"{prefix}#frontchapter([{self.inline(title)}], [")
                        front_open = True
                        pending_label = None
                        index += 1
                        continue
                    if mode == "matter":
                        prefix = f"<{pending_label}>" if pending_label else ""
                        emit(f"{prefix}#frontchapter([{self.inline(title)}], [")
                        front_open = True
                        pending_label = None
                        index += 1
                        continue
                # All non-top-level headings retain the visible source numbering;
                # the shared template's outline still makes them real targets.
                prefix = f"<{pending_label}>" if pending_label else ""
                outlined = "true" if level <= 3 else "false"
                numbered = re.match(r"^(\d+(?:\.\d+)+)\s+(.+)$", title)
                numbering = "none"
                if numbered:
                    number, title = numbered.groups()
                    numbering = f'(..nums) => {typst_string(number)}'
                emit(f"{prefix}#heading(level: {min(level, 4)}, numbering: {numbering}, outlined: {outlined})[{self.inline(title)}]")
                pending_label = None
                index += 1
                continue

            list_match = re.match(r"^\s*(?:[-*+] |\d+\. )", line)
            if list_match:
                list_lines = [line]
                index += 1
                while index < len(lines):
                    candidate = lines[index]
                    if re.match(r"^\s*(?:[-*+] |\d+\. )", candidate):
                        list_lines.append(candidate)
                        index += 1
                    elif not candidate.strip():
                        # The extractor does not put blank lines inside a list;
                        # stop here so the next paragraph remains independent.
                        break
                    else:
                        break
                value = self.list_block(list_lines)
                if pending_label:
                    value = f"<{pending_label}>" + value
                emit(value)
                pending_label = None
                continue

            if line.startswith("> "):
                quote_lines = []
                while index < len(lines) and lines[index].startswith("> "):
                    quote_lines.append(lines[index][2:])
                    index += 1
                quote_lines, emphasized = self.quote_emphasis_lines(quote_lines)
                body = self.paragraph(quote_lines)
                if emphasized:
                    body = f"#emph[{body}]"
                attribution_index = self.following_quote_attribution(lines, index, "zh" if self.edition == "zh" else "en")
                if attribution_index is None:
                    value = f"#quoteblock[{body}]"
                else:
                    attribution = self.inline(lines[attribution_index].strip())
                    value = f"#quoteblock-attributed([{body}], [{attribution}])"
                    index = attribution_index + 1
                if pending_label:
                    value = f"<{pending_label}>" + value
                emit(value)
                pending_label = None
                continue

            if line == "---":
                emit("#line(length: 100%, stroke: 0.4pt + luma(190))")
                pending_label = None
                index += 1
                continue

            if re.match(r"^\*\*(?:Table\s+|表\s*)\d", line) and line.endswith("**"):
                table_caption = f"[#strong[{self.inline(line[2:-2].strip())}]]"
                caption_label = pending_label
                pending_label = None
                index += 1
                continue

            paragraph_lines = [line]
            index += 1
            while index < len(lines):
                candidate = lines[index]
                if (
                    not candidate.strip()
                    or candidate.startswith("<!--")
                    or candidate.startswith("```")
                    or candidate.startswith("|")
                    or re.match(r"^(#{1,6})\s+", candidate)
                    or re.match(r"^\s*(?:[-*+] |\d+\. )", candidate)
                    or candidate.startswith("> ")
                    or candidate == "---"
                ):
                    break
                paragraph_lines.append(candidate)
                index += 1
            value = self.paragraph(paragraph_lines)
            if pending_label:
                value = f"<{pending_label}>" + value
            emit(value)
            emit(self.paragraph_editorial_note(source_name, paragraph_lines))
            pending_label = None

        close_front()
        return "\n\n".join(output).rstrip() + "\n"

    def render_file_pair(self, source_name: str, mode: str) -> str:
        """Render one Markdown source and its translated sidecar as paired blocks."""
        english = (self.markdown_dir / source_name).read_text(encoding="utf-8").splitlines()
        chinese = (self.translation_dir / source_name).read_text(encoding="utf-8").splitlines()
        if len(english) != len(chinese):
            raise SystemExit(f"dual line-count mismatch in {source_name}: {len(english)} != {len(chinese)}")

        self.current_source_name = source_name
        self.current_context = ""
        table_caption = None
        caption_label = None
        output: list[str] = []
        pending_label: str | None = None
        current_source = ""
        front_open = False
        chapter_started = False

        def close_front() -> None:
            nonlocal front_open
            if front_open:
                output.append("])" )
                front_open = False

        def emit(value: str) -> None:
            if value.strip():
                anchor = re.match(r"^<([a-z0-9-]+)>(.*)$", value, re.S)
                if anchor:
                    target, value = anchor.groups()
                    if value.startswith("#frontchapter("):
                        value += f'\n#metadata("source-anchor") <{target}>'
                    elif target.startswith("index-"):
                        value = f'#metadata("source-anchor") <{target}>\n' + value
                    elif value.startswith(("#technical-code(", "#edition-table(", "#paired-tables(")):
                        value = value[:-1] + f', target: "{target}")'
                    else:
                        value += f" <{target}>"
                output.append(value)

        def should_skip() -> bool:
            return mode == "front" and current_source in SKIP_FRONT_SOURCES

        def image_value(alt_en: str, alt_zh: str, asset: str, label: str | None) -> str:
            prefix = f"<{label}>" if label else ""
            if not alt_en or alt_en.lower() == "image":
                caption = "none"
            else:
                en_alt, zh_alt = self.dual_inline(alt_en, alt_zh)
                caption = f"dual-caption([{en_alt}], [{zh_alt}])"
            return f'{prefix}#fig("/assets/figures/{asset}", caption: {caption}, width: {"75%" if asset == "04fig07.jpg" else "100%"}, floating: {str("[^" not in alt_en).lower()})'

        def list_value(en_line: str, zh_line: str) -> str:
            en_match = re.match(r"^(\s*)([-*+] |\d+\. )(.*)$", en_line)
            zh_match = re.match(r"^(\s*)([-*+] |\d+\. )(.*)$", zh_line)
            if not en_match or not zh_match:
                return ""
            indent, marker, en_text = en_match.groups()
            _, _, zh_text = zh_match.groups()
            en, zh = self.dual_inline(en_text, zh_text)
            typst_marker = "+ " if marker[0].isdigit() else "- "
            return f"{indent}{typst_marker}#dual-list([{en}], [{zh}])"

        index = 0
        while index < len(english):
            line = english[index]
            zh_line = chinese[index]
            if line.startswith("<!--"):
                label = self.source_label(line)
                if label:
                    pending_label = label if label in self.labels else None
                source_match = re.match(r"<!-- source-xhtml:\s*([^, .]+)", line)
                if source_match:
                    current_source = Path(source_match.group(1)).stem.lower()
                index += 1
                continue
            if not line.strip() or line.startswith("[^"):
                index += 1
                continue
            if should_skip():
                pending_label = None
                index += 1
                continue

            fence = re.match(r"^```(?:([^\s]+))?\s*$", line)
            if fence:
                language = fence.group(1) or "text"
                code_lines: list[str] = []
                index += 1
                while index < len(english) and not english[index].startswith("```"):
                    code_lines.append(english[index])
                    index += 1
                if index >= len(english):
                    raise SystemExit(f"unterminated code fence in {source_name}")
                if not chinese[index].startswith("```"):
                    raise SystemExit(f"dual code fence mismatch in {source_name}")
                zh_code = chinese[index - len(code_lines):index]
                if code_lines != zh_code:
                    raise SystemExit(f"translated code changed in {source_name} near line {index + 1}")
                code_path = self.save_code(source_name, "\n".join(code_lines))
                value = self.code_block(code_path)
                if pending_label:
                    value = f"<{pending_label}>" + value
                pending_label = None
                emit(value)
                index += 1
                continue

            image_match = re.fullmatch(r"!\[(.*)\]\(\.\./images/([^\)]+)\)", line)
            if image_match:
                alt_en, asset = image_match.groups()
                image_zh = re.fullmatch(r"!\[(.*)\]\(\.\./images/([^\)]+)\)", zh_line)
                alt_zh = image_zh.group(1) if image_zh else alt_en
                look = index + 1
                while look < len(english) and (not english[look].strip() or english[look].startswith("<!--")):
                    look += 1
                if asset in self.code_plate_assets and look < len(english) and english[look].startswith("```"):
                    pending_label = None
                    index += 1
                    continue
                emit(image_value(alt_en, alt_zh, asset, pending_label))
                pending_label = None
                index += 1
                continue

            if line.startswith("|"):
                en_table = [line]
                zh_table = [zh_line]
                index += 1
                while index < len(english) and english[index].startswith("|"):
                    en_table.append(english[index])
                    zh_table.append(chinese[index])
                    index += 1
                emit(self.table_block_pair(en_table, zh_table, caption_label or pending_label, table_caption))
                emit(self.editorial_note(source_name, caption_label or pending_label))
                table_caption = None
                caption_label = None
                pending_label = None
                continue

            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading:
                level = len(heading.group(1))
                title_en = heading.group(2).strip()
                self.current_context = title_en
                zh_heading = re.match(r"^(#{1,6})\s+(.+)$", zh_line)
                title_zh = zh_heading.group(2).strip() if zh_heading else title_en
                if mode == "chapter" and level == 1 and not chapter_started:
                    chapter_match = re.match(r"^Chapter\s+(\d+)\s+[—-]\s+(.+)$", title_en, re.I)
                    if chapter_match:
                        number, name_en = chapter_match.groups()
                        zh_match = re.match(r"^第\s*(\d+)\s*章\s+[—-]\s+(.+)$", title_zh)
                        name_zh = zh_match.group(2) if zh_match else title_zh
                        en_name, zh_name = self.dual_inline(name_en, name_zh)
                        prefix = f"<{pending_label}>" if pending_label else ""
                        emit(f"{prefix}#chapter(\"{number}\", [#dual-caption([{en_name}], [{zh_name}])], running: [{en_name}])")
                        pending_label = None
                        chapter_started = True
                        index += 1
                        continue
                if level == 1:
                    close_front()
                    if mode == "front" and (
                        title_en in FRONT_TOP_TITLES
                        or current_source in {"pref01", "pref02", "pref03"}
                    ):
                        en_title, zh_title = self.dual_inline(title_en, title_zh)
                        prefix = f"<{pending_label}>" if pending_label else ""
                        emit(f"{prefix}#frontchapter([#dual-caption([{en_title}], [{zh_title}])], running: [{en_title}], [")
                        front_open = True
                        pending_label = None
                        index += 1
                        continue
                    if mode == "matter":
                        en_title, zh_title = self.dual_inline(title_en, title_zh)
                        prefix = f"<{pending_label}>" if pending_label else ""
                        emit(f"{prefix}#frontchapter([#dual-caption([{en_title}], [{zh_title}])], running: [{en_title}], [")
                        front_open = True
                        pending_label = None
                        index += 1
                        continue
                numbered = re.match(r"^(\d+(?:\.\d+)+)\s+(.+)$", title_en)
                numbering = "none"
                if numbered:
                    number, title_en = numbered.groups()
                    title_zh = re.sub(r"^"+re.escape(number)+r"\s+", "", title_zh)
                    numbering = f'(..nums) => {typst_string(number)}'
                en_title, zh_title = self.dual_inline(title_en, title_zh)
                prefix = f"<{pending_label}>" if pending_label else ""
                outlined = "true" if level <= 3 else "false"
                emit(f"{prefix}#dual-heading({min(level, 4)}, [{en_title}], [{zh_title}], numbering: {numbering}, outlined: {outlined})")
                pending_label = None
                index += 1
                continue

            if re.match(r"^\s*(?:[-*+] |\d+\. )", line):
                list_lines = [(line, zh_line)]
                index += 1
                while index < len(english):
                    candidate = english[index]
                    if re.match(r"^\s*(?:[-*+] |\d+\. )", candidate):
                        list_lines.append((candidate, chinese[index]))
                        index += 1
                    elif not candidate.strip():
                        break
                    else:
                        break
                value = "\n".join(list_value(en, zh) for en, zh in list_lines if list_value(en, zh))
                if pending_label:
                    value = f"<{pending_label}>" + value
                emit(value)
                pending_label = None
                continue

            if line.startswith("> "):
                en_quote: list[str] = []
                zh_quote: list[str] = []
                while index < len(english) and english[index].startswith("> "):
                    en_quote.append(english[index][2:])
                    zh_quote.append(chinese[index][2:] if chinese[index].startswith("> ") else chinese[index])
                    index += 1
                en_quote, en_emphasized = self.quote_emphasis_lines(en_quote)
                zh_quote, zh_emphasized = self.quote_emphasis_lines(zh_quote)
                if en_emphasized != zh_emphasized:
                    raise SystemExit(f"bilingual quote emphasis mismatch in {source_name} after line {index}")
                body_en = self.paragraph_dual_side(en_quote, self.footnotes_en, lambda key, definition: self.dual_footnote(key, definition))
                body_zh = self.paragraph_dual_side(zh_quote, self.footnotes_zh, lambda _key, _definition: "")
                if en_emphasized:
                    body_en = f"#emph[{body_en}]"
                    body_zh = f"#emph[{body_zh}]"
                attribution_en_index = self.following_quote_attribution(english, index, "en")
                attribution_zh_index = self.following_quote_attribution(chinese, index, "zh")
                if (attribution_en_index is None) != (attribution_zh_index is None):
                    raise SystemExit(f"bilingual quote attribution mismatch in {source_name} after line {index}")
                if attribution_en_index is None:
                    value = f"#quoteblock[#dual([{body_en}], [{body_zh}])]"
                else:
                    if attribution_en_index != attribution_zh_index:
                        raise SystemExit(f"bilingual quote attribution line drift in {source_name}")
                    attribution_en, attribution_zh = self.dual_inline(
                        english[attribution_en_index].strip(), chinese[attribution_zh_index].strip()
                    )
                    value = (
                        f"#dual-quoteblock-attributed([#dual([{body_en}], [{body_zh}])], "
                        f"[{attribution_en}], [{attribution_zh}])"
                    )
                    index = attribution_en_index + 1
                if pending_label:
                    value = f"<{pending_label}>" + value
                emit(value)
                pending_label = None
                continue

            if line == "---":
                emit("#line(length: 100%, stroke: 0.4pt + luma(190))")
                pending_label = None
                index += 1
                continue

            if line.startswith("**Table ") and line.endswith("**"):
                title_en = line[2:-2].strip()
                title_zh = zh_line[2:-2].strip() if zh_line.startswith("**") and zh_line.endswith("**") else title_en
                en, zh = self.dual_inline(title_en, title_zh)
                table_caption = (f"[#strong[{en}]]", f"[#strong[{zh}]]")
                caption_label = pending_label
                pending_label = None
                index += 1
                continue

            en_para = [line]
            zh_para = [zh_line]
            index += 1
            while index < len(english):
                candidate = english[index]
                if (
                    not candidate.strip()
                    or candidate.startswith("<!--")
                    or candidate.startswith("```")
                    or candidate.startswith("|")
                    or re.match(r"^(#{1,6})\s+", candidate)
                    or re.match(r"^\s*(?:[-*+] |\d+\. )", candidate)
                    or candidate.startswith("> ")
                    or candidate == "---"
                ):
                    break
                en_para.append(candidate)
                zh_para.append(chinese[index])
                index += 1
            value = self.dual_paragraph(en_para, zh_para)
            if pending_label:
                value = f"<{pending_label}>" + value
            emit(value)
            emit(self.paragraph_editorial_note(source_name, en_para))
            pending_label = None

        close_front()
        return "\n\n".join(output).rstrip() + "\n"

    def dual_footnote(self, key: str, definition: str) -> str:
        zh_definition = self.footnotes_zh.get(key, definition)
        en_body = self.inline_with(definition, self.footnotes_en)
        zh_body = self.inline_with(zh_definition, self.footnotes_zh)
        return f"#dual-footnote([{en_body}], [{zh_body}])"

    def prepare_tree(self) -> None:
        for relative in (
            "assets/covers/boliu",
            "assets/covers/source",
            "assets/figures",
            "assets/fonts",
            "assets/code",
            "book/chapters",
            "editorial/content-audit",
            "output/audit",
            "output/build",
            "output/preview",
        ):
            (self.edition_dir / relative).mkdir(parents=True, exist_ok=True)
        for font in (Path(__file__).resolve().parents[1] / "references/fonts").iterdir():
            shutil.copy2(font, self.edition_dir / "assets/fonts" / font.name)
        for name in ("core.typ", "covers.typ", "matter.typ"):
            shutil.copy2(TEMPLATES / name, self.edition_dir / "book" / name)
        matter_path = self.edition_dir / "book" / "matter.typ"
        matter_path.write_text(
            matter_path.read_text(encoding="utf-8")
            + "\n\n"
            + Path(__file__).with_name("quote-style.typ").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        if self.edition == "dual":
            bilingual = (TEMPLATES / "bilingual.typ").read_text(encoding="utf-8")
            bilingual = bilingual.replace("Noto Serif SC", "Noto Serif CJK SC")
            bilingual = bilingual.replace(
                "#let dual-heading(level, en, zh) = heading(level: level)[",
                "#let dual-heading(level, en, zh, numbering: none, outlined: true) = heading(level: level, numbering: numbering, outlined: outlined)[",
            )
            bilingual = bilingual.replace("#let dual-zh-body-size = none", "#let dual-zh-body-size = 9.5pt")
            footnote_start = bilingual.index("#let dual-footnote")
            bilingual = bilingual[:footnote_start] + Path(__file__).with_name("bilingual-footnotes.typ").read_text()
            bilingual += "\n\n" + Path(__file__).with_name("dual-quote-style.typ").read_text(encoding="utf-8")
            (self.edition_dir / "book" / "bilingual.typ").write_text(bilingual, encoding="utf-8")
        core_path = self.edition_dir / "book" / "core.typ"
        core_text = (
            core_path.read_text(encoding="utf-8")
            
            .replace("Noto Serif SC", "Noto Serif CJK SC")
        )
        # Query only semantic opener marks. Their zero-size metadata does not
        # participate in body flow, and furniture emits no marks of its own.
        furniture = (Path(__file__).with_name("page_furniture.typ")).read_text(encoding="utf-8")
        core_text = re.sub(
            r"#let page-role\(role, running: \[\]\) = metadata\(.*?^#let section-title",
            lambda _: furniture + "#let section-title",
            core_text,
            flags=re.S | re.M,
        )
        core_text = core_text.replace(
            '      if page-kind() != "body" { return }\n',
            '      if is-opener() or is-blank() { return }\n',
        ).replace(
            '      if page-kind() == "opener" {\n',
            '      if is-opener() {\n',
        )
        core_text = core_text.replace('counter(heading).display("1.1")', 'counter(heading).display(it.numbering)')
        core_text = core_text.replace('grid(columns: (auto, 1fr), gutter: 6pt,', 'grid(columns: (auto, 1fr), gutter: if it.numbering == none { 0pt } else { 6pt },')
        core_text = core_text.replace('#set text(size: if it.level == 1 { 10pt } else { 9pt })', '#set text(size: if it.level == 1 { 10pt } else { 9pt }, hyphenate: false)\n    #set par(justify: false, spacing: 0pt)')
        core_text = core_text.replace('gutter: 4pt, align: (left, top),', 'gutter: if it.element.numbering == none { 0pt } else { 4pt }, align: (left, top),')
        core_text = core_text.replace('#text(size: 10.5pt, weight: "bold", style: "italic")[#it.body]', '#grid(columns: (auto, 1fr), gutter: if it.numbering == none { 0pt } else { 6pt }, align: (left, top), if it.numbering != none { text(size: 10.5pt, weight: "bold", style: "italic", counter(heading).display(it.numbering)) }, text(size: 10.5pt, weight: "bold", style: "italic", it.body))')
        toc_start = core_text.index("  show outline.entry:")
        toc_end = core_text.index("  show footnote.entry:", toc_start)
        core_text = core_text[:toc_start] + Path(__file__).with_name("contents-style.typ").read_text() + core_text[toc_end:]
        core_text = core_text.replace('("DejaVu Sans", "Noto Serif CJK SC")', '("DejaVu Sans", "Noto Sans CJK SC")')
        core_path.write_text(core_text, encoding="utf-8")
        cover_path = self.edition_dir / "book/covers.typ"
        cover_text = cover_path.read_text().replace('accent, display-face, faint, page-role', 'accent, display-face, faint, ink-gray, page-role')
        cover_text = cover_text[:cover_text.index("#let boliu-cover(")] + Path(__file__).with_name("painting-cover.typ").read_text()
        cover_path.write_text(cover_text)
        if self.edition == "dual":
            template = '#import "bilingual.typ": *\n'
        else:
            body_lang = "zh" if self.edition == "zh" else "en"
            template = (
                '#import "core.typ": *\n'
                '#import "matter.typ": *\n'
                '#import "covers.typ": source-cover, boliu-cover\n\n'
                f'#let book = boliu-book.with(body-font: ("Libertinus Serif", "Noto Serif CJK SC"), body-lang: "{body_lang}")\n'
            )
        shutil.copy2(Path(__file__).with_name("publication.typ"), self.edition_dir / "book/publication.typ")
        template += '#import "publication.typ": technical-code, edition-table, paired-tables, fig, book-index, index-size, index-page\n'
        if self.edition == "dual":
            template += "#let dual-index = dual.with(cjk-size: none)\n"
        (self.edition_dir / "book" / "template.typ").write_text(template, encoding="utf-8")
        source_cover = self.workspace / f"{BOOK_SLUG}-markdown" / "images" / "source-cover-print.jpeg"
        shutil.copy2(source_cover, self.edition_dir / "assets/covers/source/source-cover-print.jpeg")
        shutil.copy2(ARTWORK, self.edition_dir / "assets/covers/boliu/monet-the-japanese-footbridge-1899.jpg")
        shutil.copy2(ARTWORK.with_name("provenance.json"), self.edition_dir / "assets/covers/boliu/provenance.json")
        # Copy the complete recovered image inventory.  Even assets omitted from
        # the current Typst flow remain available for later reviewed editions.
        image_source = self.workspace / f"{BOOK_SLUG}-markdown" / "images"
        for image in sorted(image_source.iterdir()):
            if image.name == "source-cover-print.jpeg":
                continue
            target = self.edition_dir / "assets/figures" / image.name
            shutil.copy2(image, target)
        # Read dimensions from the already audited source manifest, not from a
        # lossy re-probe of every copied file.
        source_manifest = json.loads(
            (self.workspace / ".agents/skills" / BOOK_SLUG / "references/source-manifest.json").read_text(encoding="utf-8")
        )
        self.image_manifest = [
            {
                "asset": f"assets/figures/{item['asset']}",
                "width": int(item["width"]),
                "height": int(item["height"]),
                "source": item.get("source"),
                "sha256": item.get("sha256"),
            }
            for item in source_manifest["images"]
            if item["asset"] != "source-cover-print.jpeg"
        ]

    def write_content(self) -> None:
        mapping: list[dict[str, object]] = []
        render = self.render_file_pair if self.edition == "dual" else self.render_file
        front = render("000-front-matter.md", "front")
        (self.chapter_dir / "front-matter.typ").write_text('#import "../template.typ": *\n\n' + front, encoding="utf-8")
        mapping.append({"source": "000-front-matter.md", "output": "book/chapters/front-matter.typ", "source_sha256": digest(self.markdown_dir / "000-front-matter.md"), "order": 0})

        for i in range(1, 17):
            source = f"{i:03}-chapter-{i:02}.md"
            output = f"chapter-{i:02}.typ"
            text = render(source, "chapter")
            (self.chapter_dir / output).write_text('#import "../template.typ": *\n\n' + text, encoding="utf-8")
            mapping.append({"source": source, "output": f"book/chapters/{output}", "source_sha256": digest(self.markdown_dir / source), "order": i})

        for offset, letter in zip(range(17, 22), "abcde"):
            source = f"{offset:03}-appendix-{letter}.md"
            output = f"appendix-{letter}.typ"
            text = render(source, "matter")
            (self.chapter_dir / output).write_text('#import "../template.typ": *\n\n' + text, encoding="utf-8")
            mapping.append({"source": source, "output": f"book/chapters/{output}", "source_sha256": digest(self.markdown_dir / source), "order": offset})

        for source, output, order in (
            ("022-glossary.md", "glossary.typ", 22),
            ("023-index.md", "index.typ", 23),
            ("024-back-matter-01.md", "back-matter-01.typ", 24),
            ("025-back-matter-02.md", "back-matter-02.typ", 25),
            ("026-back-matter-03.md", "back-matter-03.typ", 26),
        ):
            text = render(source, "matter")
            if source == "023-index.md":
                # Index letters are navigational symbols, never translated words.
                if self.edition == "zh":
                    letters = iter("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                    text = re.sub(r'#heading\(level: 2, numbering: none, outlined: true\)\[.*?\]',
                                  lambda m: f'#heading(level: 2, numbering: none, outlined: false)[{next(letters)}]', text)
                text = re.sub(r'#dual-heading\(2, \[\#text\("([A-Z])"\)\], .*?\], numbering: none, outlined: true\)',
                              lambda m: f'#heading(level: 2, numbering: none, outlined: false)[{m.group(1)}]', text)
                text = re.sub(r'#heading\(level: 2, numbering: none, outlined: true\)\[\#text\("([A-Z])"\)\]',
                              lambda m: f'#heading(level: 2, numbering: none, outlined: false)[{m.group(1)}]', text)
                start = text.index("\n") + 1
                end = text.rfind("])" )
                if self.edition == "dual":
                    text = text.replace("#dual(", "#dual-index(")
                end = text.rfind("])")
                index_notice = '#block(breakable: false, below: 8pt)[#text(size: 8pt, fill: faint)[Index numbers show this edition’s physical pages at the corresponding semantic anchors; original print numbers follow in brackets.\\ 索引数字为本版对应语义位置的物理页码，方括号内保留原书印刷页码；电子版数字可点击。]]\n' if self.edition == "dual" else '#block(breakable: false, below: 8pt)[#text(size: 8pt, fill: faint)[' + ('索引数字为本版对应语义位置的物理页码，方括号内保留原书印刷页码；电子版数字可点击。' if self.edition == "zh" else 'Index numbers show this edition’s physical pages at the corresponding semantic anchors; original print numbers follow in brackets. Click numbers to navigate.') + ']]\n'
                text = text[:start] + index_notice + '#book-index[\n' + text[start:end] + ']\n' + text[end:]
            (self.chapter_dir / output).write_text('#import "../template.typ": *\n\n' + text, encoding="utf-8")
            mapping.append({"source": source, "output": f"book/chapters/{output}", "source_sha256": digest(self.markdown_dir / source), "order": order})

        copyright_text = self.render_copyright_pair() if self.edition == "dual" else self.render_copyright()
        (self.chapter_dir / "copyright.typ").write_text('#import "../template.typ": *\n\n' + copyright_text, encoding="utf-8")
        dedication_text = self.render_dedication_pair() if self.edition == "dual" else self.render_dedication()
        (self.chapter_dir / "dedication.typ").write_text('#import "../template.typ": *\n\n' + dedication_text, encoding="utf-8")

        status = release_status(self.workspace, self.edition)
        source_map = {
            "editorial_annotations": {"authority": str(self.annotation_path.relative_to(self.workspace)), "sha256": digest(self.annotation_path) if self.annotation_path.exists() else None, "emitted": self.annotation_emissions},
            "generator": "book-local build_typst.py",
            "generator_version": "1.2.1",
            "code": self.code_records,
            "tables": self.table_records,
            "print_page_navigation": {"display": "current-edition physical page followed by original print reference in brackets", "precision": "nearest preceding retained semantic anchor in authoritative EPUB", "targets": self.page_reference_targets},
            "authority": "canonical Markdown chapters; EPUB semantic source reconciled to 929-page print PDF and 2161-page Calibre PDF",
            "edition": self.edition,
            "title": BOOK_TITLE,
            "author": AUTHOR,
            "mapping_granularity": "one normalized Markdown document to one maintained Typst chapter file",
            "chapters": mapping,
            "images": self.image_manifest,
            "excluded_sources": [],
            "excluded_assets": [],
            **status,
        }
        (self.edition_dir / "source-map.json").write_text(json.dumps(source_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        book_toml = f'''schema = "typst-book-production/v1"
name = "{BOOK_SLUG}-typst-{self.edition}"
title = "{BOOK_TITLE}"
author = "{AUTHOR}"
source_language = "en"
edition = "{ {"en": "monolingual-en", "zh": "monolingual-zh", "dual": "bilingual"}[self.edition]}"
project_name = "{BOOK_SLUG}-typst-{self.edition}"
book_slug = "{BOOK_SLUG}"
primary_language = "{ "zh" if self.edition == "zh" else "en" }"
raw_authority = "../{BOOK_SLUG}-raw/"
markdown_authority = "../{BOOK_SLUG}-markdown/"
local_skill = "../.agents/skills/{BOOK_SLUG}/"
translation_status = "{status['translation_status']}"
release_ready = {str(status['release_ready']).lower()}
release_approval_basis = "{status['release_approval_basis']}"
full_text_review_complete = {str(status['full_text_review_complete']).lower()}
template = "book/template.typ"
source_markdown = "../{BOOK_SLUG}-markdown/chapters"
source_map = "source-map.json"
output_pdf = "output/build/{BOOK_SLUG}-typst-{self.edition}.pdf"
build_command = "python3 ../.agents/skills/systems-performance-enterprise-and-the-cloud/scripts/build_edition.py --edition {self.edition}"
source_cover = "assets/covers/source/source-cover-print.jpeg"
publisher_artwork = "assets/covers/boliu/monet-the-japanese-footbridge-1899.jpg"
code_highlight = "pygments-2.18.0"
bilingual_tables = "separate-matched-geometry"
paragraph_pairs = "native-paragraphs-shared-gap"
publisher_profile = "boliu-b5-2"
contents_style = "ddia-hierarchy-native-leaders; black-chapters-blue-sections-gray-nested"
publisher_imprint_position = "bottom-center"
publisher_cover_override = "user-requested-public-domain-classic-painting-2026-10-01"
publisher_artwork_source = "https://www.nga.gov/artworks/74796-japanese-footbridge"
publisher_artwork_rights = "NGA Open Access CC0"
publisher_artwork_provenance = "assets/covers/boliu/provenance.json"
publisher_artwork_crop = "none"
contents_visual_proof = "output/preview/details/"
paragraph_style = "flush-left-spaced"
body_en = "Libertinus Serif"
heading_zh = "Noto Sans CJK SC"
footnote_en_pt = 8
bilingual_footnote_zh_pt = 7
quality_reference = "../../ddia-v2/ddia-v2-typest-dual/"
body_zh = "Noto Serif CJK SC"
body_size_pt = 10
body_latin_size_pt = 10
body_cjk_size_pt = {9.5 if self.edition == "dual" else 10}
footnote_cjk_size_pt = {7 if self.edition == "dual" else 8}
mixed_script_policy = "latin-face-size-and-emphasis-follow-component-role; cjk-only-optical-compensation"
body_leading_em = 0.68
paragraph_gap_em = 1.1
binding = "left"
duplex = true
flip_edge = "long"
print_scale = "100%"
figure_caption_alignment = "center"
quote_attribution_alignment = "right-within-quote-block"
table_continuation_policy = "repeated-identity-language-and-header"
index_pagination = "current-edition-physical-pages-with-source-print-provenance"
raster_resolution_policy = "user-accepted-source-resolution-2026-10-03; preserve-original-bytes"
source_raster_target_met = false
'''
        (self.edition_dir / "book.toml").write_text(book_toml, encoding="utf-8")

        # This edition-level audit makes the translation boundary explicit and
        # records the deliberate math/code-image decisions for future passes.
        audit = {
            "edition": self.edition,
            "translation_status": status["translation_status"],
            "release_ready": status["release_ready"],
            "visual_qa": {"status": "pending-build-and-pdf-audit", "pdf_pages": None, "inspected_physical_pages": []},
            "omissions": [
                {"source": "pref00.xhtml", "reason": "EPUB technical usage note; absent from supplied print PDF body"},
                {"source": "toc.xhtml", "reason": "replaced by native Typst outline"},
                {"source": "bk01-toc.xhtml", "reason": "replaced by native Typst outline"},
            ],
            "decisions": [
                "Print-fidelity code-image links remain in Markdown/assets; Typst uses the adjacent semantic raw code block once.",
                "Sparse formula-like paragraphs remain source-faithful text/italics; no unreviewed math conversion was applied.",
                "Copyright and dedication source blocks are emitted once in their dedicated matter files; the aggregated front-matter stream skips them.",
                "The 929-page print-PDF cover raster is selected for page 1 because it is higher resolution than the EPUB cover; the EPUB raster remains in the Markdown asset inventory.",
                "Running furniture is suppressed by semantic opener metadata without physical-page constants.",
                "Standalone quotation and proverb attributions are emitted inside the quotation block and right-aligned to its content edge; bilingual attribution lines share that edge.",
                *(["User-approved bilingual optical compensation: body Latin 10pt in both languages; CJK body glyphs (including lists) 9.5pt only; other components retain their own role sizes.",
                   "Figure 4.7 uses 75% live width to keep its caption and note with nearby prose after optical compensation."]
                  if self.edition == "dual" else []),
                "Back matter begins on a recto using semantic page furniture; an automatic blank verso is retained when needed.",
            ],
        }
        (self.edition_dir / "editorial/content-audit/production-decisions.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def render_copyright(self) -> str:
        source_dir = self.translation_dir if self.edition == "zh" else self.markdown_dir
        lines = (source_dir / "000-front-matter.md").read_text(encoding="utf-8").splitlines()
        chunks: list[str] = []
        active = False
        for line in lines:
            marker = re.match(r"<!-- source-xhtml:\s*([^, .]+)", line)
            if marker:
                active = Path(marker.group(1)).stem.lower() == "copyright"
                continue
            if active and not line.startswith("<!--") and not line.startswith("# Systems Performance"):
                chunks.append(line)
        # Reuse the normal block renderer only for the legal prose; images and
        # links are safe through inline(), and a blank source gives a legal marker.
        body: list[str] = []
        for line in chunks:
            if not line.strip():
                continue
            image = re.fullmatch(r"!\[(.*)\]\(\.\./images/([^\)]+)\)", line)
            if image:
                body.append(self.image_block(*image.groups()))
            else:
                body.append(self.inline(line))
        return "\n\n".join(body) + "\n"

    def render_dedication(self) -> str:
        source_dir = self.translation_dir if self.edition == "zh" else self.markdown_dir
        lines = (source_dir / "000-front-matter.md").read_text(encoding="utf-8").splitlines()
        active = False
        body: list[str] = []
        for line in lines:
            marker = re.match(r"<!-- source-xhtml:\s*([^, .]+)", line)
            if marker:
                active = Path(marker.group(1)).stem.lower() == "ded01"
                continue
            if active and line.strip() and not line.startswith("<!--"):
                body.append(self.inline(line.rstrip()))
        return "#recto-start(running: [Dedication])\n#align(center + horizon)[" + "\\\n".join(body) + "]\n"

    def _front_section_pair(self, section: str) -> tuple[list[str], list[str]]:
        english = (self.markdown_dir / "000-front-matter.md").read_text(encoding="utf-8").splitlines()
        chinese = (self.translation_dir / "000-front-matter.md").read_text(encoding="utf-8").splitlines()
        en_out: list[str] = []
        zh_out: list[str] = []
        active = False
        for index, line in enumerate(english):
            marker = re.match(r"<!-- source-xhtml:\s*([^, .]+)", line)
            if marker:
                active = Path(marker.group(1)).stem.lower() == section
                continue
            if active:
                en_out.append(line)
                zh_out.append(chinese[index])
        return en_out, zh_out

    def render_copyright_pair(self) -> str:
        english, chinese = self._front_section_pair("copyright")
        body: list[str] = []
        index = 0
        while index < len(english):
            if not english[index].strip() or english[index].startswith("<!--"):
                index += 1
                continue
            image = re.fullmatch(r"!\[(.*)\]\(\.\./images/([^\)]+)\)", english[index])
            if image:
                zh_image = re.fullmatch(r"!\[(.*)\]\(\.\./images/([^\)]+)\)", chinese[index])
                alt_zh = zh_image.group(1) if zh_image else image.group(1)
                body.append(self._dual_image_value(image.group(1), alt_zh, image.group(2), None))
                index += 1
                continue
            en_para = [english[index]]
            zh_para = [chinese[index]]
            index += 1
            while index < len(english) and english[index].strip() and not english[index].startswith("<!--"):
                if re.fullmatch(r"!\[(.*)\]\(\.\./images/([^\)]+)\)", english[index]):
                    break
                en_para.append(english[index])
                zh_para.append(chinese[index])
                index += 1
            body.append(self.dual_paragraph(en_para, zh_para))
        return "\n\n".join(body) + "\n"

    def _dual_image_value(self, alt_en: str, alt_zh: str, asset: str, label: str | None) -> str:
        prefix = f"<{label}>" if label else ""
        if not alt_en or alt_en.lower() == "image":
            caption = "none"
        else:
            en_alt, zh_alt = self.dual_inline(alt_en, alt_zh)
            caption = f"dual-caption([{en_alt}], [{zh_alt}])"
        return f'{prefix}#fig("/assets/figures/{asset}", caption: {caption}, width: {"75%" if asset == "04fig07.jpg" else "100%"}, floating: {str("[^" not in alt_en).lower()})'

    def render_dedication_pair(self) -> str:
        english, chinese = self._front_section_pair("ded01")
        body: list[str] = []
        for en_line, zh_line in zip(english, chinese):
            if not en_line.strip() or en_line.startswith("<!--"):
                continue
            en, zh = self.dual_inline(en_line.rstrip(), zh_line.rstrip())
            body.append(f"#dual-caption([{en}], [{zh}])")
        return "#recto-start(running: [Dedication])\n#align(center + horizon)[" + "\\\n".join(body) + "]\n"

    def write_main(self) -> None:
        display_title = "系统性能：企业与云计算" if self.edition == "zh" else BOOK_TITLE
        edition_label = release_status(self.workspace, self.edition)['edition_label']
        main = f'''// {BOOK_TITLE} · {self.edition} edition
// Generated from the audited Markdown boundary; see source-map.json and editorial/content-audit.
#import "template.typ": book
#import "core.typ": *
#import "matter.typ": *
#import "covers.typ": source-cover, boliu-cover

#show: book
#set document(title: "Systems Performance · Second Edition · {self.edition} study edition", author: ("Brendan Gregg",), description: "Unofficial study typesetting; {edition_label}", keywords: ("Systems Performance", "Enterprise and the Cloud", "Second Edition", "{self.edition}"))

#source-cover(
  [{self.inline(BOOK_TITLE)}],
  [{literal(AUTHOR)}],
  [{literal("Pearson second edition · print-cover source") }],
  original-cover: "/assets/covers/source/source-cover-print.jpeg",
)
#boliu-cover(
  [{self.inline(display_title)}],
  [{literal(AUTHOR)}],
  [{literal("Pearson second edition · print-cover source") }],
  [{literal(edition_label)}],
  bilingual: {str(self.edition == "dual").lower()},
  artwork: "/assets/covers/boliu/monet-the-japanese-footbridge-1899.jpg",
  artwork-credit: [Claude Monet, The Japanese Footbridge (1899); Courtesy National Gallery of Art, Washington; CC0.],
)

#copyright-page[
  #include "chapters/copyright.typ"
]
#toc-page(title: [{self.inline("目录" if self.edition == "zh" else "Contents")}], depth: 3)

#include "chapters/dedication.typ"
#include "chapters/front-matter.typ"
'''
        for i in range(1, 17):
            main += f'#include "chapters/chapter-{i:02}.typ"\n'
        for letter in "abcde":
            main += f'#include "chapters/appendix-{letter}.typ"\n'
        main += '#include "chapters/glossary.typ"\n#include "chapters/index.typ"\n#recto-start(running: [Back Matter / 后附文])\n#include "chapters/back-matter-01.typ"\n#include "chapters/back-matter-02.typ"\n#include "chapters/back-matter-03.typ"\n'
        (self.edition_dir / "book/main.typ").write_text(main, encoding="utf-8")

    def run(self) -> None:
        self.collect_footnotes()
        self.prepare_tree()
        self.write_content()
        if any(count != 1 for count in self.annotation_emissions.values()):
            raise ValueError(f"Missing or duplicate editorial annotation emission: {self.annotation_emissions}")
        self.write_main()
        print(json.dumps({"edition": self.edition, "chapters": len(SOURCE_FILES), "images": len(self.image_manifest), "footnotes": len(self.footnotes), "code_blocks": self.code_index}, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", choices=("en", "dual", "zh"), default=None)
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parents[4]
    editions = (args.edition,) if args.edition else ("en", "dual", "zh")
    for edition in editions:
        TypstRenderer(workspace, edition).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
