#!/usr/bin/env python3
"""Move language-neutral code samples out of Chinese translation blockquotes."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


OPEN_RE = re.compile(r"^> ?(?P<indent>\s*)```(?P<rest>.*)$")


def transform(text: str) -> str:
    output: list[str] = []
    in_code = False
    indent = ""
    for line in text.splitlines():
        if not in_code:
            match = OPEN_RE.match(line)
            if match:
                in_code = True
                indent = match.group("indent")
                output.append(f"```{match.group('rest')}")
            else:
                output.append(line)
            continue

        if re.match(r"^> ?\s*```\s*$", line):
            output.append("```")
            in_code = False
            indent = ""
            continue

        if line.startswith(">"):
            payload = line[1:]
            if payload.startswith(" "):
                payload = payload[1:]
            if indent and payload.startswith(indent):
                payload = payload[len(indent) :]
            output.append(payload)
        else:
            output.append(line)

    if in_code:
        raise RuntimeError("unterminated quoted code fence")
    return "\n".join(output).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.paths:
        path.write_text(transform(path.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()
