#!/usr/bin/env python3
"""Write reproducible audit reports for the five official Kubernetes posts."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
from pathlib import Path


DEFAULT_OUTPUT_ROOT = Path.cwd() / "阅读"
DEFAULT_COMMIT = "890b36a496fb93c68efedc06385293ee35326df7"


POSTS = {
    "官方文档 | Kubernetes Resource Model and Control Loop｜Kubernetes 资源模型与控制循环": [
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/sources/en/objects.md"),
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/sources/zh-cn/objects.md"),
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/sources/en/controllers.md"),
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/sources/zh-cn/controllers.md"),
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/sources/en/finalizers.md"),
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/sources/zh-cn/finalizers.md"),
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/sources/en/garbage-collection.md"),
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/sources/zh-cn/garbage-collection.md"),
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/sources/en/leases.md"),
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/sources/zh-cn/leases.md"),
        Path("02-Kubernetes-Resource-Model-and-Control-Loop/deployment.yaml"),
    ],
    "官方文档 | Kubernetes Cluster Architecture and Control Plane Communication｜Kubernetes 集群架构与控制平面通信": [
        Path("03-Kubernetes-Cluster-Architecture/sources/en/components.md"),
        Path("03-Kubernetes-Cluster-Architecture/sources/zh-cn/components.md"),
        Path("03-Kubernetes-Cluster-Architecture/sources/en/control-plane-node-communication.md"),
        Path("03-Kubernetes-Cluster-Architecture/sources/zh-cn/control-plane-node-communication.md"),
        Path("03-Kubernetes-Cluster-Architecture/assets/components-of-kubernetes.svg"),
    ],
    "官方文档 | Kubernetes API Concepts｜Kubernetes API 核心语义": [
        Path("05-Kubernetes-API-Concepts/sources/en/api-concepts.md"),
        Path("05-Kubernetes-API-Concepts/sources/zh-cn/api-concepts.md"),
    ],
    "官方文档 | Kubernetes Scheduling Framework｜Kubernetes 调度框架": [
        Path("09-Kubernetes-Scheduling-Framework/sources/en/scheduling-framework.md"),
        Path("09-Kubernetes-Scheduling-Framework/sources/zh-cn/scheduling-framework.md"),
        Path("09-Kubernetes-Scheduling-Framework/assets/scheduling-framework-extensions.png"),
    ],
    "官方文档 | Custom Resources and Operator Pattern｜自定义资源与 Operator 模式": [
        Path("10-Custom-Resources-and-Operator/sources/en/custom-resources.md"),
        Path("10-Custom-Resources-and-Operator/sources/zh-cn/custom-resources.md"),
        Path("10-Custom-Resources-and-Operator/sources/en/operator.md"),
        Path("10-Custom-Resources-and-Operator/sources/zh-cn/operator.md"),
        Path("10-Custom-Resources-and-Operator/shirt-resource-definition.yaml"),
    ],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit assembled Kubernetes official-document posts."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory containing assembled posts (default: ./阅读).",
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        required=True,
        help="Pinned Kubernetes archive used to calculate source hashes.",
    )
    parser.add_argument(
        "--commit",
        default=DEFAULT_COMMIT,
        help="Kubernetes website commit recorded in audit reports.",
    )
    args = parser.parse_args()
    output_root = args.output_root.resolve()
    archive_root = args.archive_root.resolve()

    for directory, relative_sources in POSTS.items():
        sources = [archive_root / relative for relative in relative_sources]
        missing_sources = [path for path in sources if not path.is_file()]
        if missing_sources:
            missing = "\n".join(f"- {path}" for path in missing_sources)
            raise SystemExit(f"Missing archived source files:\n{missing}")

        target = output_root / directory
        index = target / "index.md"
        if not index.is_file():
            raise SystemExit(f"Missing assembled post: {index}")
        text = index.read_text(encoding="utf-8")
        diagnostics: list[str] = []
        for label, pattern in {
            "Hugo shortcode": r"\{\{[<%]",
            "visible translation label": r"中文译文[：:]",
            "quoted heading": r"(?m)^>[ \t]*#{1,6}[ \t]",
            "unexpanded Kubernetes link": r"\]\(/(?:zh-cn/)?docs/",
            "replacement character": "�",
        }.items():
            hits = len(re.findall(pattern, text))
            diagnostics.append(f"- {label}: `{hits}`")

        headings = re.findall(r"(?m)^#{2,6}\s+(.+)$", text)
        bilingual_headings = sum("｜" in heading for heading in headings)
        images = re.findall(r"!\[[^]]*\]\(([^)]+)\)", text)
        missing_images = [image for image in images if not (target / image).resolve().is_file()]
        fences = len(re.findall(r"(?m)^```", text))
        pandoc_path = shutil.which("pandoc")
        if pandoc_path:
            pandoc = subprocess.run(
                [pandoc_path, "-f", "gfm+yaml_metadata_block+tex_math_dollars", "-t", "html", str(index), "-o", "/dev/null"],
                capture_output=True,
                text=True,
                check=False,
            )
            # Pandoc emits an irrelevant localization warning for lang zh-CN; a nonzero
            # exit status remains a hard failure.
            status = "PASS" if pandoc.returncode == 0 else f"FAIL ({pandoc.returncode})"
        else:
            status = "SKIP (pandoc not installed)"
        source_rows = "\n".join(
            f"- `{path.relative_to(archive_root)}` — `{sha(path)}`" for path in sources
        )
        report = f"""# {directory} 审计

## 固定来源

- Kubernetes website commit: `{args.commit}`（2024-08-24）
{source_rows}

## 输出与结构

- `index.md` SHA-256：`{sha(index)}`
- 标题数：`{len(headings)}`；同行双语标题：`{bilingual_headings}`；非同行标题：`{len(headings) - bilingual_headings}`
- Markdown 图片引用：`{len(images)}`；断链：`{len(missing_images)}`
- 围栏代码标记数：`{fences}`（应为偶数：`{fences % 2 == 0}`）
- Pandoc GFM + YAML + MathJax 解析：`{status}`

## 禁用模式

{chr(10).join(diagnostics)}

## 人工核验边界

- 英文原文与官方简体中文译文取自同一固定提交；中文页面 HTML 注释中的对应英文块用于逐块对齐。
- 相邻短段按完整语义单元编排，代码、表格和命令等语言无关内容只展示一次。
- 官网构建时注入的 glossary、feature-state、code-sample、figure、table 与 third-party notice 已展开；特性阶段以 Kubernetes v1.31 快照为准。
- 标题采用 `English｜中文` 同行形式；中文标题不重复章节序号；正文不出现“中文译文”前缀。
- 相对站内链接已展开为 `https://kubernetes.io/` 绝对链接；该变换不改变可见锚文本。
"""
        (target / "audit.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
