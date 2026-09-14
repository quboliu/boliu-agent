#!/usr/bin/env python3
"""Expand substantive Kubernetes Hugo shortcodes in the pinned v1.31 drafts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DEFAULT_DRAFT_ROOT = Path.cwd() / "kubernetes-topic-drafts"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, found {count}")
    return text.replace(old, new)


def expand_common(text: str) -> str:
    text = text.replace(
        '> {{< feature-state feature_gate_name="APIServerIdentity" >}}',
        '**Feature state (Kubernetes v1.31): Beta, enabled by default｜特性状态（Kubernetes v1.31）：Beta，默认启用**',
    )
    text = text.replace(
        '> {{< feature-state feature_gate_name="ImageMaximumGCAge" >}}',
        '**Feature state (Kubernetes v1.31): Beta, enabled by default｜特性状态（Kubernetes v1.31）：Beta，默认启用**',
    )
    text = text.replace(
        '> {{< feature-state feature_gate_name="WatchList" >}}',
        '**Feature state (Kubernetes v1.31): Alpha, disabled by default｜特性状态（Kubernetes v1.31）：Alpha，默认关闭**',
    )
    text = text.replace(
        '> {{< feature-state feature_gate_name="APIResponseCompression" >}}',
        '**Feature state (Kubernetes v1.31): Beta, enabled by default｜特性状态（Kubernetes v1.31）：Beta，默认启用**',
    )
    text = text.replace(
        '> {{< feature-state feature_gate_name="APIListChunking" >}}',
        '**Feature state (Kubernetes v1.31): Stable, enabled by default｜特性状态（Kubernetes v1.31）：Stable，默认启用**',
    )
    text = text.replace(
        '> {{< feature-state feature_gate_name="ServerSideFieldValidation" >}}',
        '**Feature state (Kubernetes v1.31): Stable, enabled by default｜特性状态（Kubernetes v1.31）：Stable，默认启用**',
    )
    text = text.replace(
        '> {{< feature-state feature_gate_name="DryRun" >}}',
        '**Feature state: Stable since Kubernetes v1.19｜特性状态：自 Kubernetes v1.19 起为 Stable**',
    )
    text = text.replace(
        '> {{< feature-state feature_gate_name="CustomResourceFieldSelectors" >}}',
        '**Feature state (Kubernetes v1.31): Beta, enabled by default｜特性状态（Kubernetes v1.31）：Beta，默认启用**',
    )
    text = text.replace(
        '> {{< feature-state for_k8s_version="v1.19" state="stable" >}}',
        '**Feature state: Kubernetes v1.19 [stable]｜特性状态：Kubernetes v1.19 [stable]**',
    )
    text = text.replace(
        '> {{< feature-state for_k8s_version="v1.28" state="beta" >}}',
        '**Feature state: Kubernetes v1.28 [beta]｜特性状态：Kubernetes v1.28 [beta]**',
    )
    text = text.replace(
        '> {{< feature-state for_k8s_version="v1.18" state="beta" >}}',
        '**Feature state: Kubernetes v1.18 [beta]｜特性状态：Kubernetes v1.18 [beta]**',
    )
    text = text.replace(
        '> {{% thirdparty-content %}}',
        "**Third-party content notice｜第三方内容说明**\n\n"
        "This section links to third party projects that provide functionality required by Kubernetes. "
        "The Kubernetes project authors aren't responsible for these projects, which are listed alphabetically. "
        "To add a project to this list, read the [content guide](https://kubernetes.io/docs/contribute/style/content-guide/#third-party-content) before submitting a change.\n\n"
        "> 本部分链接到提供 Kubernetes 所需功能的第三方项目。Kubernetes 项目作者不负责这些项目。"
        "此页面遵循 [CNCF 网站指南](https://github.com/cncf/foundation/blob/master/website-guidelines.md)，按字母顺序列出项目。"
        "若要把项目加入此列表，请先阅读[内容指南](https://kubernetes.io/zh-cn/docs/contribute/style/content-guide/#third-party-content)，再提交更改。",
    )
    # Definition-list caution shortcodes are inline rather than standalone.
    text = text.replace(
        ': {{< caution >}} Watches initialized this way may return arbitrarily stale\n'
        '  data. Please review this semantic before using it, and favor the other semantics\n'
        '  where possible.\n\n',
        ': **Caution:** Watches initialized this way may return arbitrarily stale data. Please review this semantic before using it, and favor the other semantics where possible.\n\n',
    )
    text = text.replace(
        '> : {{< caution >}}\n'
        '>   以这种方式初始化的监视可能会返回任意陈旧的数据。\n'
        '>   请在使用之前查看此语义，并尽可能支持其他语义。\n\n',
        '> : **注意：** 以这种方式初始化的监视可能会返回任意陈旧的数据。请在使用之前审慎确认这一语义，并尽可能采用其他语义。\n\n',
    )
    # Absolute links keep the standalone Markdown meaningful outside kubernetes.io.
    text = text.replace('](/zh-cn/docs/', '](https://kubernetes.io/zh-cn/docs/')
    text = text.replace('](/docs/', '](https://kubernetes.io/docs/')
    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Expand substantive Kubernetes Hugo shortcodes in bilingual drafts."
    )
    parser.add_argument(
        "--draft-root",
        type=Path,
        default=DEFAULT_DRAFT_ROOT,
        help="Root containing generated part files (default: ./kubernetes-topic-drafts).",
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        required=True,
        help="Pinned Kubernetes archive containing code samples and source assets.",
    )
    args = parser.parse_args()
    draft_root = args.draft_root.resolve()
    archive_root = args.archive_root.resolve()

    objects = draft_root / "resource-control/parts/objects.md"
    text = objects.read_text(encoding="utf-8")
    deployment = (archive_root / "02-Kubernetes-Resource-Model-and-Control-Loop/deployment.yaml").read_text(encoding="utf-8").rstrip()
    text = replace_once(
        text,
        '> {{% code_sample file="application/deployment.yaml" %}}',
        f"```yaml\n{deployment}\n```",
        "deployment sample",
    )
    objects.write_text(expand_common(text), encoding="utf-8")

    controllers = draft_root / "resource-control/parts/controllers.md"
    text = controllers.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '> {{< glossary_definition term_id="controller" length="short">}}',
        "In Kubernetes, controllers are control loops that watch the state of your cluster, then make or request changes where needed. Each controller tries to move the current cluster state closer to the desired state.\n\n"
        "> 在 Kubernetes 中，控制器是持续监视集群状态的控制回路，并在需要时实施或请求变更。每个控制器都力图推动集群的当前状态接近期望状态。",
        "controller definition",
    )
    controllers.write_text(expand_common(text), encoding="utf-8")

    gc = draft_root / "resource-control/parts/garbage-collection.md"
    text = gc.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '{{<glossary_definition term_id="garbage-collection" length="short">}} This\nallows the clean up of resources like the following:',
        "Garbage collection is a collective term for the various mechanisms Kubernetes uses to clean up cluster resources. This allows the clean up of resources like the following:",
        "garbage collection English definition",
    )
    text = replace_once(
        text,
        '> {{<glossary_definition term_id="garbage-collection" length="short">}}\n> 垃圾收集允许系统清理如下资源：',
        "> 垃圾收集是 Kubernetes 用于清理集群资源的各种机制的统称。系统由此可以清理以下资源：",
        "garbage collection Chinese definition",
    )
    gc.write_text(expand_common(text), encoding="utf-8")

    scheduling = draft_root / "scheduling-framework/parts/scheduling-framework.md"
    text = scheduling.read_text(encoding="utf-8")
    figure_en = '{{< figure src="/images/docs/scheduling-framework-extensions.png" title="scheduling framework extension points" class="diagram-large">}}'
    figure_zh = '> {{< figure src="/images/docs/scheduling-framework-extensions.png" title="调度框架扩展点" class="diagram-large">}}'
    text = replace_once(
        text,
        f"{figure_en}\n\n{figure_zh}",
        "![Scheduling framework extension points｜调度框架扩展点](./assets/scheduling-framework-extensions.png)\n\n"
        "**Figure: Scheduling framework extension points｜图：调度框架扩展点**\n\n"
        "> **图解：** 一次 Pod 调度被拆成调度周期与绑定周期。扩展点按执行顺序分布在队列、预过滤、过滤、打分、保留、许可、预绑定、绑定和后处理等阶段；插件只需实现对应接口即可介入流程，而调度器框架负责调用顺序、状态传递与失败处理。",
        "scheduling figure",
    )
    scheduling.write_text(expand_common(text), encoding="utf-8")

    custom = draft_root / "custom-resources-operator/parts/custom-resources.md"
    text = custom.read_text(encoding="utf-8")
    shirt = (archive_root / "10-Custom-Resources-and-Operator/shirt-resource-definition.yaml").read_text(encoding="utf-8").rstrip()
    text = replace_once(
        text,
        '> {{% code_sample file="customresourcedefinition/shirt-resource-definition.yaml" %}}',
        f"```yaml\n{shirt}\n```",
        "CRD sample",
    )
    custom.write_text(expand_common(text), encoding="utf-8")

    for relative in [
        "resource-control/parts/finalizers.md",
        "resource-control/parts/leases.md",
        "cluster-architecture/parts/components.md",
        "cluster-architecture/parts/control-plane-node-communication.md",
        "api-concepts/parts/api-concepts.md",
        "custom-resources-operator/parts/operator.md",
    ]:
        path = draft_root / relative
        path.write_text(expand_common(path.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()
