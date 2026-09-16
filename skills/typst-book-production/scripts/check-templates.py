#!/usr/bin/env python3
"""Compile actual entry points and inspect PDF geometry/content; keep proof artifacts."""
import argparse
import pathlib
import subprocess
import pymupdf

p = argparse.ArgumentParser()
p.add_argument("--font-path", required=True)
p.add_argument("--output", required=True)
args = p.parse_args()
root = pathlib.Path(__file__).resolve().parents[1] / "templates"
out = pathlib.Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)
for mode in ("monolingual-zh", "monolingual-en", "bilingual", "stress", "original-cover"):
    pdf = out / (mode + ".pdf")
    fixture = "stress" if mode == "original-cover" else mode
    run = subprocess.run(
        ["typst", "compile", "--root", str(root), "--font-path", args.font_path,
         "--input", "original=" + str(mode == "original-cover").lower(),
         str(root / "examples" / (fixture + ".typ")), str(pdf)],
        capture_output=True, text=True, check=True)
    if run.stderr.strip():
        raise RuntimeError(run.stderr)
    doc = pymupdf.open(pdf)
    for page in doc:
        assert abs(page.rect.width - 176 / 25.4 * 72) < 0.1
        assert abs(page.rect.height - 250 / 25.4 * 72) < 0.1
        for word in page.get_text("words"):
            assert word[0] >= 0 and word[1] >= 0
            assert word[2] <= page.rect.width + 0.1
            assert word[3] <= page.rect.height + 0.1
    if mode != "original-cover":
        assert "SOURCE EDITION" in doc[0].get_text()
    else:
        assert doc[0].get_drawings(), "Original SVG cover missing"
    assert "伯流出版社" in doc[1].get_text()
    assert "NOT FOR RELEASE" in doc[1].get_text()
    assert doc[2].get_text().strip(), "Unwanted blank before first chapter"
    if fixture == "stress":
        joined = "".join(page.get_text() for page in doc)
        assert "3.1" in joined and "2.1" in joined
        assert "4.1" in joined
        assert any(not page.get_text().strip() for page in doc), "Blank verso not exercised"
        assert sum("Key" in page.get_text() for page in doc) >= 2, "Header did not repeat"
        code = [s for b in doc[2].get_text("dict")["blocks"] if "lines" in b
                for line in b["lines"] for s in line["spans"] if "Mono" in s["font"]]
        assert code and all(s["color"] == 0 for s in code), "Unexpected syntax colors"
        assert any(abs(s["size"] - 8) < 0.01 for s in code)
        assert any(abs(s["size"] - 8.6) < 0.01 for s in code)
        tested_sides = set()
        for index, page in enumerate(doc):
            if "CHAPTER" in page.get_text():
                assert (index + 1) % 2 == 1
            # Transition blanks must not contain a rule or furniture.
            if not page.get_text().strip():
                assert not page.get_drawings()
            header_words = [w for w in page.get_text("words") if w[3] < 22 / 25.4 * 72]
            if index >= 2 and header_words:
                physical = index + 1
                odd = physical % 2 == 1
                tested_sides.add(odd)
                folios = [w for w in header_words if w[4] == str(physical)]
                assert len(folios) == 1, "Missing running folio"
                folio = folios[0]
                expected_left = (19 if odd else 16) / 25.4 * 72
                expected_right = page.rect.width - (16 if odd else 19) / 25.4 * 72
                if odd:
                    assert abs(folio[2] - expected_right) < 1, "Recto folio not outside"
                else:
                    assert abs(folio[0] - expected_left) < 1, "Verso folio not outside"
                rules = [d["rect"] for d in page.get_drawings()
                         if d["rect"].y1 < 22 / 25.4 * 72 and d["rect"].width > 300]
                assert rules, "Running rule missing"
                assert any(abs(r.x0 - expected_left) < 0.2 and
                           abs(r.x1 - expected_right) < 0.2 for r in rules), "Margins not mirrored"
        assert tested_sides == {False, True}, "Need both recto and verso body pages"
    for index in range(len(doc)):
        doc[index].get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(
            str(out / f"{mode}-page-{index+1}.png"))
    print(f"{mode}: {len(doc)} pages, B5, cover sequence and geometry passed"
          + (", duplex mirror/folios passed" if fixture == "stress" else ""))
