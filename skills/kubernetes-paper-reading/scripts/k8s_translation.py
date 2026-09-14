#!/usr/bin/env python3
"""Translation helpers shared by the Kubernetes paper-reading scripts.

The helpers protect Markdown/API syntax, cache network translations, and keep
the result explicitly in draft status. Optional ML and HTTP dependencies are
loaded only when the selected provider is used, so command-line help remains
available in a minimal environment.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path


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


class Translator:
    """Translate with a local Hugging Face sequence-to-sequence model."""

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
            key = f"XQ{self.counter:06d}X"
            self.counter += 1
            values[key] = value if replacement is None else replacement
            return key

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
    """Use the public Google Translate endpoint for a cached first draft."""

    endpoint = "https://translate.googleapis.com/translate_a/single"
    separator = "ZXBLOCKSEPZX"

    def __init__(self, cache_path: Path | None = None) -> None:
        self.counter = 0
        self.cache_path = cache_path or Path(".review/google-translate-cache.json")
        try:
            self.cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            self.cache = {}

    split_long = staticmethod(lambda text, limit=3500: Translator.split_long(text, limit))

    def protect(self, text: str) -> tuple[str, dict[str, str]]:
        values: dict[str, str] = {}

        def put(value: str, replacement: str | None = None) -> str:
            key = f"XQ{self.counter:06d}X"
            self.counter += 1
            values[key] = value if replacement is None else replacement
            return key

        text = re.sub(r"`[^`]+`", lambda m: put(m.group(0)), text)
        text = re.sub(r"<[^>]+>", lambda m: put(m.group(0)), text)
        text = re.sub(r"(?<=\]\()[^)]+(?=\))", lambda m: put(m.group(0)), text)
        text = re.sub(r'"[-A-Za-z0-9_./*:+]+"', lambda m: put(m.group(0)), text)
        text = re.sub(r"(?<![A-Za-z])kinds?(?![A-Za-z])", lambda m: put(m.group(0), "类别"), text, flags=re.I)
        return text, values

    @staticmethod
    def polish(text: str) -> str:
        text = re.sub(r"(?<=[\u3400-\u9fff])\s+(?=[\u3400-\u9fff])", "", text)
        text = re.sub(r"\s+([，。；：！？、）])", r"\1", text)
        text = re.sub(r"([（])\s+", r"\1", text)
        text = re.sub(r"([，。；：！？、])\s+", r"\1", text)
        text = re.sub(r" {2,}", " ", text)
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
            except Exception as exc:
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


def quote(text: str) -> str:
    """Render translated Markdown as a block quote without changing code."""

    return "\n".join(">" if not line else f"> {line}" for line in text.splitlines())
