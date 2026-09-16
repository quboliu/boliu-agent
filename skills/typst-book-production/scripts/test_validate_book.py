"""Regression tests for real-project validation. Run with PyMuPDF installed."""
import json
import hashlib
import tempfile
import unittest
from pathlib import Path
import pymupdf
import validate_book as validator


class ProjectValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "markdown/chapters").mkdir(parents=True)
        (self.root / "book/chapters").mkdir(parents=True)
        (self.root / "markdown/chapters/01.md").write_text("# Chapter\nText.", encoding="utf-8")
        (self.root / "book/chapters/01.typ").write_text("= Chapter\nText.", encoding="utf-8")
        self.manifest = self.root / "source-map.json"
        self.manifest.write_text(json.dumps({"chapters": [
            {"source": "01.md", "output": "book/chapters/01.typ", "order": 1,
             "source_sha256": hashlib.sha256((self.root / "markdown/chapters/01.md").read_bytes()).hexdigest()}
        ], "images": []}), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def check_manifest(self):
        failures = []
        validator.check_manifest(self.root, self.root / "markdown/chapters", self.manifest, failures)
        return failures

    def test_recursive_sources(self):
        self.assertEqual(self.check_manifest(), [])
        (self.root / "markdown/chapters/02.md").write_text("# Missing")
        self.assertTrue(any("absent from manifest" in x for x in self.check_manifest()))

    def test_missing_output(self):
        (self.root / "book/chapters/01.typ").unlink()
        self.assertTrue(any("generated chapter" in x for x in self.check_manifest()))

    def test_changed_source_hash(self):
        (self.root / "markdown/chapters/01.md").write_text("# Chapter\nChanged facts.")
        self.assertTrue(any("hash mismatch" in x for x in self.check_manifest()))

    def test_missing_or_invalid_source_hash(self):
        data = json.loads(self.manifest.read_text())
        for digest in (None, "bad", 123):
            data["chapters"][0]["source_sha256"] = digest
            self.manifest.write_text(json.dumps(data))
            self.assertTrue(any("source_sha256" in x for x in self.check_manifest()))

    def test_missing_asset(self):
        self.manifest.write_text(json.dumps({"chapters": [
            {"source": "chapters/01.md", "output": "book/chapters/01.typ", "order": 2}
        ], "images": [{"asset": "assets/missing.png", "width": 100, "height": 100}]}))
        result = self.check_manifest()
        self.assertTrue(any("asset does not exist" in x for x in result))

    def test_project_owned_mapping_cardinality_and_order(self):
        data = json.loads(self.manifest.read_text())
        first = data["chapters"][0]
        (self.root / "book/chapters/02.typ").write_text("= Part two")
        data["chapters"] += [dict(first, output="book/chapters/02.typ", order=7),
                             dict(first, order=7)]
        second = self.root / "markdown/chapters/02.md"
        second.write_text("# Supporting source")
        data["chapters"].append(dict(first, source="02.md", order=7,
            source_sha256=hashlib.sha256(second.read_bytes()).hexdigest()))
        self.manifest.write_text(json.dumps(data))
        self.assertEqual(self.check_manifest(), [])

    def pdf(self, watermark=False):
        path = self.root / "book.pdf"
        with pymupdf.open() as doc:
            for i in range(3):
                page = doc.new_page(width=176 / 25.4 * 72, height=250 / 25.4 * 72)
                page.insert_font(fontname="proof", fontbuffer=pymupdf.Font("helv").buffer)
                page.insert_text((60, 90), "NOT FOR RELEASE" if watermark else f"Page {i+1}", fontname="proof")
            doc.save(path)
        return path

    def test_parsed_pdf_and_wrong_trim(self):
        path = self.pdf()
        failures = []
        self.assertEqual(validator.check_pdf(path, failures), 3)
        self.assertEqual(failures, [])
        validator.check_pdf(path, failures, page_size_mm=(210, 297))
        self.assertTrue(any("trim" in x for x in failures))

    def test_fixture_rejected(self):
        failures = []
        validator.check_pdf(self.pdf(watermark=True), failures)
        self.assertTrue(any("fixture" in x for x in failures))

    def test_placeholder(self):
        (self.root / "book/chapters/01.typ").write_text("// BOLIU-UNRESOLVED: missing diagram")
        failures = []
        validator.check_generated_text(self.root, failures)
        self.assertTrue(failures)

    def test_literal_words_and_template_comments_are_not_placeholders(self):
        (self.root / "book/chapters/01.typ").write_text(
            '// artwork placeholder\n#raw("TODO FIXME placeholder ![[diagram.png]]")\nTODO is a code convention.')
        failures = []
        validator.check_generated_text(self.root, failures)
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
