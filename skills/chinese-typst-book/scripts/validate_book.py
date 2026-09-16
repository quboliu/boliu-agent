#!/usr/bin/env python3
"""Mechanical release checks for a Typst book project.

The script intentionally uses only the Python standard library so it can run in
a clean checkout. It validates the source map, derived files, asset paths, and
basic PDF integrity; Typst compilation and visual review remain separate gates.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PLACEHOLDER_RE = re.compile(
    r"(?i)(?:\bTODO\b|\[TODO\]|\bPLACEHOLDER\b|\bFIXME\b|"
    r"!\[\[.*?\]\])"
)
PAGE_RE = re.compile(rb"/Type\s*/Page\b")
A4_MEDIA_BOX_RE = re.compile(
    rb"/MediaBox\s*\[\s*0\s+0\s+595\.2756\s+841\.8898\s*\]"
)


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def load_json(path: Path, failures: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        fail(f"missing manifest: {path}", failures)
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read manifest {path}: {exc}", failures)
        return None
    if not isinstance(value, dict):
        fail(f"manifest must be a JSON object: {path}", failures)
        return None
    return value


def relative_path(book_dir: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    candidate = Path(value)
    return candidate if candidate.is_absolute() else book_dir / candidate


def check_manifest(
    book_dir: Path,
    source_dir: Path | None,
    manifest_path: Path,
    failures: list[str],
) -> tuple[int, int]:
    manifest = load_json(manifest_path, failures)
    if manifest is None:
        return 0, 0

    chapters = manifest.get("chapters", [])
    images = manifest.get("images", [])
    if not isinstance(chapters, list):
        fail("manifest.chapters must be a list", failures)
        chapters = []
    if not isinstance(images, list):
        fail("manifest.images must be a list", failures)
        images = []

    orders: list[int] = []
    source_names: set[str] = set()
    output_names: set[str] = set()
    for index, chapter in enumerate(chapters, start=1):
        if not isinstance(chapter, dict):
            fail(f"chapter entry {index} is not an object", failures)
            continue
        source = chapter.get("source")
        output = chapter.get("output")
        order = chapter.get("order", index)
        if not isinstance(source, str) or not source:
            fail(f"chapter entry {index} has no source", failures)
        else:
            if source in source_names:
                fail(f"duplicate chapter source: {source}", failures)
            source_names.add(source)
            if source_dir is not None and not (source_dir / source).is_file():
                fail(f"source file does not exist: {source_dir / source}", failures)
        if not isinstance(output, str) or not output:
            fail(f"chapter entry {index} has no output", failures)
        else:
            if output in output_names:
                fail(f"duplicate chapter output: {output}", failures)
            output_names.add(output)
            output_path = relative_path(book_dir, output)
            if output_path is None or not output_path.is_file():
                fail(f"generated chapter does not exist: {output}", failures)
        if isinstance(order, int):
            orders.append(order)
        else:
            fail(f"chapter {source!r} has non-integer order", failures)

    if orders and orders != list(range(1, len(orders) + 1)):
        fail(f"chapter order is not contiguous: {orders}", failures)

    if source_dir is not None:
        expected = {
            path.relative_to(source_dir).as_posix()
            for path in source_dir.glob("*.md")
            if path.name != "SUMMARY.md"
        }
        missing = sorted(expected - source_names)
        extra = sorted(source_names - expected)
        if missing:
            fail("source files absent from manifest: " + ", ".join(missing), failures)
        if extra:
            fail("manifest names files outside source directory: " + ", ".join(extra), failures)

    asset_count = 0
    for index, image in enumerate(images, start=1):
        if not isinstance(image, dict):
            fail(f"image entry {index} is not an object", failures)
            continue
        asset = image.get("asset")
        if not isinstance(asset, str) or not asset:
            fail(f"image entry {index} has no asset path", failures)
            continue
        asset_path = relative_path(book_dir, asset)
        if asset_path is None or not asset_path.is_file():
            fail(f"image asset does not exist: {asset}", failures)
        else:
            asset_count += 1
        width = image.get("width")
        height = image.get("height")
        if not isinstance(width, int) or not isinstance(height, int):
            fail(f"image {asset!r} lacks integer dimensions", failures)
        elif width < 64 or height < 24:
            fail(f"image is suspiciously small ({width}x{height}): {asset}", failures)

    return len(chapters), asset_count


def check_generated_text(book_dir: Path, failures: list[str]) -> tuple[int, int]:
    typst_files = sorted(book_dir.rglob("*.typ"))
    if not typst_files:
        fail(f"no Typst files found under {book_dir}", failures)
        return 0, 0
    placeholders: list[str] = []
    raw_obisidian: list[str] = []
    for path in typst_files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            fail(f"cannot read generated file {path}: {exc}", failures)
            continue
        if PLACEHOLDER_RE.search(text):
            placeholders.append(str(path))
        if "![[" in text:
            raw_obisidian.append(str(path))
    if placeholders:
        fail("placeholders remain in generated Typst: " + ", ".join(placeholders), failures)
    if raw_obisidian:
        fail("raw Obsidian image syntax remains in generated Typst: " + ", ".join(raw_obisidian), failures)
    return len(typst_files), len(placeholders) + len(raw_obisidian)


def check_pdf(
    pdf_path: Path,
    failures: list[str],
    require_a4: bool = False,
) -> int:
    if not pdf_path.is_file():
        fail(f"missing PDF: {pdf_path}", failures)
        return 0
    try:
        data = pdf_path.read_bytes()
    except OSError as exc:
        fail(f"cannot read PDF {pdf_path}: {exc}", failures)
        return 0
    if len(data) < 10000:
        fail(f"PDF is unexpectedly small ({len(data)} bytes): {pdf_path}", failures)
    if not data.startswith(b"%PDF-"):
        fail(f"not a PDF file: {pdf_path}", failures)
    if b"%%EOF" not in data[-2048:]:
        fail(f"PDF has no EOF marker near its end: {pdf_path}", failures)
    pages = len(PAGE_RE.findall(data))
    if pages < 2:
        fail(f"PDF has implausible page count ({pages}): {pdf_path}", failures)
    if require_a4:
        a4_boxes = len(A4_MEDIA_BOX_RE.findall(data))
        if a4_boxes != pages:
            fail(
                f"expected A4 page boxes on every page, found {a4_boxes}/{pages}: {pdf_path}",
                failures,
            )
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-dir", required=True, type=Path)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument(
        "--require-a4",
        action="store_true",
        help="require every page to use the exact A4 media box",
    )
    args = parser.parse_args()

    book_dir = args.book_dir.resolve()
    source_dir = args.source_dir.resolve() if args.source_dir else None
    manifest = (args.manifest or book_dir / "source-map.json").resolve()
    pdf = (args.pdf or book_dir / "dist" / "book.pdf").resolve()
    failures: list[str] = []

    chapter_count, asset_count = check_manifest(book_dir, source_dir, manifest, failures)
    typst_count, issue_count = check_generated_text(book_dir, failures)
    page_count = check_pdf(pdf, failures, require_a4=args.require_a4)

    print(
        f"checked chapters={chapter_count} assets={asset_count} "
        f"typst_files={typst_count} pdf_pages={page_count}"
    )
    if failures:
        print("FAIL")
        for item in failures:
            print(f"- {item}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
