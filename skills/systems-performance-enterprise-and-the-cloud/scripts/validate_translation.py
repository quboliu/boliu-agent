#!/usr/bin/env python3
"""Validate the Chinese Markdown sidecar against the immutable English boundary."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
from pathlib import Path


LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)")
IMAGE_RE = re.compile(r"!\[[^\]\n]*\]\(([^)\n]+)\)")
CODE_SPAN_RE = re.compile(r"`[^`\n]*`")
FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]]+)\]")
SENTINEL_RE = re.compile(r"XQZ[A-Z0-9]+QZX")


def footnote_definitions(lines: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in lines:
        match = re.match(r"^\[\^([^\]]+)\]:\s*(.*)$", line)
        if match:
            result[match.group(1)] = match.group(2)
    return result


def structural_prefix(line: str) -> str:
    heading = re.match(r"^(#{1,6})\s+", line)
    if heading:
        return heading.group(1)
    listing = re.match(r"^(\s*(?:[-*+] |\d+\. ))", line)
    if listing:
        return listing.group(1)
    return ""


def validate_file(source: Path, translation: Path) -> dict[str, object]:
    english = source.read_text(encoding="utf-8").splitlines()
    chinese = translation.read_text(encoding="utf-8").splitlines()
    errors: list[str] = []
    warnings: list[str] = []
    if len(english) != len(chinese):
        errors.append(f"line count {len(english)} != {len(chinese)}")

    source_ids = [line for line in english if line.startswith("<!-- source-id:")]
    translated_ids = [line for line in chinese if line.startswith("<!-- source-id:")]
    if source_ids != translated_ids:
        errors.append("source-id comments changed or reordered")

    in_code = False
    equal_lines = 0
    for index, (source_line, translated_line) in enumerate(zip(english, chinese), 1):
        if SENTINEL_RE.search(translated_line):
            errors.append(f"sentinel remains on line {index}")
        if source_line.startswith("<!--") and source_line != translated_line:
            errors.append(f"comment changed on line {index}")
        if source_line.startswith("```"):
            if source_line != translated_line:
                errors.append(f"code fence changed on line {index}")
            in_code = not in_code
            continue
        if in_code and source_line != translated_line:
            errors.append(f"code body changed on line {index}")
        if source_line == translated_line and source_line.strip():
            equal_lines += 1
        if source_line.startswith("|"):
            source_pipes = source_line.count("|")
            translated_pipes = translated_line.count("|")
            if source_pipes != translated_pipes:
                errors.append(f"table delimiters changed on line {index}")
        prefix = structural_prefix(source_line)
        if prefix and structural_prefix(translated_line) != prefix:
            errors.append(f"structural prefix changed on line {index}")

    source_links = LINK_RE.findall("\n".join(english))
    translated_links = LINK_RE.findall("\n".join(chinese))
    if source_links != translated_links:
        errors.append(f"link targets changed ({len(source_links)} != {len(translated_links)})")
    source_images = IMAGE_RE.findall("\n".join(english))
    translated_images = IMAGE_RE.findall("\n".join(chinese))
    if source_images != translated_images:
        errors.append(f"image targets changed ({len(source_images)} != {len(translated_images)})")
    source_code = CODE_SPAN_RE.findall("\n".join(english))
    translated_code = CODE_SPAN_RE.findall("\n".join(chinese))
    if source.name.endswith("index.md"):
        # Chinese index names place the owning tool before its command/function.
        # Allow that phrase order while guarding every literal on its own line.
        for index, (source_line, translated_line) in enumerate(zip(english, chinese), 1):
            if Counter(CODE_SPAN_RE.findall(source_line)) != Counter(CODE_SPAN_RE.findall(translated_line)):
                errors.append(f"index inline code changed on line {index}")
    elif source_code != translated_code:
        errors.append(f"inline code changed ({len(source_code)} != {len(translated_code)})")

    source_notes = footnote_definitions(english)
    translated_notes = footnote_definitions(chinese)
    if set(source_notes) != set(translated_notes):
        errors.append("footnote definition keys changed")
    source_refs = FOOTNOTE_REF_RE.findall("\n".join(english))
    translated_refs = FOOTNOTE_REF_RE.findall("\n".join(chinese))
    if sorted(source_refs) != sorted(translated_refs):
        errors.append("footnote reference keys changed")
    if not re.search(r"[\u3400-\u9fff]", "\n".join(chinese)):
        warnings.append("no CJK characters found")
    if equal_lines:
        warnings.append(f"{equal_lines} non-empty lines are unchanged (often code, names, or protected references)")
    return {
        "file": source.name,
        "source_lines": len(english),
        "translation_lines": len(chinese),
        "source_chars": len(source.read_text(encoding="utf-8")),
        "translation_chars": len(translation.read_text(encoding="utf-8")),
        "source_links": len(source_links),
        "source_images": len(source_images),
        "footnotes": len(source_notes),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--translation-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    reports: list[dict[str, object]] = []
    for source in sorted(args.source_dir.glob("*.md")):
        translation = args.translation_dir / source.name
        if not translation.exists():
            reports.append({"file": source.name, "errors": ["translation file missing"]})
            continue
        reports.append(validate_file(source, translation))
    result = {
        "schema": "systems-performance-enterprise-and-the-cloud/translation-validation/v1",
        "files": reports,
        "file_count": len(reports),
        "error_count": sum(len(item.get("errors", [])) for item in reports),
        "warning_count": sum(len(item.get("warnings", [])) for item in reports),
        "status": "pass" if all(not item.get("errors") for item in reports) else "fail",
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
