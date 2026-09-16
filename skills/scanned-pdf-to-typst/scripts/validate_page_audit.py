#!/usr/bin/env python3
"""Validate one final source-page status record per source page."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


OPEN_STATUSES = {"open", "pending", "unresolved", "needs-review", "needs_review"}
PAGE_KEYS = ("page", "source_page", "page_number")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check a final page-status JSON/JSONL ledger for exact source-page "
            "coverage, duplicate pages, and unresolved statuses."
        )
    )
    parser.add_argument(
        "--records",
        required=True,
        type=Path,
        help="JSONL ledger, JSON list, or JSON object with a records list.",
    )
    parser.add_argument(
        "--page-count",
        required=True,
        type=int,
        help="Expected source PDF page count.",
    )
    parser.add_argument(
        "--allow-unresolved",
        action="store_true",
        help="Report rather than fail unresolved or pending records.",
    )
    return parser.parse_args()


def load_records(path: Path) -> list[dict[str, Any]]:
    payload = path.read_text(encoding="utf-8").strip()
    if not payload:
        raise ValueError("records file is empty")

    try:
        decoded = json.loads(payload)
    except json.JSONDecodeError:
        records: list[dict[str, Any]] = []
        for line_number, line in enumerate(payload.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid JSONL at line {line_number}: {error}") from error
            if not isinstance(item, dict):
                raise ValueError(f"JSONL line {line_number} is not an object")
            records.append(item)
        return records

    if isinstance(decoded, list):
        records = decoded
    elif isinstance(decoded, dict) and isinstance(decoded.get("records"), list):
        records = decoded["records"]
    else:
        raise ValueError("JSON input must be a list or an object with a records list")

    if not all(isinstance(item, dict) for item in records):
        raise ValueError("every record must be a JSON object")
    return records


def page_for(record: dict[str, Any], index: int) -> int:
    for key in PAGE_KEYS:
        if key in record:
            value = record[key]
            try:
                page = int(value)
            except (TypeError, ValueError) as error:
                raise ValueError(f"record {index} has non-integer {key}: {value!r}") from error
            return page
    keys = ", ".join(PAGE_KEYS)
    raise ValueError(f"record {index} lacks a page key; expected one of: {keys}")


def main() -> int:
    args = parse_args()
    if args.page_count < 1:
        print("ERROR: --page-count must be positive", file=sys.stderr)
        return 2
    if not args.records.is_file():
        print(f"ERROR: records file not found: {args.records}", file=sys.stderr)
        return 2

    try:
        records = load_records(args.records)
        pages = [page_for(record, index) for index, record in enumerate(records, start=1)]
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    counts = Counter(pages)
    expected = set(range(1, args.page_count + 1))
    actual = set(pages)
    missing = sorted(expected - actual)
    out_of_range = sorted(actual - expected)
    duplicates = sorted(page for page, count in counts.items() if count > 1)
    unresolved = [
        (page_for(record, index), record.get("status"))
        for index, record in enumerate(records, start=1)
        if str(record.get("status", "")).strip().lower() in OPEN_STATUSES
    ]

    print(
        json.dumps(
            {
                "records": len(records),
                "expected_pages": args.page_count,
                "covered_pages": len(actual & expected),
                "missing_pages": missing,
                "duplicate_pages": duplicates,
                "out_of_range_pages": out_of_range,
                "unresolved": unresolved,
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    failed = bool(missing or duplicates or out_of_range)
    if unresolved and not args.allow_unresolved:
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
