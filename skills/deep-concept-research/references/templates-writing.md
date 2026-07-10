# 写作与治理产物模板

## 目录

- [Q&A 文章](#qa-文章)
- [读者索引](#读者索引)
- [Review Record](#review-record)
- [Refresh Record](#refresh-record)
- [封版矩阵](#封版矩阵)

## Q&A 文章

```md
---
title: <真问题>
type: qa
status: draft
---

# <真问题>

## Prerequisites

- Required:
- Adds:
- Follow-ups:

## 最短结论

<3–6 句；首次引用主 Claim ID>

## 为什么容易混淆

## 术语和分层坐标

## 关键对象

| 对象 | 层 | 位置 | 所有/共享 | 生命周期 | 作用 | 不是什么 |
| --- | --- | --- | --- | --- | --- | --- |

## 主原型链路

<按 State/Transform/Lookup/Allocation/Protocol/Performance 组织，不固定套等待/唤醒>

## 错误、竞争、Fallback 与恢复

## 什么变了，什么没变

## 横向对比或场景边界

## 常见错误模型

## 诊断问题

1. <用新反例检验心智模型>

## Claim 与证据索引

| Claim | Statement summary | Evidence artifact | Grade/vector | Boundary |
| --- | --- | --- | --- | --- |

## 本文不能证明什么

## 最终心智模型
```

## 读者索引

```md
---
title: Q&A Index
type: qa-index
status: draft
---

# Q&A

本目录是读者入口，不是编辑计划。

| 顺序 | 文章 | 它解决什么 | 前置 | 主 Claim | 状态 |
| --- | --- | --- | --- | --- | --- |

## Reading Paths

- Minimal:
- Mechanism:
- Experiment/research:

## Evidence Entry Points

- Context:
- Claim Ledger:
- Source maps:
- Experiments:
```

## Review Record

```md
---
title: <review name>
type: review
status: draft
---

# <Fact|Rebuttal|Reproduction|Reader> Review

## Review Scope

- Reviewer:
- Artifacts:
- Claims:
- Baseline:
- Out of scope:

## Method

<独立复核/反驳/重跑/读者测试的方法；说明看到了哪些上下文>

## Findings

| ID | Severity | Claim/artifact | Evidence | Finding | Required action | Acceptance check |
| --- | --- | --- | --- | --- | --- | --- |

## Challenges That Did Not Hold

| Challenge | Why it does not rebut | Evidence |
| --- | --- | --- |

## Result

- Claims upgraded/downgraded:
- New conflicts:
- Reproduction update:
- Remaining risk:
```

## Refresh Record

```md
---
title: <old> to <new>
type: refresh
status: draft
---

# Baseline Refresh: <old> -> <new>

## Baselines

| 项 | Old | New |
| --- | --- | --- |

## Impact Scan

| Symbol/field/config/dependency | Referencing claims | Change type | Action |
| --- | --- | --- | --- |

## Claim Revalidation

| Claim | Old status/vector | New evidence | New status/vector | Consumers updated |
| --- | --- | --- | --- | --- |

## Experiments Re-run

| Experiment | Old observations | New observations | Difference | Claim impact |
| --- | --- | --- | --- | --- |

## Superseded Claims

## Remaining Stale Claims

## Audit Result
```

## 封版矩阵

```md
---
title: 封版矩阵
type: audit-matrix
status: draft
---

# <专题> 封版矩阵

## Decision Rules

| 判定 | 含义 |
| --- | --- |
| 通过 | 当前 baseline 下无阻止稳定草稿/封版的问题 |
| 轻微待修 | 结论可用，但元数据、说明或低风险重验待处理 |
| 需修正 | 有事实错误、证据升格、跨层混淆、stale 高风险 Claim 或不可复现依赖 |

## Article Matrix

| 文章 | 前置 | 术语 | Claims | Source | Experiment | Reviews | Images/links | Status | Decision | Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Claim Dependency Matrix

| Claim | Type | Status/vector | Source-map | Experiment/OBS | Consumers | Fact review | Rebuttal review | Reproduction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Open-risk Queue

| Priority | Risk | Affected claims/consumers | Why bounded or blocking | Action | Acceptance check |
| --- | --- | --- | --- | --- | --- |

## Automated Audit

- Command:
- Result:
- Warnings accepted with reason:
- Baseline:
```
