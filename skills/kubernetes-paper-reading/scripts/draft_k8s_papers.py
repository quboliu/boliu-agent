#!/usr/bin/env python3
"""Assemble first bilingual drafts for the Borg and Omega papers."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path

from k8s_translation import GoogleTranslator, Translator, quote
from extract_k8s_papers import PAPERS, extract, join_lines


DEFAULT_OUTPUT_ROOT = Path.cwd() / "阅读"


META = {
    "borg": {
        "output": Path("论文阅读 | Large-scale Cluster Management at Google with Borg｜Google Borg 的大规模集群管理/index.md"),
        "date": "2025-01-12",
        "title_en": "Large-scale Cluster Management at Google with Borg",
        "title_zh": "Google Borg 的大规模集群管理",
        "description": "Google Borg 经典论文中英对照精读：覆盖 Cell、作业与任务、Borgmaster/Borglet、调度、可用性、资源回收、隔离及十年生产经验。",
        "source": "https://research.google/pubs/large-scale-cluster-management-at-google-with-borg/",
        "sha": "2fdacd3b69f8af91477412fc91d1d858a43e764929a4edb646bd517ededdad94",
        "venue": "EuroSys 2015",
        "authors_en": "Abhishek Verma†, Luis Pedrosa‡, Madhukar Korupolu, David Oppenheimer, Eric Tune, John Wilkes — Google Inc.",
        "authors_zh": "Abhishek Verma†、Luis Pedrosa‡、Madhukar Korupolu、David Oppenheimer、Eric Tune、John Wilkes——Google Inc.（谷歌公司）",
        "context": "本文阅读时间安排在 2025 年 1 月，对应存算分离云原生数据库项目的 Kubernetes、Longhorn 与资源管理实践。阅读重点是追溯 Kubernetes 调度、容错、资源超卖和高利用率机制在 Borg 生产系统中的来源。",
        "reference_pages": (15, 17),
        "reference_count": 84,
    },
    "omega": {
        "output": Path("论文阅读 | Omega: Flexible, Scalable Schedulers for Large Compute Clusters｜Omega：面向大规模计算集群的灵活、可扩展调度器/index.md"),
        "date": "2025-02-16",
        "title_en": "Omega: Flexible, Scalable Schedulers for Large Compute Clusters",
        "title_zh": "Omega：面向大规模计算集群的灵活、可扩展调度器",
        "description": "Omega 经典论文中英对照精读：比较单体、两级与共享状态调度，分析乐观并发、调度器干扰、冲突处理和 MapReduce 专用调度。",
        "source": "https://research.google/pubs/omega-flexible-scalable-schedulers-for-large-compute-clusters/",
        "sha": "41457f149c2cad8ea6e858707fb0bb38370595bd4abd918c2f17a0cb3a28823f",
        "venue": "EuroSys 2013",
        "authors_en": "Malte Schwarzkopf†*, Andy Konwinski‡*, Michael Abd-El-Malek§, John Wilkes§ — †University of Cambridge Computer Laboratory; ‡University of California, Berkeley; §Google, Inc.",
        "authors_zh": "Malte Schwarzkopf†*、Andy Konwinski‡*、Michael Abd-El-Malek§、John Wilkes§——†剑桥大学计算机实验室；‡加州大学伯克利分校；§Google Inc.（谷歌公司）",
        "context": "本文阅读时间安排在 2025 年 2 月，对应存算分离云原生数据库项目后期的 Kubernetes 调度与资源编排实践。它解释共享集群状态、乐观并发控制与多调度器并行如何从 Borg 的单体架构演进而来。",
        "reference_pages": (14, 14),
        "reference_count": 29,
    },
}


HEADINGS = {
    "Abstract": "摘要",
    "1 Introduction": "引言",
    "2 The user perspective": "用户视角",
    "2.1 The workload": "工作负载",
    "2.2 Clusters and cells": "集群与 Cell",
    "2.3 Jobs and tasks": "作业与任务",
    "2.4 Allocs": "Alloc",
    "2.5 Priority, quota, and admission control": "优先级、配额与准入控制",
    "2.6 Naming and monitoring": "命名与监控",
    "3 Borg architecture": "Borg 架构",
    "3.1 Borgmaster": "Borgmaster",
    "3.2 Scheduling": "调度",
    "3.3 Borglet": "Borglet",
    "3.4 Scalability": "可扩展性",
    "4 Availability": "可用性",
    "5 Utilization": "利用率",
    "5.1 Evaluation methodology": "评估方法",
    "5.2 Cell sharing": "Cell 共享",
    "5.3 Large cells": "大型 Cell",
    "5.4 Fine-grained resource requests": "细粒度资源请求",
    "5.5 Resource reclamation": "资源回收",
    "6 Isolation": "隔离",
    "6.1 Security isolation": "安全隔离",
    "6.2 Performance isolation": "性能隔离",
    "7 Related work": "相关工作",
    "8 Lessons and future work": "经验与未来工作",
    "8.1 Lessons learned: the bad": "经验教训：不足之处",
    "8.2 Lessons learned: the good": "经验教训：成功之处",
    "8.3 Conclusion": "结论",
    "Acknowledgments": "致谢",
    "Acknowledgements": "致谢",
    "References": "参考文献",
    "1.1 Contributions": "主要贡献",
    "2 Requirements": "需求",
    "2.1 Workload heterogeneity": "工作负载异构性",
    "3 Taxonomy": "架构分类",
    "3.1 Monolithic schedulers": "单体调度器",
    "3.2 Statically partitioned schedulers": "静态分区调度器",
    "3.3 Two-level scheduling": "两级调度",
    "3.4 Shared-state scheduling": "共享状态调度",
    "4 Design comparisons": "设计比较",
    "4.1 Monolithic schedulers": "单体调度器",
    "4.2 Two-level scheduling: Mesos": "两级调度：Mesos",
    "4.3 Shared-state scheduling: Omega": "共享状态调度：Omega",
    "4.4 Summary": "小结",
    "5 Trace-driven simulation": "跟踪驱动模拟",
    "5.1 Scheduling performance": "调度性能",
    "5.2 Dealing with conflicts": "冲突处理",
    "6 Flexibility: a MapReduce scheduler": "灵活性：MapReduce 调度器",
    "6.1 Implementation": "实现",
    "6.2 Evaluation": "评估",
    "7 Additional related work": "补充相关工作",
    "8 Conclusions and future work": "结论与未来工作",
}


CAPTION_ZH = {
    "borg": {
        1: "图 1：Borg 的高层架构。图中只画出了数千个工作节点中的极少一部分。",
        2: "图 2：作业与任务共用的状态图。用户可以触发提交、终止和更新状态转换。",
        3: "图 3：生产与非生产工作负载的任务驱逐率及其原因。数据采自 2013 年 8 月 1 日。",
        4: "图 4：压实的效果。该图给出 15 个 Cell 压实后规模占原始规模比例的累积分布函数（CDF）。",
        5: "图 5：把 prod 与 non-prod 工作放入不同 Cell 会需要更多机器。两幅图都以单一 Cell 运行该工作负载所需的最少机器数为基准，给出拆分后增加的机器比例；本图及后续 CDF 图中，每个 Cell 的值取多次试验结果的第 90 百分位，误差线表示完整取值范围。",
        6: "图 6：按用户隔离会需要更多机器。图中针对 5 个 Cell，给出当规模超过所示阈值的用户分别获得私有 Cell 时所需的 Cell 总数与额外机器数。",
        7: "图 7：把 Cell 划分为更小的 Cell 会需要更多机器。图中给出把指定 Cell 拆成不同数量的小 Cell 后，相对于单 Cell 情况增加的机器比例。",
        8: "图 8：没有一种桶大小能够很好地适配大多数任务。图中给出样本 Cell 内 CPU 与内存请求量的 CDF；没有哪个值格外突出，只有少数整数 CPU 核数略受欢迎。",
        9: "图 9：对资源需求量“分桶”会需要更多机器。图中给出把 15 个 Cell 的 CPU 与内存请求向上取整到最近的 2 的幂后产生的额外开销 CDF；上下界包围实际值。",
        10: "图 10：资源回收非常有效。图中给出在 15 个代表性 Cell 中禁用资源回收后所需额外机器数的 CDF。",
        11: "图 11：资源估算能够成功识别未使用资源。虚线表示 15 个 Cell 内任务的 CPU、内存实际用量与请求上限之比，实线表示预留量与上限之比；直线段是资源估算过程造成的形态。",
        12: "图 12：更激进的资源估算可以回收更多资源，而对内存不足事件影响很小。时间线展示一个生产 Cell 的用量、预留量、上限和累计 OOM；竖线分隔采用不同估算设置的周。",
        13: "图 13：负载变化下的调度延迟。每组柱中左侧为延迟敏感任务、右侧为批处理任务；即使机器很忙，线程等待 CPU 超过 5 ms 的情况也只占很小比例。",
    },
    "omega": {
        1: "图 1：本文考察的三类调度架构示意图：单体、两级和共享状态。",
        2: "图 2：集群 A、B、C 的批处理与服务工作负载，包括归一化作业数、任务数以及 CPU 核秒和 RAM GB 秒总请求量；斜线部分为服务作业。",
        3: "图 3：集群 A、B、C 的作业运行时间与到达间隔 CDF。实线表示批处理作业，虚线表示服务作业；曲线未到 1.0 表示存在运行超过 30 天范围的作业。",
        4: "图 4：集群 A、B、C 中每个作业所含任务数的 CDF；右图放大左图第 95 百分位以上、任务数不少于 100 的尾部。",
        5: "图 5：不同架构下，调度器的作业等待时间随相应的每作业调度时间变化；横向 SLO 线为 30 秒。",
        6: "图 6：不同架构下，调度器忙碌度随相应的每作业调度时间变化；数值为 7 天实验的每日忙碌度中位数，误差线为一个中位绝对偏差。",
        7: "图 7：两级调度（Mesos）的性能随服务作业调度时间变化。",
        8: "图 8：共享状态调度（Omega）在集群 B 中随批处理作业到达率变化的表现；竖直虚线标出调度器饱和点，右侧工作负载只能被部分调度。",
        9: "图 9：共享状态调度（Omega）在集群 B 中随批处理作业到达率变化的表现；每条曲线对应不同数量的批处理调度器。",
        10: "图 10：轻量级模拟器中，服务作业调度时间与单任务调度时间对不同调度方案忙碌度的影响；三维图中的红色区域表示仍有工作负载未被调度。",
        11: "图 11：使用高保真模拟器和集群 C 的 29 天跟踪，观察服务作业调度时间与单任务调度时间对服务调度器忙碌度的影响。",
        12: "图 12：使用集群 B 的 7 天跟踪，观察服务作业调度时间变化对共享状态调度性能的影响。",
        13: "图 13：使用集群 C 的 24 小时跟踪，把批处理工作负载拆给 3 个调度器后，批处理作业调度时间变化带来的性能影响。",
        14: "图 14：在集群 C 的 29 天跟踪上，成组调度与粗粒度冲突检测随服务作业调度时间变化而产生的影响；图中为每日均值。",
        15: "图 15：在集群 A、C、D 上采用不同策略时，每个作业潜在加速比的 CDF。",
        16: "图 16：集群 C 不使用专用 Omega MapReduce 调度器时（上）与采用最大并行度模式时（下）的归一化集群利用率时间序列。",
        101: "表 1：并行化集群调度方法的比较。",
        102: "表 2：两种模拟器的比较；“实际数据”表示使用生产集群详细工作负载执行跟踪中的信息。",
    },
}


EXPLANATIONS = {
    "borg": {
        1: "客户端把声明式作业配置交给 Borgmaster；Borgmaster 的持久状态由 Paxos 复制，调度器作出放置决策，各机器上的 Borglet 执行并上报任务状态。",
        2: "作业和任务都经过 Pending、Running、Dead 三个核心状态。调度、驱逐、失败、终止与滚动更新都被表达为可恢复的状态转换。",
        3: "生产任务很少被驱逐；非生产任务的大部分驱逐来自机器维护或关机，其次才是资源不足与抢占，这体现了优先级隔离策略。",
        4: "压实会重新打包任务、估计一个 Cell 实际需要多少机器。多数 Cell 可压缩到原规模的约 80%–100%，说明放置碎片确实存在但差异较大。",
        5: "prod 与 non-prod 混部能够共享互补的资源峰谷；把二者硬拆开会显著增加总机器数，这是 Borg 追求混部的直接容量依据。",
        6: "为大用户单建 Cell 会同时增加 Cell 数和容量冗余。隔离边界越多，跨用户统计复用机会越少。",
        7: "大 Cell 提供更大的装箱搜索空间与统计复用池；拆得越细，额外机器开销总体越高。",
        8: "资源请求分布连续而分散，不存在少数天然规格可以覆盖大部分任务，因此 Borg 不采用固定大小的资源槽。",
        9: "把请求向上取整到固定桶会把内部碎片转化成真实容量成本；桶越粗，CPU 与内存的联合浪费越明显。",
        10: "若只按请求上限而不回收未用资源，代表性 Cell 需要明显增加机器。资源回收是 Borg 高利用率的核心来源。",
        11: "任务通常远未用满请求上限；Borg 用保守的预留量承诺可用资源，再把上限与实际用量之间的空间用于超卖。",
        12: "逐步调低安全余量后，预留量明显下降而 OOM 斜率变化有限，说明基于历史用量的估算能在风险可控时释放容量。",
        13: "CPU 竞争会随机器利用率上升而增加，但延迟敏感任务受到更强保护；大部分等待仍低于 1 ms 或 5 ms 阈值。",
    },
    "omega": {
        1: "三种架构的根本差异在并发控制：单体调度器不并行，两级架构通过资源 offer 悲观分割状态，Omega 则让多个调度器共享完整状态并用事务乐观解决冲突。",
        2: "批处理作业数量占多数，服务作业却消耗大部分长期资源。调度器必须同时服务“数量多而短”和“数量少而长”的两种负载。",
        3: "批处理与服务作业在运行时间和到达模式上存在数量级差异，这解释了为何单一调度策略难以兼顾低延迟与高利用率。",
        4: "多数作业任务数很少，但尾部存在超大作业。尾部规模决定了成组放置、调度吞吐和冲突概率。",
        5: "单体多路径与共享状态模型能通过并行降低等待时间；当每次调度计算变慢时，架构差异会迅速放大。",
        6: "忙碌度接近 1 表示调度器饱和。共享状态并行提高处理能力，但也必须付出事务冲突与重试成本。",
        7: "Mesos 的资源 offer 会让服务框架长时间持有资源；计算越慢，批处理调度器越容易得不到合适资源并出现未调度作业。",
        8: "批处理到达率超过饱和点后，等待时间与未调度比例陡增；Omega 的扩展极限可由调度计算和冲突共同决定。",
        9: "增加批处理调度器能摊薄单个调度器的工作，但也提高并发事务冲突率；扩容收益并非无限。",
        10: "三维曲面同时揭示每作业固定成本与每任务成本。不同架构在这两个维度的瓶颈位置不同，红区表示已无法消化全部输入。",
        11: "高保真模拟确认，服务调度器的可扩展性同时受作业级计算和任务级计算影响，并非只取决于作业到达率。",
        12: "当服务调度算法变慢，作业等待时间、调度器忙碌度和冲突都会上升；假设无冲突的对照线量化了乐观并发税。",
        13: "把批处理负载分给多个调度器改善吞吐，但并行度提升也增加冲突；结果展示了共享状态架构的横向扩展边界。",
        14: "成组调度或把整个作业视作一个冲突单元都会放大事务范围，导致冲突率和忙碌度上升；增量事务应是默认选择。",
        15: "利用全局空闲资源动态提高作业并行度，能显著缩短部分作业的完成时间；尾部收益尤其明显。",
        16: "专用 MapReduce 调度器让作业在空闲资源出现时扩张、资源紧张时收缩，从而提高 CPU/RAM 利用率而不改变共享状态核心。",
        101: "单体、静态分区、Mesos 与 Omega 在资源选择、干扰控制、分配粒度和集群级策略上各有取舍；Omega 以乐观事务换取最完整的状态可见性。",
        102: "轻量模拟器以采样和齐次机器换取速度；高保真模拟器使用真实机器、请求、初始状态、约束和 Google 调度算法，运行更慢但更接近生产。",
    },
}


def frontmatter(name: str) -> str:
    meta = META[name]
    tags = ["论文阅读", "Kubernetes", "分布式系统"]
    tags += ["Borg", "集群管理", "资源调度"] if name == "borg" else ["Omega", "集群调度", "乐观并发控制"]
    tag_lines = "\n".join(f'  - "{tag}"' for tag in tags)
    return f'''---
lang: "zh-CN"
pubDatetime: {meta["date"]}T12:00:00+08:00
timezone: "Asia/Shanghai"
title: "论文阅读 | {meta["title_en"]}｜{meta["title_zh"]}"
featured: false
area: "distributed-systems"
draft: false
tags:
{tag_lines}
description: "{meta["description"]}"
---

> **Source and translation basis｜来源与翻译依据**
>
> [{meta["title_en"]}]({meta["source"]}), published at {meta["venue"]}. Archived PDF SHA-256: `{meta["sha"]}`.
>
> 原文来自 Google Research，并以本地归档 PDF 为唯一正文、图表与参考文献依据。本文按论文阅读顺序重建双栏内容，完整保留版权、脚注、图表题注和参考文献；中文翻译按语义段落紧随英文原文。
>
> **Reading context｜阅读背景：** {meta["context"]}

---

{meta["authors_en"]}

> {meta["authors_zh"]}
'''


def verify_source_pdf(name: str, archive_root: Path) -> Path:
    pdf = archive_root / PAPERS[name]["pdf"]
    if not pdf.is_file():
        raise SystemExit(f"Missing paper PDF: {pdf}")
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    expected = META[name]["sha"]
    if digest != expected:
        raise SystemExit(
            f"PDF SHA-256 mismatch for {name}: expected {expected}, got {digest}"
        )
    return pdf


def clean_units(name: str, archive_root: Path):
    units = extract(name, archive_root)
    start = next(i for i, unit in enumerate(units) if unit.kind == "heading2" and unit.text == "Abstract")
    units = units[start:]
    cleaned = []
    for unit in units:
        if unit.kind == "heading2" and unit.text == "References":
            break
        if name == "omega" and unit.text.startswith("D.4.7 [Operating Categories and Subject Descriptors Systems]"):
            unit.text = "Categories and Subject Descriptors D.4.7 [Operating Systems]: Organization and Design—Distributed systems; K.6.4 [Management of computing and information systems]: System Management—Centralization/decentralization"
        cleaned.append(unit)
    # Merge extraction fragments that clearly end mid-sentence. This primarily
    # repairs numbered contribution lists and column/page continuations.
    merged = []
    for unit in cleaned:
        if (
            merged
            and unit.kind == "paragraph"
            and merged[-1].kind == "paragraph"
            and not re.search(r"[.!?;:”“”'\"]$", merged[-1].text)
            and not merged[-1].text.startswith("Permission to make")
        ):
            merged[-1].text = join_lines([merged[-1].text, unit.text])
        else:
            merged.append(unit)
    repaired = []
    for unit in merged:
        if name == "omega" and "Categories and Subject Descriptors" in unit.text and " Keywords " in unit.text:
            left, right = unit.text.split(" Keywords ", 1)
            first = type(unit)(**{**unit.__dict__, "text": left})
            second = type(unit)(**{**unit.__dict__, "text": "Keywords " + right})
            repaired.extend([first, second])
            continue
        if name == "omega" and unit.text.startswith("(approx.) t (batch):") and "tecture can easily achieve" in unit.text:
            continue
        if name == "omega" and unit.text.startswith("Load-balancing the batch scheduler."):
            unit.text = re.sub(
                r"Fortunately, the Omega architask 0\.8 1\.0$",
                "Fortunately, the Omega architecture can easily achieve this by load-balancing the scheduling of batch jobs across multiple batch schedulers.",
                unit.text,
            )
        repaired.append(unit)

    footnote_markers = {
        "borg": {
            "site.1": "site.<sup>1</sup>",
            "ports,2": "ports,<sup>2</sup>",
            "them.3": "them.<sup>3</sup>",
            "tasks,4": "tasks,<sup>4</sup>",
            "weeks 2 and 3.5": "weeks 2 and 3.<sup>5</sup>",
        },
        "omega": {
            "jobs1": "jobs<sup>1</sup>",
            "frameworks.2": "frameworks.<sup>2</sup>",
            "offers.3": "offers.<sup>3</sup>",
            "state.4": "state.<sup>4</sup>",
            "software.5": "software.<sup>5</sup>",
            "conservative6": "conservative<sup>6</sup>",
            "running.7": "running.<sup>7</sup>",
            "activities8": "activities<sup>8</sup>",
        },
    }
    for unit in repaired:
        # These are visible line-wrap artifacts confirmed against the rendered
        # PDF pages, not authorial hyphenation.
        unit.text = unit.text.replace("pre-vent", "prevent")
        unit.text = unit.text.replace("pre-cludes", "precludes")
        unit.text = unit.text.replace("multi-ple", "multiple")
        unit.text = unit.text.replace("allor-nothing", "all-or-nothing")
        unit.text = unit.text.replace("out-weighed", "outweighed")
        unit.text = unit.text.replace("fairnessand", "fairness and")
        for old, new in footnote_markers[name].items():
            unit.text = unit.text.replace(old, new)

    # Remove labels that sit just outside the PDF figure bounding boxes and
    # reconstruct the few blocks interrupted by floating figures/footnotes.
    normalized = []
    borg_figure_3 = next((u for u in repaired if name == "borg" and u.text.startswith("Figure 3:")), None)
    borg_figure_4 = next((u for u in repaired if name == "borg" and u.text.startswith("Figure 4:")), None)
    for unit in repaired:
        if name == "borg" and unit.text == "100":
            continue
        if name == "borg" and (unit is borg_figure_3 or unit is borg_figure_4):
            continue
        if name == "borg" and unit.text.startswith("Several things make the Borg scheduler more scalable:"):
            normalized.append(type(unit)(**{**unit.__dict__, "text": "Several things make the Borg scheduler more scalable:"}))
            normalized.append(type(unit)(**{**unit.__dict__, "text": "**Score caching:** Evaluating feasibility and scoring a machine is expensive, so Borg caches the scores until the properties of the machine or task change – e.g., a task on the machine terminates, an attribute is altered, or a task’s requirements change. Ignoring small changes in resource quantities reduces cache invalidations."}))
            continue
        if name == "borg" and unit.text.startswith("Equivalence classes:"):
            unit.text = "**Equivalence classes:**" + unit.text.removeprefix("Equivalence classes:")
        if name == "borg" and unit.text.startswith("Relaxed randomization:"):
            unit.text = "**Relaxed randomization:**" + unit.text.removeprefix("Relaxed randomization:")
        if name == "borg" and unit.text == "4 Availability":
            normalized.append(unit)
            normalized.append(type(unit)(page=6, order=unit.order, kind="paragraph", text="Failures are the norm in large scale systems [10, 11, 22]. Figure 3 provides a breakdown of task eviction causes in 15 sample cells. Applications that run on Borg are expected to handle such events, using techniques such as replication, storing persistent state in a distributed file system, and (if appropriate) taking occasional checkpoints. Even so, we try to mitigate the impact of these events. For example, Borg:"))
            normalized.append(borg_figure_3)
            normalized.append(type(unit)(page=6, order=unit.order, kind="paragraph", text="- automatically reschedules evicted tasks, on a new machine if necessary;\n- reduces correlated failures by spreading tasks of a job across failure domains such as machines, racks, and power domains;\n- limits the allowed rate of task disruptions and the number of tasks from a job that can be simultaneously down during maintenance activities such as OS or machine upgrades;\n- uses declarative desired-state representations and idempotent mutating operations, so that a failed client can harmlessly resubmit any forgotten requests;\n- rate-limits finding new places for tasks from machines that become unreachable, because it cannot distinguish between large-scale machine failure and a network partition;\n- avoids repeating task::machine pairings that cause task or machine crashes; and\n- recovers critical intermediate data written to local disk by repeatedly re-running a logsaver task (§2.4), even if the alloc it was attached to is terminated or moved to another machine. Users can set how long the system keeps trying; a few days is common."))
            normalized.append(type(unit)(page=6, order=unit.order, kind="paragraph", text="A key design feature in Borg is that already-running tasks continue to run even if the Borgmaster or a task’s Borglet goes down. But keeping the master up is still important because when it is down new jobs cannot be submitted or existing ones updated, and tasks from failed machines cannot be rescheduled."))
            continue
        if name == "borg" and (
            unit.text.startswith("chine if necessary;")
            or unit.text.startswith("during maintenance activities")
            or unit.text.startswith("a few days is common.")
        ):
            continue
        if name == "borg" and unit.text == "5 Utilization":
            normalized.append(unit)
            normalized.append(type(unit)(page=6, order=unit.order, kind="paragraph", text="One of Borg’s primary goals is to make efficient use of Google’s fleet of machines, which represents a significant financial investment: increasing utilization by a few percentage points can save millions of dollars. This section discusses and evaluates some of the policies and techniques that Borg uses to do so."))
            continue
        if name == "omega" and unit.text in {"Mean job wait time [log10]", "single Batch sched."}:
            continue
        if name == "omega" and unit.text.startswith("Since we now have two schedulers,"):
            unit.text = unit.text.replace("insufficient 0.1s 1s 1m 1h 1d to schedule", "insufficient to schedule")
        if name == "omega" and "manyoptimizations" in unit.text:
            unit.text = unit.text.replace("manyoptimizations", "many optimizations")
        if name == "omega" and unit.kind == "footnote" and unit.text.startswith("2 We describe"):
            left, right = unit.text.split(" 3 The Mesos", 1)
            normalized.append(type(unit)(**{**unit.__dict__, "text": left}))
            normalized.append(type(unit)(**{**unit.__dict__, "text": "3 The Mesos" + right}))
            continue
        if name == "omega" and unit.text.startswith("Having compared the different scheduler architectures"):
            lead, _questions = unit.text.split(" 1. How much", 1)
            normalized.append(type(unit)(**{**unit.__dict__, "text": lead}))
            normalized.append(type(unit)(**{**unit.__dict__, "text": "1. How much scheduling interference is present in real-world workloads and what scheduler decision times can we afford in production (§5.1)?"}))
            continue
        if name == "omega" and unit.text.startswith("world workloads and what scheduler"):
            continue
        if name == "omega" and unit.text.startswith("3. Can we take advantage"):
            normalized.append(type(unit)(**{**unit.__dict__, "kind": "paragraph", "text": "3. Can we take advantage of having access to the entire state of the cell in a scheduler? (§6)"}))
            continue
        if name == "omega" and unit.text.startswith("of the cell in a scheduler? (§6)"):
            unit.text = unit.text.removeprefix("of the cell in a scheduler? (§6) ")
        normalized.append(unit)
        if name == "borg" and unit.text.startswith("In production, we deliberately leave significant headroom"):
            normalized.append(borg_figure_4)

    if name == "omega":
        # Figure 9 concludes §4; Figure 14 and footnote 7 conclude §5.2. Their
        # PDF floats appear beside the following section and must not split it.
        def move_before(text_prefix: str, heading: str) -> None:
            source_index = next(i for i, u in enumerate(normalized) if u.text.startswith(text_prefix))
            moving = normalized.pop(source_index)
            target_index = next(i for i, u in enumerate(normalized) if u.text == heading)
            normalized.insert(target_index, moving)

        move_before("Figure 9:", "5 Trace-driven simulation")
        move_before("7 This is supported", "6 Flexibility: a MapReduce scheduler")
        move_before("Figure 14:", "6 Flexibility: a MapReduce scheduler")

        math_tokens = {
            "tdecision(service)": r"$t_{\mathrm{decision}}(\mathrm{service})$",
            "tjob(service)": r"$t_{\mathrm{job}}(\mathrm{service})$",
            "ttask(service)": r"$t_{\mathrm{task}}(\mathrm{service})$",
            "tjob(batch)": r"$t_{\mathrm{job}}(\mathrm{batch})$",
            "λjobs(batch)": r"$\lambda_{\mathrm{jobs}}(\mathrm{batch})$",
            "λjobs": r"$\lambda_{\mathrm{jobs}}$",
            "tdecision": r"$t_{\mathrm{decision}}$",
            "tjob": r"$t_{\mathrm{job}}$",
            "ttask": r"$t_{\mathrm{task}}$",
        }
        for unit in normalized:
            for plain, markup in math_tokens.items():
                unit.text = unit.text.replace(plain, markup)

    # PDF figures float into neighbouring columns and can otherwise split an
    # unrelated section. Place every figure/table immediately after its first
    # textual citation, preserving numerical order when one paragraph cites
    # several assets.
    assets = [unit for unit in normalized if unit.kind in {"figure", "table"}]
    prose = [unit for unit in normalized if unit.kind not in {"figure", "table"}]
    anchored: dict[int, list] = {}
    unanchored = []
    for asset in assets:
        label = re.match(r"^(Figure|Table)\s+(\d+)", asset.text)
        if not label:
            unanchored.append(asset)
            continue
        singular = label.group(1)
        number = label.group(2)

        def cites(unit) -> bool:
            if unit.kind not in {"paragraph", "footnote"}:
                return False
            direct = rf"\b{singular}s?\s+{number}[a-z]?\b"
            grouped = rf"\b{singular}s\s+[0-9a-z,\sand–-]{{0,40}}\b{number}[a-z]?\b"
            return bool(re.search(direct, unit.text) or re.search(grouped, unit.text))

        anchor = next((unit for unit in prose if cites(unit)), None)
        if anchor is None:
            unanchored.append(asset)
        else:
            anchored.setdefault(id(anchor), []).append(asset)
    placed = []
    for unit in prose:
        placed.append(unit)
        placed.extend(sorted(anchored.get(id(unit), []), key=caption_number))
    placed.extend(unanchored)

    # Author notes and the ACM permission notice belong with the byline rather
    # than in the middle of the first body column.
    front_notes = [
        unit
        for unit in placed
        if unit.text.startswith(("† Work done", "∗Work done", "Permission to make"))
    ]
    placed = [unit for unit in placed if unit not in front_notes]
    placed = front_notes + placed

    # Keep numbered footnotes next to their first superscript marker. PDF
    # bottom-of-column placement can otherwise leave them several sections away.
    numbered_footnotes = [unit for unit in placed if unit.kind == "footnote" and re.match(r"^\d+\s", unit.text)]
    body = [unit for unit in placed if unit not in numbered_footnotes]
    footnote_anchors: dict[int, list] = {}
    unattached_footnotes = []
    for footnote in numbered_footnotes:
        number = re.match(r"^(\d+)\s", footnote.text).group(1)
        anchor = next((unit for unit in body if f"<sup>{number}</sup>" in unit.text), None)
        if anchor is None:
            unattached_footnotes.append(footnote)
        else:
            footnote_anchors.setdefault(id(anchor), []).append(footnote)
    final = []
    for unit in body:
        final.append(unit)
        final.extend(footnote_anchors.get(id(unit), []))
    final.extend(unattached_footnotes)
    return final


def reference_blocks(name: str, archive_root: Path) -> list[str]:
    meta = META[name]
    first, last = meta["reference_pages"]
    raw = subprocess.run(
        ["pdftotext", "-raw", "-f", str(first), "-l", str(last), str(archive_root / PAPERS[name]["pdf"]), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.replace("\f", "\n")
    raw = re.sub(r"(?m)^\d{3}\s*$", "", raw)
    raw = raw[raw.find("References") + len("References") :]
    parts = re.split(r"(?m)^\[(\d+)]\s*", raw)
    refs = []
    for i in range(1, len(parts), 2):
        refs.append(f"[{int(parts[i])}] {join_lines(parts[i + 1].splitlines())}")
    expected = list(range(1, meta["reference_count"] + 1))
    actual = [int(re.match(r"\[(\d+)]", ref).group(1)) for ref in refs]
    if actual != expected:
        raise RuntimeError(f"{name} reference sequence mismatch: {actual}")
    return refs


def protect_reference_authors(text: str) -> str:
    body = re.sub(r"^\[\d+]\s*", "", text)
    offset = text.find(body)
    candidates = [match.end() for match in re.finditer(r"\.\s+", body)]
    cut = None
    for end in candidates:
        prefix = body[: end - 1]
        suffix = body[end:]
        if not suffix:
            continue
        # A full stop may terminate an author's initial rather than the author
        # field ("C. Delimitrou", "T. Akidau").  Likewise, the period after
        # one author's surname can be followed by an explicit conjunction.
        if re.match(r"(?:and|&amp;|&)\s+", suffix, re.I):
            continue
        if re.match(r"[A-Z]\.\s+", suffix):
            continue
        # Omega prints author surnames in all caps.  Testing a fixed prefix of
        # the whole reference is unreliable because a short author list may
        # already include part of the mixed-case title.  Instead test the text
        # up to each candidate full stop.  This also avoids treating the dots
        # in initials such as A.-R. as the end of the author field.
        prefix_letters = re.sub(r"[^A-Za-z]", "", prefix)
        uppercase_author_prefix = len(prefix_letters) > 5 and prefix_letters == prefix_letters.upper()
        if uppercase_author_prefix and (
            re.match(r"[A-Z][a-z]", suffix)
            or (" AND " in prefix and not re.match(r"[A-Z][A-Z-]+,\s+[A-Z](?:\.|,)", suffix))
        ):
            cut = end
            break
        last_and = max(prefix.lower().rfind(" and "), prefix.rfind(" AND "))
        last_word = re.findall(r"[A-Za-z-]+", prefix)
        if last_word and len(last_word[-1].replace("-", "")) > 1 and (last_and < 0 or end > last_and):
            cut = end
            break
    if cut is None:
        return text
    authors = body[:cut].strip()
    rest = body[cut:].strip()
    return text[:offset] + f"`{authors}` {rest}"


def split_reference(text: str) -> tuple[str, str]:
    """Separate the immutable number/authors from translatable bibliography text."""
    protected = protect_reference_authors(text)
    match = re.match(r"^(\[\d+]\s+)`([^`]+)`\s+(.*)$", protected)
    if not match:
        return "", text
    return f"{match.group(1)}{match.group(2)}", match.group(3)


def errata_units(archive_root: Path) -> list[tuple[str, str]]:
    units = [unit for unit in extract("borg", archive_root) if unit.page == 18]
    result = []
    for unit in units:
        text = unit.text
        if text.startswith("Large-scale cluster management"):
            result.append(("heading2", "Errata"))
            result.append(("paragraph", text))
        elif text in {"The user perspective", "Related work", "Acknowledgements"}:
            result.append(("heading3", text))
        elif unit.kind == "heading2" and text == "References":
            result.append(("heading3", "References"))
        else:
            # The two errata references share one PDF text block.
            pieces = re.split(r"(?=\[\d+])", text) if text.startswith("[1]") else [text]
            result.extend(("paragraph", piece.strip()) for piece in pieces if piece.strip())
    return result


def caption_number(unit) -> int:
    number = int(re.match(r"^(?:Figure|Table)\s+(\d+)", unit.text).group(1))
    return number if unit.kind == "figure" else 100 + number


def polish_translation(name: str, source: str, translation: str) -> str:
    """Normalise domain terms after sentence-level MT without harming syntax."""
    text = translation.replace("`", "")
    for old, new in {
        "博格": "Borg",
        "欧米茄": "Omega",
        "梅索斯": "Mesos",
        "映射化简": "MapReduce",
        "调度程序": "调度器",
        "政策": "策略",
        "过度承诺": "超额分配",
        "过度配置": "超额分配",
        "任务打包": "任务装箱",
        "故障恢复": "故障恢复",
        "显着": "显著",
        "在过程中。": "载于：",
        "国际症状。": "国际研讨会",
        "症状。": "研讨会",
        "捐赠公司": "基金会",
        "国际会议关于超大型数据库": "超大型数据库国际会议",
        "USENIX 研讨会关于操作系统设计和实现": "USENIX 操作系统设计与实现研讨会",
        "USENIX 研讨会关于网络系统设计和实现": "USENIX 网络系统设计与实现研讨会",
        "ACM 研讨会关于操作系统原理": "ACM 操作系统原理研讨会",
        "ACM 研讨会关于云计算": "ACM 云计算研讨会",
        "IEEE 传输。并行分布。系统": "IEEE Transactions on Parallel and Distributed Systems",
        "IEEE 传输。关于并行和分布式系统": "IEEE Transactions on Parallel and Distributed Systems",
        "国际会议关于编程语言和操作系统的架构支持": "编程语言与操作系统架构支持国际会议",
        "ACM 研讨会云计算": "ACM 云计算研讨会",
        "技术。众议员": "技术报告",
        "ACM 翻译。计算机系统": "ACM Transactions on Computer Systems",
        "尾巴成比例": "规模化系统的长尾延迟",
        "基于预订的日程安排：如果您迟到了，请不要责怪我们": "基于预留的调度：若作业延迟，请勿归咎于我们",
        "通过重要的交互式分析提高大规模 MapReduce 工作负载的能源效率": "面向包含大量交互式分析的大规模 MapReduce 工作负载的能效",
    }.items():
        text = text.replace(old, new)
    text = re.sub(r"第\s+(\d+)\s+页。\s*(\d+)。", r"第 \2 页。", text)
    text = text.replace("第 14 页。24.", "第 24 页。")

    if re.search(r"\bcells?\b", source, re.I):
        text = text.replace("细胞", "Cell").replace("单元", "Cell")
    if re.search(r"\bjobs?\b", source, re.I):
        for old, new in {
            "一项工作": "一个作业",
            "每项工作": "每个作业",
            "每个工作": "每个作业",
            "工作等待时间": "作业等待时间",
            "工作到达": "作业到达",
            "工作数量": "作业数量",
            "工作类型": "作业类型",
            "工作队列": "作业队列",
            "工作调度": "作业调度",
            "工作标识符": "作业标识符",
            "工作级": "作业级",
        }.items():
            text = text.replace(old, new)
    if re.search(r"\bprod(?:uction)?\b", source, re.I):
        text = text.replace("产品作业", "生产作业").replace("都是产品", "都是生产作业")
    if re.search(r"\bmaster\b", source, re.I):
        for old in ("当选的主站", "当选的船长", "当选的主机"):
            text = text.replace(old, "当选的主节点")

    if name == "borg":
        # Proper names in acknowledgements are immutable source data.  Generic
        # MT starts transliterating halfway through long lists, so construct
        # these few sentences from the English source instead.
        if source.startswith("The initial Borgmaster was primarily designed"):
            return (
                "最初的 Borgmaster 主要由 Jeremy Dion 和 Mark Vandevoorde 设计并实现；"
                "Ben Smith、Ken Ashcraft、Maricia Scott、Ming-Yee Iu 和 Monika Henzinger 也参与其中。"
                "最初的 Borglet 主要由 Paul Menage 设计并实现。"
            )
        if source.startswith("Subsequent contributors include "):
            return "后续贡献者包括 " + source.removeprefix("Subsequent contributors include ")
        if source.startswith("The Borg SRE team has also been crucial"):
            return (
                "Borg SRE 团队同样至关重要，其成员包括 Adam Rogoyski、Alex Milivojevic、Anil Das、"
                "Cody Smith、Cooper Bethea、Folke Behrens、Matt Liggett、James Sanford、John Millikin、"
                "Matt Brown、Miki Habryn、Peter Dahl、Robert van Gent、Seppi Wilhelmi、Seth Hettich、"
                "Torsten Marek 和 Viraj Alankar。Borg 配置语言（BCL）和 borgcfg 工具最初由 "
                "Marcel van Lohuizen 与 Robert Griesemer 开发。"
            )
        if source.startswith("We thank our reviewers"):
            return "我们感谢审稿人（尤其是 Eric Brewer、Malte Schwarzkopf 和 Tom Rodeheffer）以及论文指导人（shepherd）Christos Kozyrakis 对本文提出的意见。"
        text = text.replace("单元压缩", "Cell 压实").replace("Cell 压缩", "Cell 压实").replace("Cell压缩", "Cell 压实")
        text = text.replace("Borg 简化了用户的生活", "Borg 降低了用户的使用负担").replace("简化了用户的生活", "降低了用户的使用负担")
        text = text.replace("需要几秒钟到几天的时间才能完成；这些对短期业绩波动", "需要几秒到几天才能完成；它们对短期性能波动")
        text = text.replace("Borg需要同样出色地", "Borg 必须同样妥善地")
        text = text.replace("博格需要同样出色地", "Borg 必须同样妥善地")
        text = text.replace("生产作业分配了", "生产作业获分配")
        text = text.replace("它们分配了大约 55% 的总内存，并代表了大约 85% 的总内存使用量", "它们还获分配约 55% 的总内存，并约占总内存用量的 85%")
        text = text.replace("分配和使用之间的差异将在第 5.5 节中证明很重要", "这些分配量与实际用量的差异将在 §5.5 中发挥重要作用")
        text = text.replace("具有如此弹性和完整性", "具备如此强韧性与完备性")
        text = text.replace("生产作业是监控和生产范围内的作业", "prod 作业是监控与生产优先级带中的作业")
        text = text.replace("调度量", "调度时间片")
        text = text.replace("在线调度通过待处理队列", "在线调度对待处理队列的一轮遍历")
        text = text.replace("主机将接受并应用这些分配", "主节点会接受并应用这些分配")
        text = text.replace("并将这些任务通知当选的船长", "并把这些分配通知当选的主节点")
        text = text.replace("并将这些任务通知当选的主节点", "并把这些分配通知当选的主节点")
        text = text.replace("最适合我们工作负载的打包效率", "best fit 在我们工作负载上的装箱效率")
        text = text.replace("它提供了大约 3-5% 的打包效率", "它把装箱效率提高了约 3–5%")
        text = text.replace("我们只需克隆原始细胞", "我们只需克隆原始 Cell")
        text = text.replace("每个细胞的每个实验", "每个 Cell 的每项实验")
        text = text.replace("中间单元", "中位 Cell")
        text = text.replace("一项不平凡的投资", "一笔不可忽视的投入")
        text = text.replace("本文解释了如何进行", "本文解释其实现方式")
        text = text.replace("作业可能会受到限制，强制其任务", "作业可以设置约束，要求其任务")
        text = text.replace("我们不想支付虚拟化成本", "我们不愿承担虚拟化开销")
        text = text.replace("该系统是在我们对处理器进行了大量投资而设计的，而硬件上没有虚拟化支持", "系统设计之初，我们已大量部署不支持硬件虚拟化的处理器")
        text = text.replace("并被结构化为二进制文件和数据文件包，其安装由 Borg 精心安排", "并组织成二进制文件与数据文件组成的包，由 Borg 负责安装编排")
        text = text.replace("日志保护程序任务", "logsaver 任务").replace("日志保护任务", "logsaver 任务")
        text = text.replace("关联的logsaver", "关联的 logsaver")
        text = text.replace("Borg alloc（分配的缩写）", "Borg alloc（allocation 的缩写）")
        text = text.replace("分配可用于为将来的任务留出资源", "alloc 可用于为未来任务预留资源")
        text = text.replace("分配的资源的处理方式与机器的资源类似", "alloc 资源的处理方式与机器资源类似")
        text = text.replace("在一个任务中运行的多个任务共享其资源", "在同一个 alloc 中运行的多个任务共享这些资源")
        text = text.replace("如果必须将分配重新定位到另一台计算机", "如果必须把 alloc 迁移到另一台机器")
        text = text.replace("分配集就像一个作业", "alloc set 类似于作业")
        text = text.replace("它是一组在多台机器上保留资源的分配", "它由一组在多台机器上预留资源的 alloc 构成")
        text = text.replace("创建分配集后", "创建 alloc set 后")
        text = text.replace("分配之外的任务", "alloc 之外的任务")
        text = text.replace("作业或分配集", "作业或 alloc set")
        text = text.replace("使用“任务”来指代分配或顶级任务", "使用“任务”来指代 alloc 或顶级任务")
        text = text.replace("状态变异器", "状态变更器")
        text = text.replace("保持主服务器运行", "保持主节点可用")
        text = text.replace("机器故障的复制", "通过复制容忍机器故障")
        text = text.replace("相关操作员错误", "相关运维人员失误")
        text = text.replace("发现它可以安装到多小的Cell中", "确定该工作负载最小能装入多大的 Cell")
        text = text.replace("Borg检查站", "Borg 检查点")
        text = text.replace("任务中断（重新安排或抢占）", "任务中断（重新调度或抢占）")
        text = text.replace("任何会导致更多干扰的更改", "任何会造成更多中断的更改")
        text = text.replace("实际通知可能会更少", "实际提前通知时间可能更短")
        text = text.replace("偶尔检查点", "按需制作检查点")
        text = text.replace("以Borg为例：", "例如，Borg 会：")
        text = text.replace("从头开始反复重新打包工作负载", "反复从头重新装箱工作负载")
        text = text.replace("干净的终止条件", "明确的终止条件")
        text = text.replace("而没有合成工作负载生成和建模的陷阱", "并避开合成工作负载生成和建模的陷阱")
        text = text.replace("重大财务投资", "巨额资本投入")
        text = re.sub(r"(?<=[\u3400-\u9fff0-9])Cell", " Cell", text)
        text = re.sub(r"Cell(?=[\u3400-\u9fff0-9])", "Cell ", text)
        text = text.replace("CPU核", "CPU 核").replace("TCP端口", "TCP 端口")
    else:
        for old in ("单片调度器", "整体式调度器", "整体调度器"):
            text = text.replace(old, "单体调度器")
        text = text.replace("单片", "单体")
        text = text.replace("双级调度", "两级调度")
        text = text.replace("头部阻塞", "队头阻塞").replace("行首阻塞", "队头阻塞")
        text = text.replace("帮派调度", "成组调度")
        text = text.replace("资源报价", "资源 offer")
        text = text.replace("基于报价", "基于 offer")
        text = text.replace("持有报价", "持有 offer")
        text = text.replace("公平共享的报价", "公平份额 offer")
        text = text.replace("资源以优惠的形式", "资源以 offer 的形式")
        text = text.replace("公平份额报价", "公平份额 offer")
        text = text.replace("调度器忙碌程度", "调度器繁忙度").replace("调度器忙碌度", "调度器繁忙度")
        text = text.replace("冲突分数", "冲突比例")
        text = text.replace("干涉。", "干扰。")
        text = text.replace("乐观的人会发现", "乐观方法会检测")
        text = text.replace("相互冲突的主张", "相互冲突的资源申请")
        text = text.replace("紧急行为", "涌现行为")
        text = text.replace("组调度", "成组调度")
        text = text.replace("需求的需求", "需求")
        text = text.replace("现实生活中的 Google 生产工作负载", "Google 真实生产工作负载")
        text = text.replace("与其他架构竞争或优于其他架构的性能", "可与其他架构媲美甚至更优的性能")
        text = text.replace("对现实环境的干扰很低", "在真实环境中的调度器间干扰很低")
        text = text.replace("一项或多项任务", "一个或多个任务")
        text = text.replace("轻量级、低质量的放置方法就很好", "采用轻量、近似的放置方法便已足够")
        text = text.replace("提高对故障的抵抗力", "提高容错能力")
        text = text.replace("独立故障和协调故障", "独立故障与相关故障")
        text = text.replace("只能利用其请求的资源的一小部分", "只获得所请求资源的一小部分也能")
        text = text.replace("软件工程的类别考虑", "这类软件工程考量")
        text = text.replace("实际上是单一的", "实际上仍是单体架构")
        text = text.replace("有机软件增长", "软件的自然增长")
        text = text.replace("每次提供框架时都会向框架提供", "每次生成 offer 时都会向框架给出")
        text = text.replace("其提供的顺序和大小", "offer 的顺序与大小")
        text = text.replace("一次仅向一个框架提供给定资源", "每次只向一个框架 offer 给定资源")
        text = text.replace("它想要提供的类别资源", "它希望获得哪些类别的资源")
        text = text.replace("只能访问它已提供的资源", "只能看到 offer 给它的资源")
        text = text.replace("称为优先级", "称为优先序（precedence）")
        text = text.replace("限制他们可能要求的资源总量", "限制它们可以申请的资源总量")
        text = text.replace("限制他们承认的作业数量", "限制它们准入的作业数量")
        text = text.replace("扩大工作量", "扩展工作负载")
        text = text.replace("以实现实现可扩展性和性能可扩展性", "以同时实现工程可扩展性与性能可扩展性")
        text = text.replace("进行简短的调查", "作简要概览")
        text = text.replace("这项调查是构建", "这项研究是构建")
    return text


def build(name: str, translator: Translator, archive_root: Path) -> str:
    units = clean_units(name, archive_root)
    refs = reference_blocks(name, archive_root)
    translation_inputs = []
    input_index = {}
    for idx, unit in enumerate(units):
        if unit.kind in {"paragraph", "footnote"}:
            input_index[("unit", idx)] = len(translation_inputs)
            translation_inputs.append(unit.text)
    reference_parts = []
    for idx, ref in enumerate(refs):
        fixed, translatable = split_reference(ref)
        reference_parts.append((fixed, translatable))
        input_index[("ref", idx)] = len(translation_inputs)
        translation_inputs.append(translatable)
    extras = errata_units(archive_root) if name == "borg" else []
    for idx, (kind, text) in enumerate(extras):
        if kind == "paragraph":
            input_index[("extra", idx)] = len(translation_inputs)
            _fixed, translatable = split_reference(text) if text.startswith("[") else ("", text)
            translation_inputs.append(translatable)

    translations = translator.translate_many(translation_inputs, batch_size=8)
    out = [frontmatter(name).rstrip()]
    for idx, unit in enumerate(units):
        if unit.kind.startswith("heading"):
            level = int(unit.kind[-1])
            out.append(f"{'#' * level} {unit.text}｜{HEADINGS[unit.text]}")
        elif unit.kind in {"figure", "table"}:
            number = caption_number(unit)
            caption_zh = CAPTION_ZH[name][number]
            explanation = EXPLANATIONS[name][number]
            out.append(f"![{unit.text}]({unit.asset})")
            out.append(f"**{unit.text}**")
            out.append(quote(f"**{caption_zh}**\n\n**图表中文解读：** {explanation}"))
        else:
            if name == "borg" and unit.text.startswith("- automatically reschedules evicted tasks"):
                translated = "- 必要时在新机器上自动重新调度被驱逐的任务；\n- 把同一作业的任务分散到机器、机架和供电域等不同故障域，以降低相关故障风险；\n- 限制任务中断速率，以及维护期间同一作业可同时停机的任务数量；\n- 使用声明式期望状态和幂等变更操作，使失败的客户端可以安全重提遗忘的请求；\n- 对失联机器上的任务重新选址实施限速，因为系统无法立即区分大规模机器故障与网络分区；\n- 避免再次采用曾导致任务或机器崩溃的 task::machine 配对；\n- 即使 alloc 已终止或迁移，也会反复重跑 logsaver 任务以恢复写入本地磁盘的关键中间数据（§2.4）。用户可以指定系统持续尝试的时长，通常会设为数天。"
            else:
                translated = polish_translation(name, unit.text, translations[input_index[("unit", idx)]])
            out.append(unit.text)
            out.append(quote(translated))

    out.append("## References｜参考文献")
    for idx, ref in enumerate(refs):
        out.append(ref)
        fixed, translatable = reference_parts[idx]
        translated = polish_translation(name, translatable, translations[input_index[("ref", idx)]])
        out.append(quote(f"{fixed} {translated}".strip()))

    if extras:
        errata_heading = {"Errata": "勘误", "The user perspective": "用户视角", "Related work": "相关工作", "Acknowledgements": "致谢", "References": "参考文献"}
        for idx, (kind, text) in enumerate(extras):
            if kind.startswith("heading"):
                level = int(kind[-1])
                out.append(f"{'#' * level} {text}｜{errata_heading[text]}")
            else:
                out.append(text)
                fixed, translatable = split_reference(text) if text.startswith("[") else ("", text)
                translated = polish_translation(name, translatable, translations[input_index[("extra", idx)]])
                out.append(quote(f"{fixed} {translated}".strip()))
    return "\n\n".join(out).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a bilingual draft for the configured Borg or Omega paper."
    )
    parser.add_argument("paper", choices=sorted(META))
    parser.add_argument("--model", type=Path)
    parser.add_argument("--provider", choices=("google", "local"), default="google")
    parser.add_argument(
        "--archive-root",
        type=Path,
        required=True,
        help="Archive root containing the configured paper PDF.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory receiving the generated draft (default: ./阅读).",
    )
    parser.add_argument(
        "--cache-path",
        type=Path,
        help="Optional translation cache path for the Google provider.",
    )
    args = parser.parse_args()
    archive_root = args.archive_root.resolve()
    verify_source_pdf(args.paper, archive_root)
    if args.provider == "local":
        if not args.model:
            parser.error("--model is required with --provider local")
        translator = Translator(args.model)
    else:
        translator = GoogleTranslator(args.cache_path)
    result = build(args.paper, translator, archive_root)
    output = args.output_root.resolve() / META[args.paper]["output"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
