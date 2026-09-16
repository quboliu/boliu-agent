#!/usr/bin/env python3
"""Print one deterministic SHA-256 fingerprint for a skill directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def record(path: Path, root: Path) -> dict[str, str]:
    info = path.lstat()
    relative_path = path.relative_to(root).as_posix()
    mode = oct(stat.S_IMODE(info.st_mode))
    if path.is_symlink():
        return {
            "kind": "symlink",
            "mode": mode,
            "path": relative_path,
            "target": os.readlink(path),
        }
    if path.is_file():
        return {
            "kind": "file",
            "mode": mode,
            "path": relative_path,
            "sha256": file_digest(path),
        }
    raise ValueError(f"Unsupported entry in skill directory: {path}")


def fingerprint(root: Path) -> str:
    records: list[dict[str, str]] = []
    for directory, subdirectories, filenames in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        for name in list(subdirectories):
            candidate = directory_path / name
            if candidate.is_symlink():
                records.append(record(candidate, root))
                subdirectories.remove(name)
        for name in filenames:
            records.append(record(directory_path / name, root))
    encoded_records = [
        json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        for item in sorted(records, key=lambda item: item["path"])
    ]
    digest = hashlib.sha256()
    for encoded in encoded_records:
        digest.update(encoded.encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute a content, path, link, and mode fingerprint for a skill."
    )
    parser.add_argument("directory", type=Path)
    arguments = parser.parse_args()
    root = arguments.directory.resolve()
    if not root.is_dir():
        parser.error(f"Not a directory: {arguments.directory}")
    print(fingerprint(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
