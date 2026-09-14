#!/usr/bin/env python3
"""Build a first bilingual draft of the frozen Kubernetes API conventions.

The script deliberately preserves each English Markdown block byte-for-byte and
adds one Chinese block quote after it. Translation is a drafting aid only; the
result still requires a terminology and source-fidelity review.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path


HEADINGS = {
    "API Conventions": "Kubernetes API 约定",
    "Types (Kinds)": "类型（Kind）",
    "Resources": "资源",
    "Objects": "对象",
    "Metadata": "元数据",
    "Spec and Status": "Spec 与 Status",
    "Typical status properties": "典型的 status 属性",
    "References to related objects": "对相关对象的引用",
    "Lists of named subobjects preferred over maps": "优先使用具名子对象列表，而非映射",
    "Primitive types": "原始类型",
    "Constants": "常量",
    "Unions": "联合类型",
    "Lists and Simple kinds": "List 与 Simple 类别",
    "Differing Representations": "不同的表示形式",
    "Verbs on Resources": "作用于资源的动词",
    "PATCH operations": "PATCH 操作",
    "Short-names and Categories": "短名称与类别分组",
    "Short-names": "短名称",
    "Categories": "类别分组",
    "Idempotency": "幂等性",
    "Optional vs. Required": "可选与必需",
    "Defaulting": "默认值处理",
    "Static Defaults": "静态默认值",
    "Admission Controlled Defaults": "准入控制默认值",
    "Controller-Assigned Defaults (aka Late Initialization)": "控制器赋予的默认值（又称延迟初始化）",
    "What May Be Defaulted": "哪些内容可以设置默认值",
    "Considerations For PUT Operations": "PUT 操作的注意事项",
    "Concurrency Control and Consistency": "并发控制与一致性",
    "Serialization Format": "序列化格式",
    "Units": "单位",
    "Selecting Fields": "选择字段",
    "Object references": "对象引用",
    "Naming of the reference field": "引用字段的命名",
    "Referencing resources with multiple versions": "引用具有多个版本的资源",
    "Handling of resources that do not exist": "处理不存在的资源",
    "Validation of fields": "字段校验",
    "Do not modify the referred object": "不要修改被引用对象",
    "Minimize copying or printing values to the referrer object": "尽量不要向引用方对象复制或输出值",
    "Object References Examples": "对象引用示例",
    "Single resource reference": "单一资源引用",
    "Controller behavior": "控制器行为",
    "Multiple resource reference": "多资源引用",
    "Kind vs. Resource": "Kind 与 Resource",
    "Generic object reference": "通用对象引用",
    "Field reference": "字段引用",
    "HTTP Status codes": "HTTP 状态码",
    "Success codes": "成功状态码",
    "Error codes": "错误状态码",
    "Response Status Kind": "Status 响应类别",
    "Events": "事件",
    "Naming conventions": "命名约定",
    "Namespace Names": "名字空间名称",
    "Label, selector, and annotation conventions": "标签、选择器与注解约定",
    "WebSockets and SPDY": "WebSocket 与 SPDY",
    "Validation": "校验",
    "Automatic Resource Allocation And Deallocation": "资源的自动分配与释放",
    "Representing Allocated Values": "表示已分配的值",
    "When to use a `spec` field": "何时使用 `spec` 字段",
    "When to use a `status` field": "何时使用 `status` 字段",
    "Sequencing operations": "操作顺序",
    "When to use a different type": "何时使用不同类型",
}


# Longest entries are replaced first. These placeholders stop the MT model from
# mistranslating Kubernetes API vocabulary; exact spellings in code spans are
# protected separately.
GLOSSARY = {
    "optimistic concurrency control": "乐观并发控制",
    "shared-state scheduling": "共享状态调度",
    "shared state scheduling": "共享状态调度",
    "two-level scheduling": "两级调度",
    "monolithic schedulers": "单体调度器",
    "monolithic scheduler": "单体调度器",
    "cluster schedulers": "集群调度器",
    "cluster scheduler": "集群调度器",
    "resource reclamation": "资源回收",
    "resource requirements": "资源需求量",
    "admission control": "准入控制",
    "placement constraints": "放置约束",
    "production workloads": "生产工作负载",
    "production workload": "生产工作负载",
    "non-production": "非生产",
    "workloads": "工作负载",
    "workload": "工作负载",
    "schedulers": "调度器",
    "scheduler": "调度器",
    "preemption": "抢占",
    "utilization": "利用率",
    "availability": "可用性",
    "scalability": "可扩展性",
    "tasks": "任务",
    "task": "任务",
    "jobs": "作业",
    "job": "作业",
    "clusters": "集群",
    "cluster": "集群",
    "Borgmaster": "Borgmaster",
    "Borglet": "Borglet",
    "Borg": "Borg",
    "Omega": "Omega",
    "Mesos": "Mesos",
    "MapReduce": "MapReduce",
    "Figure": "图",
    "Table": "表",
    "controller-assigned defaults": "控制器赋予的默认值",
    "admission controlled defaults": "准入控制默认值",
    "optimistic concurrency control": "乐观并发控制",
    "automatic resource allocation": "资源自动分配",
    "declarative configuration": "声明式配置",
    "resource collections": "资源集合",
    "resource collection": "资源集合",
    "resource versions": "资源版本",
    "resource version": "资源版本",
    "API groups": "API 组",
    "API group": "API 组",
    "API objects": "API 对象",
    "API object": "API 对象",
    "API servers": "API 服务器",
    "API server": "API 服务器",
    "desired state": "期望状态",
    "observed state": "观测状态",
    "late initialization": "延迟初始化",
    "garbage collection": "垃圾回收",
    "object references": "对象引用",
    "object reference": "对象引用",
    "field selector": "字段选择器",
    "label selector": "标签选择器",
    "status code": "状态码",
    "status codes": "状态码",
    "subresources": "子资源",
    "subresource": "子资源",
    "namespaces": "名字空间",
    "namespace": "名字空间",
    "controllers": "控制器",
    "controller": "控制器",
    "clients": "客户端",
    "client": "客户端",
    "servers": "服务器",
    "server": "服务器",
    "metadata": "元数据",
    "resources": "资源",
    "resource": "资源",
    "objects": "对象",
    "object": "对象",
    "kinds": "类别",
    "kind": "类别",
    "fields": "字段",
    "field": "字段",
    "idempotency": "幂等性",
    "idempotent": "幂等",
    "defaulting": "默认值处理",
    "serialization": "序列化",
    "validation": "校验",
    "Kubernetes": "Kubernetes",
    "WebSockets": "WebSocket",
    "WebSocket": "WebSocket",
    "SPDY": "SPDY",
    "JSON": "JSON",
    "HTTP": "HTTP",
    "PATCH": "PATCH",
    "POST": "POST",
    "DELETE": "DELETE",
    "OPTIONS": "OPTIONS",
    "PUT": "PUT",
    "GET": "GET",
    "MUST NOT": "禁止",
    "SHOULD NOT": "不应",
    "MAY NOT": "不得",
    "MUST": "必须",
    "SHOULD": "应该",
    "REQUIRED": "必需",
    "OPTIONAL": "可选",
}


FRONTMATTER = '''---
lang: "zh-CN"
pubDatetime: 2024-11-03T12:00:00+08:00
timezone: "Asia/Shanghai"
title: "官方文档 | Kubernetes API Conventions｜Kubernetes API 约定"
featured: false
area: "distributed-systems"
draft: false
tags:
  - "官方文档"
  - "Kubernetes"
  - "Kubernetes API"
  - "API 设计"
  - "控制器"
  - "分布式系统"
description: "Kubernetes API Conventions 官方设计文档中英对照精读：覆盖 Kind 与 Resource、spec/status、幂等性、默认值、并发控制、对象引用及 API 校验。"
---

> **Source and translation basis｜来源与翻译依据**
>
> [Kubernetes API Conventions](https://github.com/kubernetes/community/blob/fb55d44be24fa626d38c9116e966c0237ecd58ab/contributors/devel/sig-architecture/api-conventions.md), frozen at `kubernetes/community` commit [`fb55d44be24f`](https://github.com/kubernetes/community/commit/fb55d44be24fa626d38c9116e966c0237ecd58ab) (2023-10-26). The source repository is licensed under [Apache License 2.0](https://github.com/kubernetes/community/blob/fb55d44be24fa626d38c9116e966c0237ecd58ab/LICENSE).
>
> 原文固定于 `kubernetes/community` 提交 [`fb55d44be24f`](https://github.com/kubernetes/community/commit/fb55d44be24fa626d38c9116e966c0237ecd58ab)（2023-10-26）。本文完整保留可见原文，并在每个语义单元后给出中文翻译；规范性关键词及代码标识符均按原文语义核对。源代码仓库采用 [Apache License 2.0](https://github.com/kubernetes/community/blob/fb55d44be24fa626d38c9116e966c0237ecd58ab/LICENSE) 许可。
>
> **Reading context｜阅读背景：** 本文阅读时间安排在 2024 年 11 月，对应存算分离云原生数据库项目中的 Kubernetes 与 Longhorn 实践。阅读重点是理解声明式 API 为何强调 `spec/status` 分离、基于层级的调谐、幂等更新以及 `resourceVersion` 并发控制。

---
'''


class Translator:
    def __init__(self, model_path: Path) -> None:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        import torch

        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True)
        self.model.eval()
        self.counter = 0

    def protect(self, text: str) -> tuple[str, dict[str, str]]:
        values: dict[str, str] = {}

        def put(value: str, replacement: str | None = None) -> str:
            # Short alphanumeric sentinels survive Marian tokenization exactly;
            # longer English-looking sentinels are occasionally transliterated.
            key = f"XQ{self.counter:06d}X"
            self.counter += 1
            values[key] = value if replacement is None else replacement
            return key

        # Keep code literals, HTML tags, and link targets byte-identical.
        text = re.sub(r"`[^`]+`", lambda m: put(m.group(0)), text)
        text = re.sub(r"\$[^$]+\$", lambda m: put(m.group(0)), text)
        text = re.sub(r"<[^>]+>", lambda m: put(m.group(0)), text)
        text = re.sub(r"(?<=\()https?://[^)]+", lambda m: put(m.group(0)), text)

        for english, chinese in sorted(GLOSSARY.items(), key=lambda kv: len(kv[0]), reverse=True):
            flags = 0 if english.isupper() else re.IGNORECASE
            pattern = re.compile(rf"(?<![A-Za-z]){re.escape(english)}(?![A-Za-z])", flags)
            text = pattern.sub(lambda _m, zh=chinese: put("", zh), text)
        return text, values

    @staticmethod
    def split_long(text: str, limit: int = 900) -> list[str]:
        if len(text) <= limit:
            return [text]
        sentences = re.split(r"(?<=[.!?;:])\s+(?=[A-Z0-9\[(`*X])", text)
        chunks: list[str] = []
        current = ""
        for sentence in sentences:
            if current and len(current) + len(sentence) + 1 > limit:
                chunks.append(current)
                current = sentence
            else:
                current = f"{current} {sentence}".strip()
        if current:
            chunks.append(current)
        return chunks

    def translate_many(self, texts: list[str], batch_size: int = 8) -> list[str]:
        protected: list[str] = []
        maps: list[dict[str, str]] = []
        owners: list[int] = []
        for owner, text in enumerate(texts):
            safe, values = self.protect(text)
            chunks = self.split_long(safe)
            protected.extend(chunks)
            maps.extend([values] * len(chunks))
            owners.extend([owner] * len(chunks))

        translated_chunks: list[str] = []
        for start in range(0, len(protected), batch_size):
            batch = protected[start : start + batch_size]
            encoded = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )
            with self.torch.inference_mode():
                generated = self.model.generate(
                    **encoded,
                    max_new_tokens=512,
                    num_beams=1,
                )
            translated_chunks.extend(self.tokenizer.batch_decode(generated, skip_special_tokens=True))

        grouped: list[list[str]] = [[] for _ in texts]
        for translated, values, owner in zip(translated_chunks, maps, owners):
            for key, value in values.items():
                translated = translated.replace(key, value)
            translated = translated.replace(" ** ", "**").replace("* *", "**")
            translated = re.sub(r"\s+([，。；：！？、])", r"\1", translated)
            translated = translated.replace(";", "；").replace(":", "：")
            grouped[owner].append(translated.strip())
        return [" ".join(parts) for parts in grouped]


class GoogleTranslator:
    """Use the public Google Translate endpoint as a higher-quality first draft."""

    endpoint = "https://translate.googleapis.com/translate_a/single"
    separator = "ZXBLOCKSEPZX"

    def __init__(self, cache_path: Path | None = None) -> None:
        # Reuse the exact placeholder/glossary logic without loading Marian.
        self.counter = 0
        self.cache_path = cache_path or Path(".review/google-translate-cache.json")
        try:
            self.cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            self.cache = {}

    split_long = staticmethod(lambda text, limit=3500: Translator.split_long(text, limit))

    def protect(self, text: str) -> tuple[str, dict[str, str]]:
        """Protect syntax without hiding ordinary words from the translator.

        Google already translates the domain vocabulary well when it can see the
        complete sentence. Replacing every occurrence of words such as resource,
        object, or MUST with sentinels makes Chinese word order noticeably worse.
        Only byte-sensitive Markdown/API syntax is therefore protected here;
        terminology is normalised after whole-sentence translation and reviewed.
        """
        values: dict[str, str] = {}

        def put(value: str, replacement: str | None = None) -> str:
            key = f"XQ{self.counter:06d}X"
            self.counter += 1
            values[key] = value if replacement is None else replacement
            return key

        text = re.sub(r"`[^`]+`", lambda m: put(m.group(0)), text)
        text = re.sub(r"<[^>]+>", lambda m: put(m.group(0)), text)
        # Preserve every Markdown link destination, including relative anchors.
        text = re.sub(r"(?<=\]\()[^)]+(?=\))", lambda m: put(m.group(0)), text)
        # Quoted single-token strings in this document are API values or names,
        # not prose quotations ("Pod", "apiVersion", "*.k8s.io", ...).
        text = re.sub(r'"[-A-Za-z0-9_./*:+]+"', lambda m: put(m.group(0)), text)
        # The document explicitly distinguishes Kind from type. Generic MT uses
        # both “类型” and “种类” for Kind, erasing that distinction.
        text = re.sub(r"(?<![A-Za-z])kinds?(?![A-Za-z])", lambda m: put(m.group(0), "类别"), text, flags=re.I)
        return text, values

    @staticmethod
    def polish(text: str) -> str:
        # MT occasionally inserts spaces around restored sentinels or between two
        # Chinese words. Neither is meaningful in Chinese prose.
        text = re.sub(r"(?<=[\u3400-\u9fff])\s+(?=[\u3400-\u9fff])", "", text)
        text = re.sub(r"\s+([，。；：！？、）])", r"\1", text)
        text = re.sub(r"([（])\s+", r"\1", text)
        text = re.sub(r"([，。；：！？、])\s+", r"\1", text)
        text = re.sub(r" {2,}", " ", text)
        # Stable terminology where generic MT has a known non-technical sense.
        text = text.replace("基于关卡", "基于层级")
        text = text.replace("基于级别", "基于层级")
        text = text.replace("基于边缘", "基于边沿")
        text = text.replace("边缘触发", "边沿触发")
        text = text.replace("调度程序", "调度器")
        text = text.replace("声明性", "声明式")
        text = text.replace("命令性", "命令式")
        text = text.replace("群组", "组")
        text = text.replace(" - ", "——")
        text = text.replace("发布或放置对象的新版本", "发布对象的新版本或通过 PUT 写入新版本")
        text = text.replace("在 5 处“触及基础”", "经历 5 这一中间状态")
        text = text.replace("规范中的字段应该具有声明式的而不是命令式的名称和语义", "规约中的字段应该采用声明式而非命令式的名称与语义")
        text = text.replace("然后将其放回来", "然后再通过 PUT 写回")
        text = text.replace("允许状态突变", "允许修改状态")
        text = text.replace("控制器编写的对象的观察状态", "控制器对对象所观测状态")
        text = text.replace("观察状态", "观测状态")
        return text.strip()

    def request(self, texts: list[str]) -> list[str]:
        import requests

        result: list[str | None] = [self.cache.get(text) for text in texts]
        missing_indexes = [index for index, value in enumerate(result) if value is None]
        if not missing_indexes:
            return [value for value in result if value is not None]
        missing_texts = [texts[index] for index in missing_indexes]
        payload = f"\n\n{self.separator}\n\n".join(missing_texts)
        last_error = None
        for attempt in range(5):
            try:
                response = requests.get(
                    self.endpoint,
                    params={"client": "gtx", "sl": "en", "tl": "zh-CN", "dt": "t", "q": payload},
                    timeout=45,
                )
                response.raise_for_status()
                translated = "".join(part[0] for part in response.json()[0] if part[0])
                pieces = re.split(self.separator, translated, flags=re.IGNORECASE)
                if len(pieces) == len(missing_texts):
                    for index, source, piece in zip(missing_indexes, missing_texts, pieces):
                        value = piece.strip()
                        result[index] = value
                        self.cache[source] = value
                    self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                    self.cache_path.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    return [value for value in result if value is not None]
                last_error = RuntimeError(f"separator count mismatch: expected {len(missing_texts)}, got {len(pieces)}")
            except Exception as exc:  # transient endpoint and rate-limit failures
                last_error = exc
            time.sleep(1.5 * (attempt + 1))
        if len(missing_texts) > 1:
            result = []
            for text in texts:
                result.extend(self.request([text]))
            return result
        raise RuntimeError(f"translation request failed: {last_error}")

    def translate_many(self, texts: list[str], batch_size: int = 8) -> list[str]:
        protected: list[str] = []
        maps: list[dict[str, str]] = []
        owners: list[int] = []
        for owner, text in enumerate(texts):
            safe, values = self.protect(text)
            chunks = self.split_long(safe)
            protected.extend(chunks)
            maps.extend([values] * len(chunks))
            owners.extend([owner] * len(chunks))

        translated_chunks: list[str] = []
        current: list[str] = []
        current_size = 0
        for text in protected:
            separator_cost = len(self.separator) + 4 if current else 0
            if current and (len(current) >= batch_size or current_size + separator_cost + len(text) > 4300):
                translated_chunks.extend(self.request(current))
                current = []
                current_size = 0
            current.append(text)
            current_size += separator_cost + len(text)
        if current:
            translated_chunks.extend(self.request(current))

        grouped: list[list[str]] = [[] for _ in texts]
        for translated, values, owner in zip(translated_chunks, maps, owners):
            for key, value in values.items():
                translated = translated.replace(key, value)
            grouped[owner].append(self.polish(translated))
        return [" ".join(parts) for parts in grouped]


LIST_ITEM = re.compile(r"^(\s*)([*+-]|\d+[.)])\s+(.*)$")


def flatten_paragraph(raw: str) -> str:
    return re.sub(r"\s*\n\s*", " ", raw.strip())


def list_items(raw: str) -> list[tuple[str, str, str]]:
    """Return indent, marker and one semantic item string."""
    result: list[tuple[str, str, str]] = []
    indent = marker = ""
    body: list[str] = []
    for line in raw.splitlines():
        match = LIST_ITEM.match(line)
        if match:
            if body:
                result.append((indent, marker, " ".join(body).strip()))
            indent, marker, first = match.groups()
            body = [first.strip()]
        elif not line.strip():
            if body and body[-1] != "":
                body.append("")
        elif body:
            body.append(line.strip())
    if body:
        result.append((indent, marker, " ".join(body).strip()))
    return result


def quote(text: str) -> str:
    return "\n".join(">" if not line else f"> {line}" for line in text.splitlines())


def top_level_blocks(source: str):
    from markdown_it import MarkdownIt

    lines = source.splitlines()
    tokens = MarkdownIt("commonmark").parse(source)
    for index, token in enumerate(tokens):
        if token.level != 0 or token.map is None:
            continue
        if token.type not in {
            "heading_open",
            "paragraph_open",
            "bullet_list_open",
            "ordered_list_open",
            "fence",
            "code_block",
            "hr",
            "html_block",
        }:
            continue
        start, end = token.map
        raw = "\n".join(lines[start:end])
        inline = ""
        if token.type == "heading_open":
            inline = tokens[index + 1].content
        yield token.type, raw, inline


def build(source: str, translator: Translator) -> str:
    blocks = list(top_level_blocks(source))
    translatable: list[str] = []
    slots: list[tuple[int, str, object]] = []

    for i, (kind, raw, inline) in enumerate(blocks):
        if kind == "paragraph_open":
            slots.append((i, "paragraph", len(translatable)))
            translatable.append(flatten_paragraph(raw))
        elif kind in {"bullet_list_open", "ordered_list_open"}:
            parsed = list_items(raw)
            indexes = []
            for _indent, _marker, body in parsed:
                indexes.append(len(translatable))
                translatable.append(body)
            slots.append((i, "list", (parsed, indexes)))

    translations = translator.translate_many(translatable)
    slot_map = {block_index: (kind, payload) for block_index, kind, payload in slots}
    out = [FRONTMATTER.rstrip()]

    for i, (kind, raw, inline) in enumerate(blocks):
        if kind == "heading_open":
            if inline == "API Conventions":
                continue
            level_match = re.match(r"^(#+)", raw)
            level = len(level_match.group(1)) if level_match else 2
            out.append(f"{'#' * level} {inline}｜{HEADINGS[inline]}")
        elif kind in {"fence", "code_block", "hr", "html_block"}:
            out.append(raw)
        elif kind == "paragraph_open":
            _slot_kind, index = slot_map[i]
            out.append(raw.rstrip())
            translated = "**目录**" if flatten_paragraph(raw) == "**Table of Contents**" else translations[index]
            out.append(quote(translated))
        else:
            _slot_kind, payload = slot_map[i]
            parsed, indexes = payload
            translated_lines = []
            for (indent, marker, _body), index in zip(parsed, indexes):
                translated = translations[index]
                toc = re.fullmatch(r"\[([^]]+)]\((#[^)]+)\)", _body)
                if toc:
                    title, anchor = toc.groups()
                    normalized_title = title.replace("<code>", "`").replace("</code>", "`")
                    if normalized_title in HEADINGS:
                        translated = f"[{HEADINGS[normalized_title]}]({anchor})"
                translated_lines.append(f"{indent}{marker} {translated}")
            out.append(raw.rstrip())
            out.append(quote("\n".join(translated_lines)))

    return "\n\n".join(out).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--provider", choices=("google", "local"), default="google")
    args = parser.parse_args()
    source = args.source.read_text(encoding="utf-8")
    if args.provider == "local":
        if not args.model:
            parser.error("--model is required with --provider local")
        translator = Translator(args.model)
    else:
        translator = GoogleTranslator()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build(source, translator), encoding="utf-8")


if __name__ == "__main__":
    main()
