#!/usr/bin/env python3
"""Build a reviewable bilingual draft from a Kubernetes zh-cn source file.

Kubernetes' zh-cn Markdown keeps the corresponding English source blocks in
multiline HTML comments. This tool exposes those blocks and places the official
Chinese translation immediately after each English block. It deliberately
produces a draft: Hugo shortcodes and source includes are left visible for the
manual audit stage.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PAIR_RE = re.compile(r"<!--[ \t]*\n(.*?)\n[ \t]*-->", re.DOTALL)
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
ONE_LINE_COMMENT_RE = re.compile(r"<!--(?!\n).*?-->", re.DOTALL)


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def is_commented_frontmatter(block: str) -> bool:
    compact = block.strip()
    return compact.startswith("title:") and "content_type:" in compact


def clean_between(text: str) -> str:
    text = ONE_LINE_COMMENT_RE.sub("", text)
    return text.strip()


def quote_markdown(text: str) -> str:
    lines = text.strip().splitlines()
    if not lines:
        return ""
    return "\n".join(">" if not line else f"> {line}" for line in lines)


def heading_parts(text: str) -> tuple[str, str] | None:
    lines = text.strip().splitlines()
    if not lines:
        return None
    match = re.match(r"^(#{1,6})\s+(.+?)\s*(?:\{#[^}]+\}|\{[^}]+\})?\s*$", lines[0])
    if not match:
        return None
    return match.group(1), match.group(2).strip()


def remove_first_line(text: str) -> str:
    lines = text.strip().splitlines()
    return "\n".join(lines[1:]).strip()


def render_pair(english: str, chinese: str) -> str:
    english = english.strip()
    chinese = chinese.strip()
    en_heading = heading_parts(english)
    zh_heading = heading_parts(chinese)

    if en_heading and zh_heading and en_heading[0] == zh_heading[0]:
        level, en_title = en_heading
        _, zh_title = zh_heading
        body_en = remove_first_line(english)
        body_zh = remove_first_line(chinese)
        parts = [f"{level} {en_title}｜{zh_title}"]
        if body_en:
            parts.append(body_en)
        if body_zh:
            parts.append(quote_markdown(body_zh))
        return "\n\n".join(parts)

    parts = [english]
    if chinese:
        parts.append(quote_markdown(chinese))
    return "\n\n".join(parts)


def convert(source: str) -> str:
    body = strip_frontmatter(source)
    matches = list(PAIR_RE.finditer(body))
    rendered: list[str] = []

    for index, match in enumerate(matches):
        english = match.group(1)
        if is_commented_frontmatter(english):
            continue
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        chinese = clean_between(body[match.end() : next_start])
        if not english.strip() or not chinese:
            continue
        rendered.append(render_pair(english, chinese))

    return "\n\n".join(rendered).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source = args.source.read_text(encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(convert(source), encoding="utf-8")


if __name__ == "__main__":
    main()
