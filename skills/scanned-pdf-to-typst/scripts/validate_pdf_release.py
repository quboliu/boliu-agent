#!/usr/bin/env python3
"""Validate a generated PDF against its reproducibility and visual QA records.

This validator intentionally does not call pdfinfo.  It tries PyMuPDF first,
then pypdf/PyPDF2, and finally uses a small PDF object-tree fallback so a
minimal Python installation can still report an explicit diagnostic.  The
fallback is not a text extractor; it only checks page-tree counts and common
searchability markers.

Record schema (JSON)::

    {
      "pdf": {"sha256": "...", "page_count": 123},
      "typst_version": "typst 0.15.1",
      "build_command": "typst compile ...",
      "creation_timestamp": {"policy": "SOURCE_DATE_EPOCH", "value": 0}
    }

Visual manifests contain ``samples`` with ``filename``, ``output_page`` and
``semantic_class``.  A report may contain the same list under
``visual_review.samples``.  The two lists must match exactly and files must
exist.  Code samples additionally state whether an unfenced OCR candidate was
confirmed into raw typesetting or retained as ordinary text. This makes a
visual claim traceable without tying the skill to one project's report format.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_pdf(path: Path) -> tuple[int, dict[str, Any]]:
    """Return page count and parser/readability evidence, without pdfinfo."""
    diagnostics: list[str] = []

    try:
        import fitz  # type: ignore

        document = fitz.open(path)
        pages = len(document)
        text_lengths = [len(page.get_text()) for page in document]
        document.close()
        return pages, {
            "parser": "pymupdf",
            "readability": {
                "method": "pymupdf-text-extraction",
                "pages_with_text": sum(n > 0 for n in text_lengths),
                "text_characters": sum(text_lengths),
                "searchable": any(n > 0 for n in text_lengths),
            },
            "diagnostics": diagnostics,
        }
    except ImportError:
        diagnostics.append("PyMuPDF unavailable; trying pypdf/PyPDF2")
    except Exception as exc:  # pragma: no cover - environment-specific
        diagnostics.append(f"PyMuPDF failed: {type(exc).__name__}: {exc}")

    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = __import__(module_name)
            reader = module.PdfReader(str(path))
            lengths = [len(page.extract_text() or "") for page in reader.pages]
            return len(reader.pages), {
                "parser": module_name,
                "readability": {
                    "method": f"{module_name}-text-extraction",
                    "pages_with_text": sum(n > 0 for n in lengths),
                    "text_characters": sum(lengths),
                    "searchable": any(n > 0 for n in lengths),
                },
                "diagnostics": diagnostics,
            }
        except ImportError:
            diagnostics.append(f"{module_name} unavailable")
        except Exception as exc:  # pragma: no cover - environment-specific
            diagnostics.append(f"{module_name} failed: {type(exc).__name__}: {exc}")

    # Last resort: parse the page-tree count from the PDF bytes.  This is
    # deliberately labelled as a fallback and is never presented as text
    # extraction or a substitute for a real Python PDF parser.
    data = path.read_bytes()
    counts = [int(item) for item in re.findall(rb"/Count\s+(\d+)", data)]
    pages = max(counts, default=0)
    has_unicode_map = b"/ToUnicode" in data
    has_text_operators = bool(re.search(rb"\bBT\b|\bTj\b|\bTJ\b", data))
    diagnostics.append("No supported Python PDF parser installed; used PDF object-tree fallback")
    return pages, {
        "parser": "python-pdf-object-tree-fallback",
        "readability": {
            "method": "pdf-byte-markers-only",
            "pages_with_text": None,
            "text_characters": None,
            "searchable": bool(pages and (has_unicode_map or has_text_operators)),
            "evidence": {"tounicode": has_unicode_map, "text_operators": has_text_operators},
        },
        "diagnostics": diagnostics,
    }


def record_value(record: dict[str, Any], name: str) -> Any:
    pdf = record.get("pdf")
    if isinstance(pdf, dict) and name in pdf:
        return pdf[name]
    aliases = {"sha256": ("pdf_sha256", "sha256"), "page_count": ("pages", "pdf_pages")}
    for alias in aliases.get(name, ()):
        if alias in record:
            return record[alias]
    return None


def sample_key(sample: dict[str, Any]) -> tuple[str, int, str, str]:
    try:
        page = int(sample.get("output_page", sample.get("page", 0)))
    except (TypeError, ValueError):
        page = 0
    return (
        str(sample.get("filename", "")),
        page,
        str(sample.get("semantic_class", "")),
        str(sample.get("code_treatment", "")),
    )


def validate_visual_manifest(path: Path, report_path: Path | None, pdf_pages: int) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    manifest = json.loads(path.read_text(encoding="utf-8"))
    samples = manifest.get("samples")
    if not isinstance(samples, list) or not samples:
        return ["visual manifest must contain a non-empty samples list"], {"samples": 0}
    keys: list[tuple[str, int, str, str]] = []
    for index, sample in enumerate(samples):
        if not isinstance(sample, dict):
            errors.append(f"visual sample {index} is not an object")
            continue
        missing = [field for field in ("filename", "output_page", "semantic_class") if field not in sample]
        if missing:
            errors.append(f"visual sample {index} missing: {', '.join(missing)}")
            continue
        key = sample_key(sample)
        keys.append(key)
        candidate = Path(key[0])
        if not candidate.is_absolute():
            candidate = path.parent / candidate
        if not candidate.exists():
            errors.append(f"visual sample file missing: {key[0]}")
        if key[1] < 1:
            errors.append(f"visual sample output_page must be >= 1: {key[0]}")
        elif key[1] > pdf_pages:
            errors.append(f"visual sample output_page exceeds PDF page count ({pdf_pages}): {key[0]}")
        if "code" in key[2].lower() and sample.get("code_treatment") not in {"confirmed-raw", "retained-ordinary-text"}:
            errors.append(
                f"code sample must declare code_treatment confirmed-raw or retained-ordinary-text: {key[0]}"
            )
    if len(set(keys)) != len(keys):
        errors.append("visual manifest contains duplicate filename/page/class entries")
    classes = " ".join(key[2].lower() for key in keys)
    if not re.search(r"cover|title", classes):
        errors.append("visual samples lack a cover/title semantic class")
    if not re.search(r"code|dense|technical", classes):
        errors.append("visual samples lack a code/technical-dense semantic class")
    if report_path:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        reported = report.get("visual_review", {}).get("samples", report.get("samples"))
        if not isinstance(reported, list):
            errors.append("visual report must contain visual_review.samples (or samples)")
        else:
            report_keys = [sample_key(item) for item in reported if isinstance(item, dict)]
            if report_keys != keys:
                errors.append("visual report samples do not exactly match manifest samples")
    return errors, {"samples": len(keys), "semantic_classes": sorted(set(key[2] for key in keys))}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--visual-manifest", required=True, type=Path)
    parser.add_argument("--visual-report", type=Path)
    parser.add_argument("--report", type=Path, help="write the machine-readable validation report here")
    args = parser.parse_args()

    errors: list[str] = []
    if not args.pdf.is_file():
        errors.append(f"PDF not found: {args.pdf}")
        result = {"ok": False, "errors": errors}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    actual_sha = sha256(args.pdf)
    page_count, parser_evidence = read_pdf(args.pdf)
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read release record: {exc}")
        result = {"ok": False, "errors": errors}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    if not isinstance(record, dict):
        errors.append("release record must be a JSON object")
        result = {"ok": False, "errors": errors}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    expected_sha = record_value(record, "sha256")
    expected_pages = record_value(record, "page_count")
    for field, value in (("pdf.sha256", expected_sha), ("pdf.page_count", expected_pages), ("typst_version", record.get("typst_version")), ("build_command", record.get("build_command"))):
        if value in (None, ""):
            errors.append(f"release record missing {field}")
    timestamp = record.get("creation_timestamp", record.get("time_strategy", record.get("timestamp_policy")))
    if timestamp in (None, ""):
        errors.append("release record missing creation timestamp/time strategy")
    if expected_sha and expected_sha != actual_sha:
        errors.append(f"PDF SHA-256 mismatch: record={expected_sha} actual={actual_sha}")
    if expected_pages is not None and int(expected_pages) != page_count:
        errors.append(f"PDF page-count mismatch: record={expected_pages} actual={page_count}")
    if page_count < 1:
        errors.append("Python PDF parser/fallback could not determine a positive page count")
    try:
        visual_errors, visual_evidence = validate_visual_manifest(args.visual_manifest, args.visual_report, page_count)
    except (OSError, json.JSONDecodeError) as exc:
        visual_errors = [f"cannot read visual validation input: {exc}"]
        visual_evidence = {"samples": 0}
    errors.extend(visual_errors)
    result = {
        "ok": not errors,
        "pdf": {"path": str(args.pdf), "sha256": actual_sha, "page_count": page_count, **parser_evidence},
        "record": {"expected_sha256": expected_sha, "expected_page_count": expected_pages, "typst_version": record.get("typst_version"), "build_command": record.get("build_command"), "creation_timestamp": timestamp},
        "visual": visual_evidence,
        "errors": errors,
    }
    if args.report:
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
