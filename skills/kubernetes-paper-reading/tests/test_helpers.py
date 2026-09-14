#!/usr/bin/env python3
"""Regression tests for dependency-free paper-reading helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from extract_k8s_papers import PAPERS  # noqa: E402
from k8s_translation import GoogleTranslator, quote  # noqa: E402


class HelperTests(unittest.TestCase):
    def test_configured_pdf_paths_are_portable_relative_paths(self) -> None:
        for paper in PAPERS.values():
            self.assertFalse(paper["pdf"].is_absolute())

    def test_google_protection_preserves_syntax_and_kind_term(self) -> None:
        translator = GoogleTranslator(Path("/tmp/kubernetes-paper-reading-test-cache.json"))
        protected, values = translator.protect("Use `spec` and [docs](https://example.com) kinds.")

        restored = protected
        for key, value in values.items():
            restored = restored.replace(key, value)

        self.assertIn("`spec`", restored)
        self.assertIn("[docs](https://example.com)", restored)
        self.assertIn("类别", restored)

    def test_quote_preserves_line_structure(self) -> None:
        self.assertEqual(quote("one\n\ntwo"), "> one\n>\n> two")


if __name__ == "__main__":
    unittest.main()
