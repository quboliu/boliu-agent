"""PDF-level audit regressions; use BOLIU_FONT_PATH and the project test environment."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
import pymupdf


class LayoutRegressions(unittest.TestCase):
    def compile(self, body, edition="monolingual-en", success=True):
        root = Path(__file__).resolve().parents[1] / "templates"
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        pdf = Path(temp.name) / "proof.pdf"
        result = subprocess.run(["typst", "compile", "--root", str(root),
                                 "--font-path", os.environ["BOLIU_FONT_PATH"], "-", str(pdf)],
                                input=f'#import "/{edition}.typ": *\n#show: book\n'+body,
                                text=True, capture_output=True)
        if not success:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Cover exceeds one page", result.stderr)
            return
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        doc = pymupdf.open(pdf)
        self.addCleanup(doc.close)
        return doc

    def test_long_cover_single_page_all_editions(self):
        title = ('Designing Data-Intensive Applications: The Big Ideas Behind Reliable, '
                 'Scalable, and Maintainable Systems, Second Edition')
        for edition in ("monolingual-en", "monolingual-zh", "bilingual"):
            with self.subTest(edition=edition):
                doc = self.compile(
                    f'#source-cover("{title}", "Author", "ORIGINAL-SOURCE")\n'
                    f'#boliu-cover("{title}", "Author", "PUBLISHER-SOURCE", "Edition", '
                    'artwork: "/examples/cover-fixture.svg", artwork-credit: "ART-CREDIT")\n'
                    '#chapter("1", "Opening")\nBODY-MARKER\n', edition)
                self.assertEqual(len(doc), 3)
                self.assertIn("伯流出版社", doc[1].get_text())
                self.assertIn("PUBLISHER-SOURCE", doc[1].get_text())
                self.assertIn("ART-CREDIT", doc[1].get_text())
                self.assertIn("BODY-MARKER", doc[2].get_text())
                self.assertNotIn("\u00ad", doc[1].get_text())
                self.assertTrue(doc[1].get_drawings())

    def test_impossible_cover_rejected(self):
        self.compile('#boliu-cover("Title " * 1000, "Author", "Source", "Edition")', success=False)
        self.compile('#source-cover("Title " * 1000, "Author", "Source")', success=False)

    def test_bilingual_short_and_overheight_pairs(self):
        doc = self.compile('#v(200mm)\n#dual([PAIR-EN], [配对中文])\n'
                           '#pagebreak()\n#dual([LONG-START #lorem(1800)], [长段末尾])',
                           edition="bilingual")
        pages = [p.get_text() for p in doc]
        en = next(i for i, t in enumerate(pages) if "PAIR-EN" in t)
        zh = next(i for i, t in enumerate(pages) if "配对中文" in t)
        self.assertEqual((en, zh), (1, 1))
        start = next(i for i, t in enumerate(pages) if "LONG-START" in t)
        end = next(i for i, t in enumerate(pages) if "长段末尾" in t)
        self.assertGreater(end, start)
        for page in doc:
            for word in page.get_text("words"):
                self.assertLessEqual(word[3], page.rect.height - 20/25.4*72 + 1)

    def test_equation_numbers_and_native_references(self):
        doc = self.compile('#display-equation($x=1$, number: "(3.7)") <fixed>\n'
                           '#display-equation($y=2$) <automatic>\n'
                           '#display-equation($z=3$, number: none)\n'
                           'Fixed: @fixed; automatic: @automatic\n')
        text = doc[0].get_text()
        self.assertGreaterEqual(text.count("3.7"), 2)
        self.assertIn("(2)", text)
        self.assertTrue(doc[0].get_links())

    def test_figure_caption_left_edge(self):
        doc = self.compile('#fig("/examples/cover-fixture.svg", width: 60%, caption: [Short caption])')
        words = doc[0].get_text("words")
        caption = next(w for w in words if w[4] == "Short")
        self.assertAlmostEqual(caption[0], (19 + 141 * 0.04) * 72/25.4, delta=0.5)


if __name__ == "__main__":
    unittest.main()
