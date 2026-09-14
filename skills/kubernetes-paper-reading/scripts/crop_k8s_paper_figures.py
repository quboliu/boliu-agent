#!/usr/bin/env python3
"""Crop vector-heavy Borg and Omega figures from the archived PDFs."""

import argparse
from pathlib import Path


DEFAULT_OUTPUT_ROOT = Path.cwd() / "阅读"


PAPERS = {
    "borg": {
        "pdf": Path("06-Borg/Large-scale cluster management at Google with Borg.pdf"),
        "out": Path("论文阅读 | Large-scale Cluster Management at Google with Borg｜Google Borg 的大规模集群管理/assets"),
        "crops": {
            "figure-01.png": (1, 314, 151, 559, 376),
            "figure-02.png": (2, 317, 441, 556, 598),
            "figure-03.png": (6, 54, 54, 293, 131),
            "figure-04.png": (6, 317, 54, 556, 215),
            "figure-05.png": (7, 54, 54, 556, 237),
            "figure-06.png": (7, 317, 286, 556, 423),
            "figure-07.png": (8, 54, 54, 556, 239),
            "figure-08.png": (9, 54, 54, 293, 213),
            "figure-09.png": (9, 54, 282, 293, 425),
            "figure-10.png": (9, 317, 54, 556, 217),
            "figure-11.png": (9, 317, 272, 556, 399),
            "figure-12.png": (10, 54, 54, 556, 202),
            "figure-13.png": (10, 317, 254, 556, 383),
        },
    },
    "omega": {
        "pdf": Path("07-Omega/Omega Flexible, Scalable Schedulers for Large Compute Clusters.pdf"),
        "out": Path("论文阅读 | Omega: Flexible, Scalable Schedulers for Large Compute Clusters｜Omega：面向大规模计算集群的灵活、可扩展调度器/assets"),
        "crops": {
            "figure-01.png": (1, 317, 151, 556, 338),
            "figure-02.png": (2, 317, 54, 556, 155),
            "figure-03.png": (2, 317, 222, 556, 368),
            "figure-04.png": (3, 54, 54, 293, 211),
            "table-01.png": (4, 54, 54, 556, 143),
            "table-02.png": (5, 317, 54, 556, 193),
            "figure-05.png": (6, 54, 54, 556, 224),
            "figure-06.png": (6, 54, 255, 556, 412),
            "figure-07.png": (8, 116, 54, 496, 224),
            "figure-08.png": (9, 54, 54, 293, 433),
            "figure-09.png": (9, 317, 54, 556, 433),
            "figure-10.png": (10, 54, 54, 556, 198),
            "figure-11.png": (10, 54, 232, 293, 358),
            "figure-12.png": (11, 54, 54, 556, 219),
            "figure-13.png": (11, 54, 274, 293, 497),
            "figure-14.png": (12, 54, 54, 293, 217),
            "figure-15.png": (13, 54, 54, 556, 183),
            "figure-16.png": (13, 54, 222, 293, 371),
        },
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crop figures and tables from the archived Borg/Omega PDFs."
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        required=True,
        help="Archive root containing the configured paper PDFs.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory receiving paper assets (default: ./阅读).",
    )
    parser.add_argument(
        "--paper",
        choices=sorted(PAPERS),
        help="Crop only one paper; default crops both.",
    )
    args = parser.parse_args()
    import fitz

    matrix = fitz.Matrix(4, 4)  # 288 dpi; labels stay readable on the blog.
    archive_root = args.archive_root.resolve()
    output_root = args.output_root.resolve()
    selected = {args.paper: PAPERS[args.paper]} if args.paper else PAPERS
    for paper in selected.values():
        pdf = archive_root / paper["pdf"]
        if not pdf.is_file():
            raise SystemExit(f"Missing paper PDF: {pdf}")
        out = output_root / paper["out"]
        out.mkdir(parents=True, exist_ok=True)
        document = fitz.open(pdf)
        for name, (page_number, x0, y0, x1, y1) in paper["crops"].items():
            page = document[page_number - 1]
            pixmap = page.get_pixmap(matrix=matrix, clip=fitz.Rect(x0, y0, x1, y1), alpha=False)
            pixmap.save(out / name)


if __name__ == "__main__":
    main()
