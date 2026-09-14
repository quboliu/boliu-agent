#!/usr/bin/env python3
"""Regression tests for the dependency-free official-document transforms."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from k8s_bilingual_from_zh import convert  # noqa: E402
from normalize_k8s_markdown import normalize  # noqa: E402
from unquote_shared_code import transform  # noqa: E402


class TransformTests(unittest.TestCase):
    def test_bilingual_converter_pairs_heading_and_translation(self) -> None:
        source = """---
title: Example
---
<!--
# Objects
-->
# 对象

<!--
The object has a desired state.
-->
对象具有期望状态。
"""

        result = convert(source)

        self.assertIn("# Objects｜对象", result)
        self.assertIn("The object has a desired state.", result)
        self.assertIn("> 对象具有期望状态。", result)
        self.assertNotIn("title: Example", result)

    def test_normalizer_expands_mechanical_shortcodes(self) -> None:
        source = """{{< glossary_tooltip term_id="Pod" >}} {{< param "version" >}}
{{< note >}}
Important.
{{< /note >}}
"""

        result = normalize(source, "v1.32")

        self.assertIn("Pod v1.32", result)
        self.assertIn("**Note｜说明**", result)
        self.assertIn("Important.", result)
        self.assertNotIn("{{<", result)

    def test_unquote_moves_only_quoted_code_fence(self) -> None:
        source = "> ```yaml\n> apiVersion: v1\n> kind: Pod\n> ```\n"

        result = transform(source)

        self.assertEqual(result, "```yaml\napiVersion: v1\nkind: Pod\n```\n")


if __name__ == "__main__":
    unittest.main()
