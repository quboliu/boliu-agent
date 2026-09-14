#!/usr/bin/env python3
"""Normalize Kubernetes website Hugo Markdown for a standalone blog draft.

This performs only lossless, mechanical rewrites. Shortcodes that inject
substantive content (glossary definitions, code samples, feature-state boxes,
figures, and third-party notices) remain for the article-specific audit.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TOOLTIP_RE = re.compile(r"\{\{<\s*glossary_tooltip\s+([^>]*?)\s*>\}\}", re.DOTALL)
PARAM_RE = re.compile(r"\{\{<\s*param\s+[\"']version[\"']\s*>\}\}")
SKEW_RE = re.compile(r"\{\{<\s*skew\s+currentVersion\s*>\}\}")
COMMENT_BLOCK_RE = re.compile(
    r"(?m)^>? ?\{\{<\s*/?comment\s*>\}\}\s*\n?"
)
NOTE_RE = re.compile(r"(?m)^(\s*>?\s*)\{\{<\s*(/)?(note|caution)\s*>\}\}\s*$")
TABLE_RE = re.compile(r"(?m)^>? ?\{\{<\s*/?table(?:\s+[^>]*)?\s*>\}\}\s*$")
ESCAPED_TABLE_RE = re.compile(r"(?m)^\{\{</\*\s*/?table(?:\s+.*?)?\s*\*/>\}\}\s*$")
WHATS_NEXT_RE = re.compile(r"(?m)^(>\s*)?(#{1,6})\s+\{\{%\s*heading\s+[\"']whatsnext[\"']\s*%\}\}\s*$")


def shortcode_attr(arguments: str, name: str) -> str | None:
    match = re.search(rf"\b{name}\s*=\s*([\"'])(.*?)\1", arguments, re.DOTALL)
    return match.group(2) if match else None


def tooltip_text(match: re.Match[str]) -> str:
    arguments = match.group(1)
    visible = shortcode_attr(arguments, "text") or shortcode_attr(arguments, "term_id")
    return visible or ""


def normalize(text: str, version: str) -> str:
    text = TOOLTIP_RE.sub(tooltip_text, text)
    text = PARAM_RE.sub(version, text)
    text = SKEW_RE.sub(version.removeprefix("v"), text)
    text = COMMENT_BLOCK_RE.sub("", text)

    def note_replacement(match: re.Match[str]) -> str:
        prefix, closing, kind = match.groups()
        if closing:
            return ""
        label = "**Caution｜注意**" if kind == "caution" else "**Note｜说明**"
        return f"{prefix}{label}" if prefix.strip() == ">" else label

    text = NOTE_RE.sub(note_replacement, text)
    text = TABLE_RE.sub("", text)
    text = ESCAPED_TABLE_RE.sub("", text)

    def whats_next(match: re.Match[str]) -> str:
        quote, level = match.groups()
        # A quoted form came from the Chinese half of the source. The paired
        # English heading was a shortcode too, so emit one bilingual heading.
        if quote:
            return f"{level} What's next｜接下来"
        return f"{level} What's next"

    text = WHATS_NEXT_RE.sub(whats_next, text)
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--version", default="v1.31")
    args = parser.parse_args()
    for path in args.paths:
        path.write_text(normalize(path.read_text(encoding="utf-8"), args.version), encoding="utf-8")


if __name__ == "__main__":
    main()
