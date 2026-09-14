#!/usr/bin/env python3
"""Extract reading-order paragraph blocks from the archived Borg/Omega PDFs.

PyMuPDF supplies paragraph boundaries (first-line indentation); Poppler's raw
text supplies the canonical two-column reading order. Figure/table interiors
are excluded because they are represented by high-resolution crops.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


LIGATURES = str.maketrans({"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"})
REAL_HYPHEN_PREFIXES = {
    "admission",
    "application",
    "best",
    "cell",
    "cluster",
    "coarse",
    "compute",
    "cross",
    "data",
    "end",
    "fine",
    "first",
    "fixed",
    "high",
    "job",
    "large",
    "latency",
    "lock",
    "long",
    "low",
    "machine",
    "memory",
    "multi",
    "non",
    "out",
    "pre",
    "priority",
    "production",
    "real",
    "resource",
    "run",
    "second",
    "shared",
    "short",
    "single",
    "site",
    "state",
    "task",
    "time",
    "two",
    "user",
    "web",
}
REAL_HYPHEN_PAIRS = {
    ("application", "level"),
    ("auto", "scaling"),
    ("data", "access"),
    ("data", "center"),
    ("difficult", "to"),
    ("gb", "seconds"),
    ("in", "memory"),
    ("lower", "priority"),
    ("month", "long"),
    ("multi", "path"),
    ("multi", "tenancy"),
    ("multi", "tenant"),
    ("of", "memory"),
    ("open", "source"),
    ("post", "facto"),
    ("publicly", "available"),
    ("resource", "consumption"),
    ("slo", "driven"),
    ("time", "consuming"),
    ("two", "way"),
    ("workload", "execution"),
}


@dataclass
class Unit:
    page: int
    order: int
    kind: str
    text: str
    continued: bool = False
    source_bbox: tuple[float, float, float, float] | None = None
    asset: str | None = None


PAPERS = {
    "borg": {
        "pdf": Path("06-Borg/Large-scale cluster management at Google with Borg.pdf"),
        "regions": {
            1: [(314, 151, 559, 376, "figure", "assets/figure-01.png")],
            2: [(317, 441, 556, 598, "figure", "assets/figure-02.png")],
            6: [(54, 54, 293, 131, "figure", "assets/figure-03.png"), (317, 54, 556, 215, "figure", "assets/figure-04.png")],
            7: [(54, 54, 556, 237, "figure", "assets/figure-05.png"), (317, 286, 556, 423, "figure", "assets/figure-06.png")],
            8: [(54, 54, 556, 239, "figure", "assets/figure-07.png")],
            9: [(54, 54, 293, 213, "figure", "assets/figure-08.png"), (54, 282, 293, 425, "figure", "assets/figure-09.png"), (317, 54, 556, 217, "figure", "assets/figure-10.png"), (317, 272, 556, 399, "figure", "assets/figure-11.png")],
            10: [(54, 54, 556, 202, "figure", "assets/figure-12.png"), (317, 254, 556, 383, "figure", "assets/figure-13.png")],
        },
    },
    "omega": {
        "pdf": Path("07-Omega/Omega Flexible, Scalable Schedulers for Large Compute Clusters.pdf"),
        "regions": {
            1: [(317, 151, 556, 338, "figure", "assets/figure-01.png")],
            2: [(317, 54, 556, 155, "figure", "assets/figure-02.png"), (317, 222, 556, 368, "figure", "assets/figure-03.png")],
            3: [(54, 54, 293, 211, "figure", "assets/figure-04.png")],
            4: [(54, 54, 556, 143, "table", "assets/table-01.png")],
            5: [(317, 54, 556, 193, "table", "assets/table-02.png")],
            6: [(54, 54, 556, 224, "figure", "assets/figure-05.png"), (54, 255, 556, 412, "figure", "assets/figure-06.png")],
            8: [(116, 54, 496, 224, "figure", "assets/figure-07.png")],
            9: [(54, 54, 293, 433, "figure", "assets/figure-08.png"), (317, 54, 556, 433, "figure", "assets/figure-09.png")],
            10: [(54, 54, 556, 198, "figure", "assets/figure-10.png"), (54, 232, 293, 358, "figure", "assets/figure-11.png")],
            11: [(54, 54, 556, 219, "figure", "assets/figure-12.png"), (54, 274, 293, 497, "figure", "assets/figure-13.png")],
            12: [(54, 54, 293, 217, "figure", "assets/figure-14.png")],
            13: [(54, 54, 556, 183, "figure", "assets/figure-15.png"), (54, 222, 293, 371, "figure", "assets/figure-16.png")],
        },
    },
}


def clean_chars(text: str) -> str:
    return text.translate(LIGATURES).replace("−", "−").replace("–", "–")


def join_lines(lines: list[str]) -> str:
    result = ""
    for raw in lines:
        line = clean_chars(raw).strip()
        if not line:
            continue
        if not result:
            result = line
            continue
        if result.endswith("-") and re.match(r"^[a-z]", line):
            match = re.search(r"([A-Za-z]+)-$", result)
            prefix = match.group(1).lower() if match else ""
            next_word_match = re.match(r"([A-Za-z]+)", line)
            pair = (prefix, next_word_match.group(1).lower() if next_word_match else "")
            if prefix in REAL_HYPHEN_PREFIXES or pair in REAL_HYPHEN_PAIRS or "-" in result[max(0, result.rfind(" ")) : -1]:
                result += line
            else:
                result = result[:-1] + line
        else:
            result += " " + line
    return re.sub(r"\s+", " ", result).strip()


def tokenize(text: str) -> list[str]:
    text = clean_chars(text).lower()
    text = re.sub(r"([a-z])-\s+([a-z])", r"\1\2", text)
    return re.findall(r"[a-z0-9µ§]+", text)


def raw_pages(pdf: Path) -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-raw", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return result.split("\f")


def raw_order(text: str, raw: str, used: dict[str, int]) -> int:
    candidate = tokenize(text)
    haystack = " ".join(tokenize(raw))
    if not candidate:
        return 10**9
    for length in (12, 9, 7, 5, 3, 2, 1):
        if len(candidate) < length:
            continue
        needle = " ".join(candidate[:length])
        start = used.get(needle, 0)
        pos = haystack.find(needle, start)
        if pos >= 0:
            used[needle] = pos + len(needle)
            return pos
    return 10**9


def inside_region(bbox, regions) -> bool:
    rect = fitz.Rect(bbox)
    for x0, y0, x1, y1, _kind, _asset in regions:
        overlap = rect & fitz.Rect(x0, y0, x1, y1)
        if not overlap.is_empty and overlap.get_area() >= rect.get_area() * 0.35:
            return True
    return False


def heading_kind(text: str, bold: bool) -> tuple[str, int] | None:
    if text in {"Abstract", "Acknowledgments", "Acknowledgements", "References"}:
        return text, 2
    match = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+)$", text)
    if not match or len(text) > 120 or not bold:
        return None
    number, title = match.groups()
    level = min(2 + number.count("."), 5)
    return f"{number} {title}", level


def split_block(block: dict) -> list[tuple[str, bool, tuple[float, float, float, float], bool]]:
    raw_lines = block.get("lines", [])
    # Some section headings encode the number and title as separate lines at
    # the exact same vertical position. Merge those fragments first.
    lines: list[dict] = []
    for line in sorted(raw_lines, key=lambda item: (round(item["bbox"][1], 1), item["bbox"][0])):
        if lines and abs(lines[-1]["bbox"][1] - line["bbox"][1]) < 1.0:
            lines[-1]["text"] += " " + "".join(span["text"] for span in line.get("spans", []))
            old = lines[-1]["bbox"]
            new = line["bbox"]
            lines[-1]["bbox"] = (min(old[0], new[0]), min(old[1], new[1]), max(old[2], new[2]), max(old[3], new[3]))
            lines[-1]["bold"] = lines[-1]["bold"] or any("Medi" in span["font"] or "Bold" in span["font"] for span in line.get("spans", []))
        else:
            lines.append({
                "bbox": tuple(line["bbox"]),
                "text": "".join(span["text"] for span in line.get("spans", [])),
                "bold": any("Medi" in span["font"] or "Bold" in span["font"] for span in line.get("spans", [])),
            })
    if not lines:
        return []
    block_bbox = tuple(block["bbox"])
    base = 54.0 if block_bbox[0] < 305 else 317.0
    groups: list[tuple[list[str], bool, bool]] = []
    current: list[str] = []
    continued = False
    bold = False
    for line in lines:
        text = line["text"]
        indented = line["bbox"][0] >= base + 7.0
        if current and indented:
            groups.append((current, continued, bold))
            current = []
        if not current:
            continued = not indented
            bold = False
        bold = bold or line["bold"]
        current.append(text)
    if current:
        groups.append((current, continued, bold))
    return [(join_lines(group), cont, block_bbox, is_bold) for group, cont, is_bold in groups if join_lines(group)]


def extract(paper_name: str, archive_root: Path) -> list[Unit]:
    import fitz

    config = PAPERS[paper_name]
    pdf = archive_root / config["pdf"]
    if not pdf.is_file():
        raise FileNotFoundError(f"Missing paper PDF: {pdf}")
    document = fitz.open(pdf)
    page_raw = raw_pages(pdf)
    all_units: list[Unit] = []
    next_figure = 1
    next_table = 1

    for page_index, page in enumerate(document):
        page_number = page_index + 1
        regions = config["regions"].get(page_number, [])
        candidates: list[Unit] = []
        used: dict[str, int] = {}
        for block in page.get_text("dict", sort=False)["blocks"]:
            if block.get("type") != 0 or inside_region(block["bbox"], regions):
                continue
            for text, continued, bbox, bold in split_block(block):
                if re.fullmatch(r"\d+", text) and bbox[1] > 735:
                    continue
                caption = re.match(r"^(Figure|Table)\s+(\d+)\s*:", text)
                if caption:
                    kind = caption.group(1).lower()
                    number = int(caption.group(2))
                    asset = f"assets/{kind}-{number:02d}.png"
                    candidates.append(Unit(page_number, 0, kind, text, False, bbox, asset))
                    continue
                kind = "footnote" if bbox[1] > 590 and re.match(r"^[†‡*0-9]", text) and not bold else "paragraph"
                heading = heading_kind(text, bold)
                if heading:
                    heading_text, level = heading
                    candidates.append(Unit(page_number, 0, f"heading{level}", heading_text, False, bbox))
                    continue
                candidates.append(Unit(page_number, 0, kind, text, continued, bbox))

        for unit in candidates:
            unit.order = raw_order(unit.text, page_raw[page_index] if page_index < len(page_raw) else "", used)
        candidates.sort(key=lambda u: (u.order, u.source_bbox[1] if u.source_bbox else 0))

        # Assign a deterministic fallback order after all raw-matched blocks.
        fallback = max((u.order for u in candidates if u.order < 10**9), default=0) + 1000
        for unit in candidates:
            if unit.order >= 10**9:
                unit.order = fallback
                fallback += 1

        # Join true paragraph continuations across columns/pages while leaving
        # captions and footnotes as independent source units.
        for unit in candidates:
            if unit.kind == "paragraph" and unit.continued:
                previous = next(
                    (
                        u
                        for u in reversed(all_units)
                        if u.kind == "paragraph"
                        and not u.text.startswith("Permission to make")
                        and not re.search(r"[.!?\]\)”]$", u.text)
                    ),
                    None,
                )
                continuation_signal = bool(
                    re.match(r"^[a-z(]", unit.text)
                    or re.search(r"[-,;:(]$", previous.text if previous else "")
                )
                if previous and continuation_signal and not re.match(r"^(Abstract|Permission)", unit.text):
                    previous.text = join_lines([previous.text, unit.text])
                    continue
            all_units.append(unit)

    return all_units


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract reading-order units from an archived Borg/Omega PDF."
    )
    parser.add_argument("paper", choices=sorted(PAPERS))
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--archive-root",
        type=Path,
        required=True,
        help="Archive root containing the configured paper PDF.",
    )
    args = parser.parse_args()
    units = extract(args.paper, args.archive_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps([asdict(unit) for unit in units], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
