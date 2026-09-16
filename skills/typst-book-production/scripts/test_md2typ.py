"""Semantic conversion and actual Typst integration tests. Set BOLIU_FONT_PATH."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import pymupdf
from md2typ import Converter


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
        self.converter(front=["a.md"], math="typst").run()
        template = Path(__file__).resolve().parents[1] / "templates"
        for name in ("core.typ", "covers.typ", "matter.typ"):
            shutil.copyfile(template / name, self.root / "book" / name)
        shutil.copyfile(template / "monolingual-en.typ", self.root / "book/template.typ")
        main = self.root / "book/main.typ"
        main.write_text('#import "template.typ": *\n#show: book\n#include "chapters/001.typ"\n#include "chapters/002.typ"\n')
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


if __name__ == "__main__":
    unittest.main()
