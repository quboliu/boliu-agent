"""Semantic conversion and actual Typst integration tests. Set BOLIU_FONT_PATH."""
import os
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import pymupdf
from md2typ import Converter
import validate_book as validator


class Conversion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        fence = chr(96) * 3
        (self.source / "a.md").write_text("# First\n\nSee [next](b.md#second), *emphasis* and **strong**.\n\n3. third\n4. fourth\n\n> Quotation\n>\n> —— Author\n\n" + fence + "python\nprint('literal # []')\n" + fence + "\n\n| Key | Value |\n| --- | --- |\n| one | two |\n", encoding="utf-8")
        (self.source / "b.md").write_text("# Second\n\nBack [here](a.md).\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def converter(self, **kw):
        return Converter(self.source, self.root, ["a.md", "b.md"], **kw)

    def test_semantics(self):
        result = self.converter().run()
        body = (self.root / "book/chapters/001.typ").read_text()
        self.assertIn("#emph[", body)
        self.assertIn("#strong[", body)
        self.assertIn("#enum(start: 3,", body)
        self.assertIn("#link(label(", body)
        self.assertIn('attribution: [#text("Author")]', body)
        self.assertEqual(len(result["chapters"]), 2)

    def test_unresolved_link(self):
        (self.source / "b.md").write_text("# Second\n\n[bad](a.md#absent)")
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            self.converter().run()
        self.assertFalse((self.root / "book").exists())

    def test_math_requires_declared_syntax(self):
        (self.source / "b.md").write_text("# Second\n\n$x^2$\n\n$$\ny = x^2\n$$")
        with self.assertRaisesRegex(ValueError, "math"):
            self.converter().run()
        self.converter(math="typst").run()
        self.assertIn("$x^2$", (self.root / "book/chapters/002.typ").read_text())

    def test_html_fails(self):
        (self.source / "b.md").write_text("# Second\n\n<div>Unadapted</div>")
        with self.assertRaisesRegex(ValueError, "HTML"):
            self.converter().run()

    def test_numbered_heading_and_alignment(self):
        (self.source / "a.md").write_text("# 第 1 章 起点\n\n## 1.1 小节\n\n| 数值 |\n| ---: |\n| 10 |\n")
        self.converter().run()
        text = (self.root / "book/chapters/001.typ").read_text()
        self.assertIn('chapter("1", [#text("起点")])', text)
        self.assertIn('heading(level: 2)[#text("小节")]', text)
        self.assertIn("table.cell(align: right)", text)

    def test_unsupported_footnotes_rejected_before_writes(self):
        for content in ('Text[^1].\n\n[^1]: Note.', '[^unused]: Unused note.',
                        'Undefined[^missing].', 'Inline^[note].', '~~deleted~~'):
            with self.subTest(content=content):
                (self.source / "b.md").write_text("# Second\n\n" + content)
                with self.assertRaisesRegex(ValueError, "Unsupported"):
                    self.converter().run()
                self.assertFalse((self.root / "book").exists())

    def test_footnote_syntax_in_code_is_literal(self):
        (self.source / "b.md").write_text("# Second\n\n`[^1]`\n\n```md\n[^1]: literal\n```\n")
        self.converter().run()
        self.assertIn('[^1]: literal', (self.root / "book/chapters/002.typ").read_text())

    def test_number_drift_rejected_before_writes(self):
        for content in ('## 1.7 Jump', '## 1.1 One\n\n## 1.1 Duplicate',
                        '### 1.1.1 Skipped', '## 1.1 One\n\n### 1.1.3 Jump',
                        '## 1.1 *Styled*', '#### 1.1.1.1 Unnumbered depth'):
            with self.subTest(content=content):
                (self.source / "a.md").write_text("# First\n\n" + content)
                with self.assertRaises(ValueError):
                    self.converter().run()
                self.assertFalse((self.root / "book").exists())

    def test_nested_and_implicit_numbers(self):
        (self.source / "a.md").write_text(
            "# 第 1 章 First\n\n## Implicit\n\n### 1.1.1 Nested\n\n## 1.2 Next\n\n### 1.2.1 Reset")
        self.converter().run()
        self.assertIn('heading(level: 3)[#text("Reset")]',
                      (self.root / "book/chapters/001.typ").read_text())

    def test_asset_and_explicit_caption(self):
        (self.source / "diagram.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="40"><rect width="80" height="40" fill="white"/></svg>')
        (self.source / "b.md").write_text("# Second\n\n![alternative](diagram.svg)\n\n<center>图 2-1 正式图注</center>\n")
        result = self.converter().run()
        self.assertEqual(len(result["images"]), 1)
        self.assertEqual(result["images"][0]["width"], 80)
        self.assertIn("正式图注", (self.root / "book/chapters/002.typ").read_text())

    def test_compile_output(self):
        fontpath = os.environ.get("BOLIU_FONT_PATH")
        self.assertTrue(fontpath, "Set BOLIU_FONT_PATH for integration test")
        (self.source / "b.md").write_text("# Second\n\n## Details\n\n$x^2$\n\n$$\ny = x^2\n$$\n")
        manifest = self.converter(front=["a.md"], math="typst").run()
        manifest_path = self.source / "source-map.json"
        manifest_path.write_text(json.dumps(manifest))
        template = Path(__file__).resolve().parents[1] / "templates"
        for name in ("core.typ", "covers.typ", "matter.typ"):
            shutil.copyfile(template / name, self.root / "book" / name)
        shutil.copyfile(template / "monolingual-en.typ", self.root / "book/template.typ")
        shutil.copyfile(template / "examples/cover-fixture.svg", self.root / "art.svg")
        main = self.root / "book/main.typ"
        # Synthetic art tests mechanics only, not release rights or historical relevance.
        main.write_text('#import "template.typ": *\n#show: book\n'
                        '#source-cover("Test", "Author", "Source v1")\n'
                        '#boliu-cover("Test", "Author", "Source v1", "English", artwork: "/art.svg")\n'
                        '#include "chapters/001.typ"\n#include "chapters/002.typ"\n')
        result = subprocess.run(["typst", "compile", "--root", str(self.root),
                                 "--font-path", fontpath, str(main), str(self.root / "test.pdf")],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        with pymupdf.open(self.root / "test.pdf") as doc:
            self.assertTrue(any(page.get_links() for page in doc))
            text = "".join(page.get_text() for page in doc)
            self.assertIn("Quotation", text)
            self.assertIn("literal", text)
        failures = []
        validator.check_manifest(self.root, self.source, manifest_path, failures)
        validator.check_generated_text(self.root, failures)
        validator.check_pdf(self.root / "test.pdf", failures)
        self.assertEqual(failures, [])

    def test_bilingual_short_and_overheight_pairs(self):
        fontpath = os.environ.get("BOLIU_FONT_PATH")
        self.assertTrue(fontpath)
        template = Path(__file__).resolve().parents[1] / "templates"
        for name in ("core.typ", "covers.typ", "matter.typ", "bilingual.typ"):
            shutil.copyfile(template / name, self.root / name)
        main = self.root / "main.typ"
        main.write_text('#import "bilingual.typ": *\n#show: book\n'
                        '#v(200mm)\n#dual([PAIR-EN], [配对中文])\n'
                        '#pagebreak()\n#dual([LONG-START #lorem(1800)], [长段末尾])\n')
        pdf = self.root / "dual.pdf"
        result = subprocess.run(["typst", "compile", "--root", str(self.root),
                                 "--font-path", fontpath, str(main), str(pdf)],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        with pymupdf.open(pdf) as doc:
            pages = [p.get_text() for p in doc]
            en = next(i for i, text in enumerate(pages) if "PAIR-EN" in text)
            zh = next(i for i, text in enumerate(pages) if "配对中文" in text)
            self.assertEqual(en, zh)
            self.assertEqual(en, 1, "Short pair should move to second page")
            start = next(i for i, text in enumerate(pages) if "LONG-START" in text)
            end = next(i for i, text in enumerate(pages) if "长段末尾" in text)
            self.assertGreater(end, start)
            for page in doc:
                for word in page.get_text("words"):
                    self.assertLessEqual(word[3], page.rect.height - 20/25.4*72 + 1)


if __name__ == "__main__":
    unittest.main()
