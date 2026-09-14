#!/usr/bin/env python3
"""Assemble the five Kubernetes official-document posts from audited parts."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_OUTPUT_ROOT = Path.cwd() / "阅读"
DEFAULT_DRAFT_ROOT = Path.cwd() / "kubernetes-topic-drafts"
DEFAULT_COMMIT = "890b36a496fb93c68efedc06385293ee35326df7"


def frontmatter(date: str, title: str, tags: list[str], description: str) -> str:
    tag_lines = "\n".join(f'  - "{tag}"' for tag in tags)
    return f'''---
lang: "zh-CN"
pubDatetime: {date}T12:00:00+08:00
timezone: "Asia/Shanghai"
title: "{title}"
featured: false
area: "kubernetes"
draft: false
tags:
{tag_lines}
description: "{description}"
---
'''


def shift_headings(text: str, amount: int = 1) -> str:
    output: list[str] = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            output.append(line)
            continue
        if not in_fence and line.startswith("#"):
            count = len(line) - len(line.lstrip("#"))
            if count and count + amount <= 6 and line[count : count + 1] == " ":
                line = "#" * (count + amount) + line[count:]
        output.append(line)
    return "\n".join(output).strip()


def source_note(pages: list[tuple[str, str]], commit: str) -> str:
    links = "\n".join(f"> - [{title}]({url})" for title, url in pages)
    commit_url = f"https://github.com/kubernetes/website/commit/{commit}"
    return f'''> **Source and translation basis｜来源与翻译依据**
>
{links}
>
> The English source and the official Simplified Chinese source were frozen at Kubernetes website commit [`{commit[:12]}`]({commit_url}) (2024-08-24). Kubernetes documentation content is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); code samples are licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0).
>
> 英文原文与简体中文官方译文均固定于 Kubernetes 网站提交 [`{commit[:12]}`]({commit_url})（2024-08-24）。本文逐个语义单元核对两种语言，并把官网构建时动态注入的术语定义、特性状态、示例代码与插图还原为可独立阅读的 Markdown。Kubernetes 文档内容采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可，代码示例采用 [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0/) 许可。'''


def write_post(output_root: Path, directory: str, fm: str, attribution: str, body: str) -> Path:
    target = output_root / directory
    target.mkdir(parents=True, exist_ok=True)
    path = target / "index.md"
    path.write_text(f"{fm}\n{attribution}\n\n---\n\n{body.strip()}\n", encoding="utf-8")
    return target


def part(draft_root: Path, relative: str) -> str:
    return (draft_root / relative).read_text(encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assemble Kubernetes official-document posts from audited parts."
    )
    parser.add_argument(
        "--draft-root",
        type=Path,
        default=DEFAULT_DRAFT_ROOT,
        help="Root containing generated part files (default: ./kubernetes-topic-drafts).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory receiving assembled posts (default: ./阅读).",
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        required=True,
        help="Pinned Kubernetes archive containing copied assets.",
    )
    parser.add_argument(
        "--commit",
        default=DEFAULT_COMMIT,
        help="Kubernetes website commit recorded in attribution notes.",
    )
    args = parser.parse_args()
    draft_root = args.draft_root.resolve()
    output_root = args.output_root.resolve()
    archive_root = args.archive_root.resolve()

    resource_pages = [
        ("Objects In Kubernetes", "https://kubernetes.io/docs/concepts/overview/working-with-objects/"),
        ("Controllers", "https://kubernetes.io/docs/concepts/architecture/controller/"),
        ("Finalizers", "https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/"),
        ("Garbage Collection", "https://kubernetes.io/docs/concepts/architecture/garbage-collection/"),
        ("Leases", "https://kubernetes.io/docs/concepts/architecture/leases/"),
    ]
    sections = [
        ("Objects In Kubernetes｜Kubernetes 对象", "resource-control/parts/objects.md"),
        ("Controllers｜控制器", "resource-control/parts/controllers.md"),
        ("Finalizers｜Finalizers", "resource-control/parts/finalizers.md"),
        ("Garbage Collection｜垃圾收集", "resource-control/parts/garbage-collection.md"),
        ("Leases｜租约", "resource-control/parts/leases.md"),
    ]
    body = "\n\n---\n\n".join(
        f"## {title}\n\n{shift_headings(part(draft_root, path))}" for title, path in sections
    )
    write_post(
        output_root,
        "官方文档 | Kubernetes Resource Model and Control Loop｜Kubernetes 资源模型与控制循环",
        frontmatter(
            "2024-09-15",
            "官方文档 | Kubernetes Resource Model and Control Loop｜Kubernetes 资源模型与控制循环",
            ["官方文档", "Kubernetes", "控制器", "声明式 API", "控制循环", "分布式系统"],
            "Kubernetes 官方文档中英对照精读：从对象的 spec/status 出发，贯通控制循环、Finalizer、属主引用、垃圾收集与 Lease。",
        ),
        source_note(resource_pages, args.commit),
        body,
    )

    architecture_pages = [
        ("Kubernetes Components", "https://kubernetes.io/docs/concepts/architecture/"),
        ("Communication between Nodes and the Control Plane", "https://kubernetes.io/docs/concepts/architecture/control-plane-node-communication/"),
    ]
    body = "\n\n---\n\n".join(
        [
            f"## Kubernetes Components｜Kubernetes 组件\n\n{shift_headings(part(draft_root, 'cluster-architecture/parts/components.md'))}",
            f"## Communication between Nodes and the Control Plane｜节点与控制面之间的通信\n\n{shift_headings(part(draft_root, 'cluster-architecture/parts/control-plane-node-communication.md'))}",
        ]
    )
    target = write_post(
        output_root,
        "官方文档 | Kubernetes Cluster Architecture and Control Plane Communication｜Kubernetes 集群架构与控制平面通信",
        frontmatter(
            "2024-10-06",
            "官方文档 | Kubernetes Cluster Architecture and Control Plane Communication｜Kubernetes 集群架构与控制平面通信",
            ["官方文档", "Kubernetes", "控制平面", "集群架构", "etcd", "分布式系统"],
            "Kubernetes 官方文档中英对照精读：把控制平面、节点组件与 API Server 双向通信路径映射到一套完整的集群架构。",
        ),
        source_note(architecture_pages, args.commit),
        body,
    )
    assets = target / "assets"
    assets.mkdir(exist_ok=True)
    shutil.copy2(
        archive_root / "03-Kubernetes-Cluster-Architecture/assets/components-of-kubernetes.svg",
        assets / "components-of-kubernetes.svg",
    )

    api_body = part(draft_root, "api-concepts/parts/api-concepts.md")
    write_post(
        output_root,
        "官方文档 | Kubernetes API Concepts｜Kubernetes API 核心语义",
        frontmatter(
            "2024-12-08",
            "官方文档 | Kubernetes API Concepts｜Kubernetes API 核心语义",
            ["官方文档", "Kubernetes", "Kubernetes API", "Watch", "resourceVersion", "分布式系统"],
            "Kubernetes API Concepts 官方文档中英对照精读：覆盖资源 URI、list/watch、分页、内容协商、更新、试运行与 resourceVersion 语义。",
        ),
        source_note([("Kubernetes API Concepts", "https://kubernetes.io/docs/reference/using-api/api-concepts/")], args.commit),
        api_body,
    )

    scheduling_body = part(draft_root, "scheduling-framework/parts/scheduling-framework.md")
    target = write_post(
        output_root,
        "官方文档 | Kubernetes Scheduling Framework｜Kubernetes 调度框架",
        frontmatter(
            "2025-03-23",
            "官方文档 | Kubernetes Scheduling Framework｜Kubernetes 调度框架",
            ["官方文档", "Kubernetes", "调度器", "Scheduling Framework", "插件", "分布式系统"],
            "Kubernetes 调度框架官方文档中英对照精读：梳理调度周期、绑定周期、全部扩展点、插件 API 与配置机制。",
        ),
        source_note([("Scheduling Framework", "https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/")], args.commit),
        scheduling_body,
    )
    assets = target / "assets"
    assets.mkdir(exist_ok=True)
    shutil.copy2(
        archive_root / "09-Kubernetes-Scheduling-Framework/assets/scheduling-framework-extensions.png",
        assets / "scheduling-framework-extensions.png",
    )

    custom_body = "\n\n---\n\n".join(
        [
            f"## Custom Resources｜定制资源\n\n{shift_headings(part(draft_root, 'custom-resources-operator/parts/custom-resources.md'))}",
            f"## Operator Pattern｜Operator 模式\n\n{shift_headings(part(draft_root, 'custom-resources-operator/parts/operator.md'))}",
        ]
    )
    write_post(
        output_root,
        "官方文档 | Custom Resources and Operator Pattern｜自定义资源与 Operator 模式",
        frontmatter(
            "2025-04-13",
            "官方文档 | Custom Resources and Operator Pattern｜自定义资源与 Operator 模式",
            ["官方文档", "Kubernetes", "CRD", "Operator", "控制器", "声明式 API"],
            "Kubernetes 官方文档中英对照精读：比较 CRD 与聚合 API，解释自定义控制器如何把运维知识编码为 Operator。",
        ),
        source_note(
            [
                ("Custom Resources", "https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/"),
                ("Operator Pattern", "https://kubernetes.io/docs/concepts/extend-kubernetes/operator/"),
            ],
            args.commit,
        ),
        custom_body,
    )


if __name__ == "__main__":
    main()
