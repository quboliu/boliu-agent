"""Regression tests for the canonical book-workspace validator."""

import tempfile
import unittest
from pathlib import Path

import validate_workspace as validator


class WorkspaceValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "example-book"
        self.root.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def create_workspace(self, language: str) -> None:
        slug = self.root.name
        raw = self.root / f"{slug}-raw"
        markdown = self.root / f"{slug}-markdown"
        raw.mkdir()
        (raw / "Source.PDF").write_bytes(b"source bytes")
        (markdown / "chapters").mkdir(parents=True)
        (markdown / "images").mkdir()
        (markdown / "chapters/01.md").write_text("# Chapter\n", encoding="utf-8")
        skill = self.root / ".agents" / "skills" / slug
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {slug}\ndescription: Local rules.\n---\n\n# Local rules\n",
            encoding="utf-8",
        )
        suffixes = ("zh",) if language == "zh" else ("en", "dual", "zh")
        for suffix in suffixes:
            edition = self.root / f"{slug}-typst-{suffix}"
            for relative in (
                "assets/covers/boliu",
                "assets/covers/source",
                "assets/figures",
                "assets/fonts",
                "book/chapters",
                "editorial/content-audit",
                "output/audit",
                "output/build",
                "output/preview",
            ):
                (edition / relative).mkdir(parents=True, exist_ok=True)
            for relative in (
                "book/covers.typ",
                "book/core.typ",
                "book/main.typ",
                "book/matter.typ",
                "book/template.typ",
                "book.toml",
                "source-map.json",
            ):
                (edition / relative).write_text("", encoding="utf-8")

    def test_chinese_matrix_passes(self):
        self.create_workspace("zh")
        self.assertEqual(validator.validate(self.root, "zh"), [])

    def test_english_requires_all_three_editions(self):
        self.create_workspace("en")
        missing = self.root / "example-book-typst-dual"
        for path in sorted(missing.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            else:
                path.rmdir()
        missing.rmdir()
        self.assertTrue(
            any("typst-dual" in item for item in validator.validate(self.root, "en"))
        )

    def test_rejects_competing_source_tree(self):
        self.create_workspace("zh")
        (self.root / "example-book-typst-zh/source").mkdir()
        self.assertTrue(
            any("competing role" in item for item in validator.validate(self.root, "zh"))
        )

    def test_rejects_unrecognized_edition_root_entry(self):
        self.create_workspace("zh")
        (self.root / "example-book-typst-zh/tools").mkdir()
        self.assertTrue(
            any(
                "unexpected entries in edition root" in item
                for item in validator.validate(self.root, "zh")
            )
        )

    def test_raw_original_filename_may_retain_uppercase(self):
        self.create_workspace("zh")
        self.assertFalse(
            any("uppercase" in item for item in validator.validate(self.root, "zh"))
        )

    def test_generated_names_must_be_lowercase(self):
        self.create_workspace("zh")
        (self.root / "example-book-markdown/images/Figure.PNG").write_bytes(b"image")
        self.assertTrue(
            any("uppercase" in item for item in validator.validate(self.root, "zh"))
        )

    def test_local_skill_name_must_match_slug(self):
        self.create_workspace("zh")
        skill = self.root / ".agents/skills/example-book/SKILL.md"
        skill.write_text("---\nname: wrong-name\n---\n", encoding="utf-8")
        self.assertTrue(
            any("does not match" in item for item in validator.validate(self.root, "zh"))
        )

    def test_rejects_nested_git_repository(self):
        self.create_workspace("zh")
        nested_git = self.root / "example-book-raw/upstream/.git"
        nested_git.mkdir(parents=True)
        self.assertTrue(
            any(
                "nested Git" in item
                for item in validator.validate(self.root, "zh")
            )
        )

    def test_rejects_submodule_configuration(self):
        self.create_workspace("zh")
        (self.root / ".gitmodules").write_text("[submodule]\n", encoding="utf-8")
        self.assertTrue(
            any(
                "submodule" in item
                for item in validator.validate(self.root, "zh")
            )
        )


if __name__ == "__main__":
    unittest.main()
