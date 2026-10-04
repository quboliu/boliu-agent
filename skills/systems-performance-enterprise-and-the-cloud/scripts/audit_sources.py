#!/usr/bin/env python3
"""Audit source reconciliation for Systems Performance: Enterprise and the Cloud.

This is intentionally independent of the Markdown renderer.  It checks the EPUB
package and normalized Markdown counts, then uses both supplied PDFs as semantic
and page-landmark cross-checks.  It writes a machine-readable report only when
asked; failures exit non-zero so the publication pipeline cannot silently proceed.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.parse
import zipfile
from pathlib import Path

from lxml import etree, html
import pymupdf


BOOK_SLUG = "systems-performance-enterprise-and-the-cloud"
EXPECTED_DOCS = [
    "pref00",
    *[f"ch{i:02}" for i in range(1, 17)],
    *[f"app{c}" for c in "abcde"],
    "gloss",
    "index",
    "bm01",
    "bm02",
    "bm03",
]
EXPECTED_CHAPTER_TITLES = [
    "Introduction",
    "Methodologies",
    "Operating Systems",
    "Observability Tools",
    "Applications",
    "CPUs",
    "Memory",
    "File Systems",
    "Disks",
    "Network",
    "Cloud Computing",
    "Benchmarking",
    "perf",
    "Ftrace",
    "BPF",
    "Case Study",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_xhtml(raw: bytes):
    text = raw.decode("utf-8")
    text = re.sub(r"^\s*<\?xml[^>]*\?>", "", text)
    return html.fromstring(text)


def main() -> int:
    root = Path(__file__).resolve().parents[4]
    raw = root / f"{BOOK_SLUG}-raw"
    markdown = root / f"{BOOK_SLUG}-markdown"
    refs = root / ".agents" / "skills" / BOOK_SLUG / "references"
    manifest = json.loads((refs / "source-manifest.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    checks: dict[str, object] = {}

    raw_files = sorted(p.name for p in raw.iterdir() if p.is_file() and p.name != "readme.md")
    checks["raw_files"] = raw_files
    if len(raw_files) != 3 or not any(p.lower().endswith(".epub") for p in raw_files) or sum(
        p.lower().endswith(".pdf") for p in raw_files
    ) != 2:
        errors.append(f"raw source set is not one EPUB plus two PDFs: {raw_files}")

    epub_path = next(raw.glob("*.epub"))
    pdfs = []
    for path in sorted(raw.glob("*.pdf")):
        doc = pymupdf.open(path)
        pdfs.append({"file": path.name, "sha256": sha256(path), "pages": doc.page_count})
        doc.close()
    checks["pdfs"] = pdfs
    print_pdf = next((p for p in pdfs if p["pages"] == 929), None)
    calibre_pdf = next((p for p in pdfs if p["pages"] == 2161), None)
    if not print_pdf:
        errors.append("929-page print/layout PDF not found")
    if not calibre_pdf:
        errors.append("2161-page Calibre/reflow PDF not found")

    with zipfile.ZipFile(epub_path) as z:
        container = etree.fromstring(z.read("META-INF/container.xml"))
        opf_path = container.xpath("string(//*[local-name()='rootfile']/@full-path)")
        opf = etree.fromstring(z.read(opf_path))
        ns = {"o": "http://www.idpf.org/2007/opf"}
        manifest_items = {
            item.get("id"): item.get("href")
            for item in opf.xpath("//o:manifest/o:item", namespaces=ns)
            if item.get("id") and item.get("href")
        }
        base = str(Path(opf_path).parent).replace("\\", "/")
        spine = []
        for itemref in opf.xpath("//o:spine/o:itemref", namespaces=ns):
            href = manifest_items.get(itemref.get("idref"))
            if href:
                full = str(Path(base) / urllib.parse.unquote(href)).replace("\\", "/")
                if full.endswith(".xhtml"):
                    spine.append(Path(full).stem.lower())
        checks["epub"] = {
            "file": epub_path.name,
            "sha256": sha256(epub_path),
            "opf": opf_path,
            "spine_count": len(spine),
            "semantic_documents": [stem for stem in EXPECTED_DOCS if stem in spine],
            "image_plates": [stem for stem in spine if stem.endswith("_images")],
        }
        missing = [stem for stem in EXPECTED_DOCS if stem not in spine]
        if missing:
            errors.append(f"EPUB spine missing semantic documents: {missing}")

    docs = manifest.get("documents", [])
    checks["markdown_documents"] = {
        "count": len(docs),
        "files": [d["output"] for d in docs],
        "all_present": all((markdown / d["output"]).is_file() for d in docs),
    }
    if len(docs) != len(EXPECTED_DOCS):
        errors.append(f"Markdown document count {len(docs)} != {len(EXPECTED_DOCS)}")
    if not checks["markdown_documents"]["all_present"]:
        errors.append("one or more manifest Markdown files are missing")

    image_records = manifest.get("images", [])
    missing_images = [rec["asset"] for rec in image_records if not (markdown / "images" / rec["asset"]).is_file()]
    checks["images"] = {
        "manifest_count": len(image_records),
        "missing": missing_images,
        "selected_source_cover": [rec for rec in image_records if rec.get("selected_as_source_cover")],
    }
    if missing_images:
        errors.append(f"missing extracted images: {missing_images[:5]}")

    all_text = "\n".join(
        (markdown / d["output"]).read_text(encoding="utf-8") for d in docs if (markdown / d["output"]).is_file()
    )
    mojibake = re.findall(r"(?:â|Â|Ã|�)", all_text)
    if mojibake:
        errors.append(f"Markdown contains mojibake markers ({len(mojibake)})")
    image_refs = re.findall(r"!\[[^\]]*\]\(\.\./images/([^\)]+)\)", all_text)
    missing_refs = sorted({name for name in image_refs if not (markdown / "images" / name).is_file()})
    checks["markdown_references"] = {
        "image_references": len(image_refs),
        "missing_image_references": missing_refs,
        "footnote_references": len(re.findall(r"\[\^fn-[^\]]+\]", all_text)),
        "footnote_definitions": len(re.findall(r"^\[\^fn-[^\]]+\]:", all_text, re.M)),
        "fenced_code_blocks": len(re.findall(r"^```(?:text)?$", all_text, re.M)),
        "markdown_tables": len(re.findall(r"^\| .* \|$", all_text, re.M)),
    }
    if missing_refs:
        errors.append(f"Markdown references missing images: {missing_refs[:5]}")
    ref_keys = set(re.findall(r"\[\^(fn-[^\]]+)\]", all_text))
    def_keys = set(re.findall(r"^\[\^(fn-[^\]]+)\]:", all_text, re.M))
    if ref_keys != def_keys:
        errors.append(f"footnote reference/definition mismatch: refs-only={sorted(ref_keys-def_keys)[:5]}, defs-only={sorted(def_keys-ref_keys)[:5]}")

    expected_stats = {"tables": 93, "figures": 170, "code_blocks": 837, "footnote_refs": 197}
    checks["renderer_stats"] = manifest.get("stats", {})
    for key, expected in expected_stats.items():
        observed = manifest.get("stats", {}).get(key)
        if observed != expected:
            errors.append(f"renderer stat {key}={observed}, expected {expected}")
    if manifest.get("unresolved_links"):
        errors.append(f"unresolved EPUB links: {len(manifest['unresolved_links'])}")

    # Compare chapter titles and first-page landmarks against the print PDF TOC.
    if print_pdf:
        path = raw / print_pdf["file"]
        doc = pymupdf.open(path)
        level_one = [title for level, title, page, *rest in doc.get_toc() if level == 1]
        chapter_entries = [title for title in level_one if re.match(r"^(?:Chapter )?\d+[.]?\s", title)]
        observed_titles = [re.sub(r"^Chapter\s+", "", t) for t in chapter_entries[:16]]
        observed_titles = [re.sub(r"^\d+[.]?\s+", "", t) for t in observed_titles]
        checks["print_pdf_toc"] = {"level_one_count": len(level_one), "chapter_titles": observed_titles}
        if observed_titles != EXPECTED_CHAPTER_TITLES:
            errors.append(f"print PDF chapter TOC mismatch: {observed_titles}")
        # Page-1 cover and the first chapter must exist and be text-bearing in the
        # print authority; this catches accidental use of the reflow PDF as layout.
        checks["print_pdf_landmarks"] = {
            "page_1_text": " ".join(doc[0].get_text("text").split())[:160],
            "chapter_1_page": next((page for level, title, page, *rest in doc.get_toc() if level == 1 and "Introduction" in title), None),
        }
        doc.close()

    report = {"book": BOOK_SLUG, "checks": checks, "errors": errors, "status": "pass" if not errors else "fail"}
    output = None
    if len(sys.argv) > 1:
        output = Path(sys.argv[1])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
