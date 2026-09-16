#!/usr/bin/env python3
"""Mechanical release checks for a Typst book project.

Validates the source map, derived files, asset paths and actual parsed PDF.
Requires PyMuPDF. Compilation, content review and duplex visual proof are
separate gates. Adapted from the retired chinese-typst-book validator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import pymupdf
from pathlib import Path
from typing import Any


# Reserved project marker, not ordinary prose/code words such as TODO/FIXME.
# It is intentionally detected even in comments: remove it only after resolution.
PLACEHOLDER_RE = re.compile(r"\bBOLIU-UNRESOLVED\b")


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
    extensions: tuple[str, ...] = (".md", ".html", ".htm"),
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

    if not chapters:
        fail("manifest has no chapters", failures)
    source_names: set[str] = set()
    for index, chapter in enumerate(chapters, start=1):
        if not isinstance(chapter, dict):
            fail(f"chapter entry {index} is not an object", failures)
            continue
        source = chapter.get("source")
        output = chapter.get("output")
        if not isinstance(source, str) or not source:
            fail(f"chapter entry {index} has no source", failures)
        else:
            source_names.add(source)
            if source_dir is not None and not (source_dir / source).is_file():
                fail(f"source file does not exist: {source_dir / source}", failures)
            digest = chapter.get("source_sha256")
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                fail(f"missing or invalid source_sha256: {source}; regenerate manifest", failures)
            elif source_dir is None:
                fail(f"source directory required to verify hash: {source}", failures)
            elif (source_dir / source).is_file():
                actual = hashlib.sha256((source_dir / source).read_bytes()).hexdigest()
                if actual != digest:
                    fail(f"source hash mismatch: {source}; regenerate derived outputs", failures)
        if not isinstance(output, str) or not output:
            fail(f"chapter entry {index} has no output", failures)
        else:
            output_path = relative_path(book_dir, output)
            if output_path is None or not output_path.is_file():
                fail(f"generated chapter does not exist: {output}", failures)

    if source_dir is not None:
        excluded = manifest.get("excluded_sources", [])
        if not isinstance(excluded, list) or not all(isinstance(x, str) for x in excluded):
            fail("excluded_sources must be a list of relative source paths", failures)
            excluded = []
        expected = {
            path.relative_to(source_dir).as_posix()
            for path in source_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in extensions
            and path.relative_to(source_dir).as_posix() not in excluded
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
        elif width <= 0 or height <= 0:
            fail(f"invalid image dimensions ({width}x{height}): {asset}", failures)

    return len(chapters), asset_count


def check_generated_text(book_dir: Path, failures: list[str]) -> tuple[int, int]:
    source_root = book_dir / "book"
    if not source_root.is_dir():
        source_root = book_dir
    typst_files = sorted(path for path in source_root.rglob("*.typ")
                         if not {"output", "build", "dist"}.intersection(path.relative_to(source_root).parts))
    if not typst_files:
        fail(f"no Typst files found under {book_dir}", failures)
        return 0, 0
    placeholders: list[str] = []
    for path in typst_files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            fail(f"cannot read generated file {path}: {exc}", failures)
            continue
        if PLACEHOLDER_RE.search(text):
            placeholders.append(str(path))
    if placeholders:
        fail("placeholders remain in generated Typst: " + ", ".join(placeholders), failures)
    return len(typst_files), len(placeholders)


def check_pdf(
    pdf_path: Path,
    failures: list[str],
    page_size_mm: tuple[float, float] = (176, 250),
) -> int:
    if not pdf_path.is_file():
        fail(f"missing PDF: {pdf_path}", failures)
        return 0
    try:
        with pymupdf.open(pdf_path) as doc:
            if doc.needs_pass:
                fail("PDF requires a password", failures)
                return 0
            if doc.is_repaired:
                fail("PDF required structural repair", failures)
            if len(doc) < 2:
                fail("Book PDF must include the two cover pages", failures)
            searchable = False
            checked_fonts = set()
            for index, page in enumerate(doc, 1):
                expected = [mm * 72 / 25.4 for mm in page_size_mm]
                if any(abs(a - b) > 0.2 for a, b in zip(
                        (page.rect.width, page.rect.height), expected)):
                    fail(f"page {index}: unexpected trim or rotation", failures)
                text = page.get_text()
                searchable |= bool(text.strip()) and index > 2
                if "NOT FOR RELEASE" in text:
                    fail(f"page {index}: publisher artwork still a fixture", failures)
                for word in page.get_text("words"):
                    if word[0] < -0.5 or word[1] < -0.5 or word[2] > page.rect.width + 0.5 or word[3] > page.rect.height + 0.5:
                        fail(f"page {index}: text exceeds page bounds", failures)
                        break
                for font in page.get_fonts():
                    xref = font[0]
                    if xref in checked_fonts:
                        continue
                    checked_fonts.add(xref)
                    if not xref or not doc.extract_font(xref)[3]:
                        fail(f"page {index}: font not embedded: {font[3]}", failures)
            if not searchable:
                fail("No searchable body text after covers", failures)
            return len(doc)
    except Exception as exc:
        fail(f"cannot parse PDF: {exc}", failures)
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-dir", required=True, type=Path)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--page-size-mm", type=float, nargs=2, default=(176, 250))
    parser.add_argument("--source-extensions", nargs="+", default=[".md", ".html", ".htm"])
    parser.add_argument(
        "--require-a4",
        action="store_true",
        help="require every page to use the exact A4 media box",
    )
    args = parser.parse_args()

    book_dir = args.book_dir.resolve()
    source_dir = (args.source_dir or book_dir / "source").resolve()
    manifest = (args.manifest or book_dir / "source" / "source-map.json").resolve()
    pdf = (args.pdf or book_dir / "output" / "build" / "book.pdf").resolve()
    failures: list[str] = []

    chapter_count, asset_count = check_manifest(book_dir, source_dir, manifest, failures,
                                               tuple(args.source_extensions))
    typst_count, issue_count = check_generated_text(book_dir, failures)
    page_count = check_pdf(pdf, failures, page_size_mm=(210, 297) if args.require_a4 else args.page_size_mm)

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
