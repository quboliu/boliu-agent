#!/usr/bin/env python3
"""Check the reviewed B5 geometry and opener-furniture landmarks.

Detect all semantic opener landmarks in the emitted PDF, check physical parity
and furniture. Historical positions are optional regression assertions for
changes that explicitly preserve pagination.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pymupdf as fitz


EXPECTED_BY_EDITION = {
    "en": {
        "dedication": 31,
        "preface": 33,
        "acknowledgments": 41,
        "about-the-author": 45,
        "chapter-01": 47,
        "chapter-02": 71,
        "chapter-03": 147,
        "chapter-04": 191,
        "chapter-05": 235,
        "chapter-06": 287,
        "chapter-07": 381,
        "chapter-08": 441,
        "chapter-09": 509,
        "chapter-10": 591,
        "chapter-11": 679,
        "chapter-12": 749,
        "chapter-13": 781,
        "chapter-14": 817,
        "chapter-15": 867,
        "chapter-16": 903,
        "appendix-a": 915,
        "appendix-b": 927,
        "appendix-c": 931,
        "appendix-d": 939,
        "appendix-e": 941,
        "glossary": 947,
        "index": 959,
    },
    "zh": {
        "dedication": 31,
        "preface": 33,
        "acknowledgments": 39,
        "about-the-author": 41,
        "chapter-01": 43,
        "chapter-02": 63,
        "chapter-03": 123,
        "chapter-04": 161,
        "chapter-05": 211,
        "chapter-06": 263,
        "chapter-07": 363,
        "chapter-08": 425,
        "chapter-09": 499,
        "chapter-10": 587,
        "chapter-11": 683,
        "chapter-12": 751,
        "chapter-13": 779,
        "chapter-14": 831,
        "chapter-15": 901,
        "chapter-16": 943,
        "appendix-a": 959,
        "appendix-b": 969,
        "appendix-c": 973,
        "appendix-d": 987,
        "appendix-e": 989,
        "glossary": 993,
        "index": 1003,
    },
    "dual": {
        "dedication": 49,
        "preface": 51,
        "acknowledgments": 65,
        "about-the-author": 71,
        "chapter-01": 73,
        "chapter-02": 111,
        "chapter-03": 231,
        "chapter-04": 305,
        "chapter-05": 375,
        "chapter-06": 461,
        "chapter-07": 607,
        "chapter-08": 703,
        "chapter-09": 809,
        "chapter-10": 937,
        "chapter-11": 1073,
        "chapter-12": 1183,
        "chapter-13": 1239,
        "chapter-14": 1289,
        "chapter-15": 1361,
        "chapter-16": 1415,
        "appendix-a": 1433,
        "appendix-b": 1455,
        "appendix-c": 1461,
        "appendix-d": 1471,
        "appendix-e": 1475,
        "glossary": 1483,
        "index": 1501,
    },
}


def first_lines(page: fitz.Page) -> list[str]:
    return [line.strip() for line in page.get_text().splitlines() if line.strip()]


def detect(lines: list[str]) -> str | None:
    if any(line.startswith(("For Deirdré Straughan", "献给")) for line in lines[:8]):
        return "dedication"
    # Contents pages repeat the names of nearly every later section.  They are
    # not physical openers, so do not classify headings found on those pages.
    is_contents = any(line in {"Contents", "目录"} for line in lines[:2])
    if is_contents:
        return None
    for key, title in (
        ("preface", ("Preface", "前言")),
        ("acknowledgments", ("Acknowledgments", "致谢")),
        ("about-the-author", ("About the Author", "关于作者", "作者简介")),
        ("glossary", ("Glossary", "术语表")),
        ("index", ("Index", "索引")),
    ):
        if any(title_line in lines[:5] for title_line in title):
            return key
    for line in lines[:8]:
        chapter = re.fullmatch(r"CHAPTER\s+(\d+)", line)
        if chapter:
            return f"chapter-{int(chapter.group(1)):02}"
        chapter = re.fullmatch(r"第\s*(\d+)\s*章", line)
        if chapter:
            return f"chapter-{int(chapter.group(1)):02}"
        appendix = re.match(r"(?:Appendix|附录)\s+([A-E])(?:\s|—|$)", line)
        if appendix:
            return f"appendix-{appendix.group(1).lower()}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--edition", choices=("en", "zh", "dual"))
    parser.add_argument("--strict-baseline", action="store_true", help="Require historical page positions for a change that preserves pagination")
    args = parser.parse_args()

    edition_match = re.search(r"-typst-(en|zh|dual)(?:[/\\]|$)", str(args.pdf))
    edition = args.edition or (edition_match.group(1) if edition_match else "en")
    expected = EXPECTED_BY_EDITION[edition]

    doc = fitz.open(args.pdf)
    errors: list[str] = []
    page_width_mm = doc[0].rect.width * 25.4 / 72
    page_height_mm = doc[0].rect.height * 25.4 / 72
    if abs(page_width_mm - 176) > 0.2 or abs(page_height_mm - 250) > 0.2:
        errors.append(f"page size {page_width_mm:.3f}x{page_height_mm:.3f}mm is not 176x250mm")

    detected: dict[str, int] = {}
    bookmarked_openers = {entry[2] for entry in doc.get_toc() if entry[0] == 1}
    for index, page in enumerate(doc, start=1):
        key = detect(first_lines(page))
        if index not in bookmarked_openers and key != "dedication":
            continue
        if key and key in expected and key not in detected:
            detected[key] = index

    for key, expected_page in expected.items():
        actual = detected.get(key)
        if actual is None or (args.strict_baseline and actual != expected_page):
            errors.append(f"{key}: expected physical page {expected_page}, found {actual}")
        if actual is not None and actual % 2 == 0:
            errors.append(f"{key}: opener is even physical page {actual}")

    opener_pages = sorted(detected.values())
    for page_number in opener_pages:
        lines = first_lines(doc[page_number - 1])
        if lines and lines[0] == "Systems Performance":
            errors.append(f"page {page_number}: running head was not suppressed")
        number_blocks = [
            block
            for block in doc[page_number - 1].get_text("blocks")
            if block[4].strip() == str(page_number)
        ]
        if not number_blocks:
            errors.append(f"page {page_number}: centered physical folio is missing")
        else:
            x0, _, x1, _, *_ = number_blocks[-1]
            center = (x0 + x1) / 2
            if abs(center - doc[page_number - 1].rect.width / 2) > 30:
                errors.append(f"page {page_number}: folio is not centered (x={center:.1f})")

    report = {
        "pdf": str(args.pdf),
        "pages": doc.page_count,
        "page_size_mm": [round(page_width_mm, 3), round(page_height_mm, 3)],
        "edition": edition,
        "historical_openers": expected,
        "strict_baseline": args.strict_baseline,
        "detected_openers": detected,
        "errors": errors,
        "status": "pass" if not errors else "fail",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
