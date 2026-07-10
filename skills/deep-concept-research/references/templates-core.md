# 核心研究产物模板

## 目录

- [标准目录](#标准目录)
- [`research-manifest.yaml`](#research-manifestyaml)
- [`CONTEXT.md`](#contextmd)
- [`大纲.md`](#大纲md)
- [Claim Ledger](#claim-ledger)
- [Conflict Ledger](#conflict-ledger)
- [Source-map](#source-map)

模板是最大字段集。删除不适用项时写 N/A 与原因，不要留空表伪装完整。项目已有 frontmatter 或命名约定时优先遵循项目规范，但保留本模板的语义字段。

## 标准目录

```text
<topic>/
├── research-manifest.yaml
├── CONTEXT.md
├── 大纲.md
├── claims/
│   ├── claim-ledger.md
│   └── conflicts.md
├── source-maps/
│   ├── README.md
│   └── <mechanism>.md
├── experiments/
│   ├── README.md
│   ├── src/
│   ├── raw/
│   └── <experiment>.md
├── Q&A/
│   ├── README.md
│   └── <question>.md
├── images/
│   ├── README.md
│   └── specs/
├── reviews/
│   └── <review>.md
├── refresh/
│   └── <old>-to-<new>.md
└── 封版矩阵.md
```

`scaffold` 只必须创建 manifest、CONTEXT、大纲、Claim Ledger、Conflict Ledger 和三个 README。开始实际研究后再创建非空证据工件；不为追求目录完整而建空图片、review 和 refresh 目录。

## `research-manifest.yaml`

```yaml
schema_version: 2
topic_id: "<UPPERCASE-STABLE-ID>"
title: "<专题标题>"
mode: "scaffold"
status: "outline"
primary_archetype: "state-event"
secondary_archetypes: []
scope:
  included:
    - "<included>"
  excluded:
    - "<excluded>"
  reader: "<reader>"
primary_baselines:
  - name: "<project/spec>"
    role: "implementation"
    repository_or_spec: "<path or official identifier>"
    version: "<tag/version>"
    commit: "<commit or n/a>"
    branch: "<branch or n/a>"
    dirty: "<true/false/n/a>"
    architecture: "<scope>"
    config_features: "<scope>"
experiment_baselines:
  - name: "<environment>"
    os_kernel: "<value>"
    architecture: "<value>"
    toolchain: "<value>"
    artifact_provenance: "<value>"
    permissions: "<value>"
last_verified:
  baseline: "<version/commit or none>"
  review: "<review artifact or none>"
audit:
  mode: "scaffold"
  strict_passed: false
```

不在 manifest 中保存 secret、token、私有连接串或未脱敏的全量环境变量。

## `CONTEXT.md`

```md
---
title: CONTEXT
type: context
status: outline
---

# <专题名>

## Total Question

> <一个可反驳、贯穿整个专题的问题>

## Reader And Deliverables

- Reader:
- Assumed knowledge:
- Deliverables:
- Mode:

## Scope

### Included

### Excluded

### Reopen Conditions

## Research Archetypes

- Primary:
- Secondary:
- Why:
- Interfaces between chains:

## Evidence Baselines

| 名称 | Claim role | 仓库/规范 | version/commit | arch/config | provenance boundary |
| --- | --- | --- | --- | --- | --- |

## Source–Experiment Boundary

<说明主证据、实验二进制与运行环境为什么不默认等价>

## Evidence Contract

- Claim ID:
- Observation ID:
- G0–G3:
- Evidence vector:
- Highest reachable grade exceptions:

## Core Terms

**Term**: <严格定义>
_Not_: <不是什么>
_Layer_: <所属层>
_Source name_: <规范/类型/字段/状态名>

## Required Writing Rules

- <本专题不能违反的特有规则>

## Artifact Contract

| 路径 | 作用 | 不能承担的作用 |
| --- | --- | --- |
```

## `大纲.md`

```md
---
title: 大纲
type: outline
status: outline
---

# <专题标题>

> [!question] Total Question
> <同 CONTEXT>

> [!warning] Highest-risk boundary
> <最容易发生的证据或层级越界>

## Question And Coverage Ledger

| QID | 原始问题/误解 | 来源 | 所属层 | 影响 Claim | 状态/去向 |
| --- | --- | --- | --- | --- | --- |

## Archetype Selection

| 中心链 | 主原型 | 副原型 | 选择理由 | 不使用的原型及原因 |
| --- | --- | --- | --- | --- | --- |

## Concept Axes

| 术语 A | 术语 B | 正交维度 | 所属层 | 实现/规范对应 |
| --- | --- | --- | --- | --- |

## System Layers And Objects

| 层 | Actor | Managed entity | Carrier | 关键对象 | Result/contract |
| --- | --- | --- | --- | --- | --- |

## Main And Secondary Chains

### Main Chain

### Secondary Chain Interfaces

| 主链 | 副链 | 交界对象 | 交付什么 | 不自动意味着 |
| --- | --- | --- | --- | --- |

## Claim Plan

| Claim ID | 预计 statement | Type | 所需主证据 | 所需实验 | 风险 |
| --- | --- | --- | --- | --- | --- |

## Article Dependency Graph

| 顺序 | 文章 | 主问题 | Prerequisite | New claims | Evidence dependencies | Status |
| --- | --- | --- | --- | --- | --- | --- |

## Experiment Roadmap

| Experiment ID | Kind | Competing models | Controlled input | Observation | Safety | Claim |
| --- | --- | --- | --- | --- | --- | --- |

## Open Questions And Non-goals

| 问题 | 风险 | 影响 Claim | 为什么不阻塞 | Reopen condition | Destination |
| --- | --- | --- | --- | --- | --- |
```

## Claim Ledger

```md
---
title: Claim Ledger
type: claim-ledger
status: outline
---

# Claim Ledger

## ID And Status Rules

- Claim ID: `CLM-<TOPIC>-NNN`
- Status: `open|supported|bounded|contradicted|superseded|stale`
- Vector: `G? [PE? EX? VA? AC? RR? TS=?]`

## Claims

| Claim ID | Statement | Type | Scope | Status | Evidence | Source-map | Experiment/OBS | Consumers | Conflict/Supersedes | Last verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CLM-ABC-001 | <单一可反驳主张> | implementation | <scope> | open | G3 [PE0 EX0 VA0 AC0 RR0 TS=local] | - | - | - | - | - |

## Consumer Integrity

| Claim ID | Q&A | Summary/table | Images | Dependent claims | Checked |
| --- | --- | --- | --- | --- | --- |
```

Ledger 中一个 Claim 只有一个以 `| CLM-` 开头的主行。如需详细解释，在表后以 Claim ID 为标题补充，不创建第二主行。

## Conflict Ledger

```md
---
title: Evidence Conflicts
type: conflict-ledger
status: outline
---

# Evidence Conflicts

| Conflict ID | Affected claims | Evidence A | Evidence B | Difference type | Current resolution | Decision evidence | Reopen condition |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Difference Types

- specification-vs-implementation
- version
- architecture-config
- terminology-layer
- observation-variance
- unresolved-source-conflict
```

## Source-map

```md
---
title: <mechanism>
type: source-map
status: draft
---

# <Mechanism> Source Map

> [!question] Core Question
> <这份地图只关闭哪个问题？>

## Claim Scope

- Claims:
- Claim types:
- Included:
- Excluded:

## Evidence Boundary

| 项 | 值 |
| --- | --- |
| repository/spec | |
| version/tag/commit | |
| branch/dirty state | |
| architecture/config/features | |
| dependency/build/loaded artifact | |
| matching experiment | |

## Files And Specifications Read

| 锚点 | 读它的原因 | 当前 checkout 行号 |
| --- | --- | --- |

## Dispatch And Build Selection

<哪个 macro/feature/target/vtable/trait impl/backend/loaded artifact 选中了该实现？>

## Competing Models

| 模型 | 如果为真，源码应有什么 | 排除/保留证据 |
| --- | --- | --- |

## Core Claims

### CLM-ABC-001: <statement>

Evidence: `G1 [PE2 EX0 VA2 AC2 RR0 TS=implementation]`

| 锚点 | 直读事实 |
| --- | --- |
| `commit:path:line` `Type::function` / field | |

Interpretation:

- <由多个锚点支持的解释>
- <未支持的外推>

Counterevidence / alternatives:

- <反证、替代路径或保留缺口>

## Object Classification

| 对象 | 层 | 位置 | 所有/共享 | 生命周期 | 记录什么 | 不是什么 |
| --- | --- | --- | --- | --- | --- | --- |

## Archetype Chain

### Main path
### Slow/fallback path
### Error/cancel/cleanup path
### Failure/recovery path

## Invariants And Negative Claims

## Cross-layer And Secondary-chain Interfaces

## Experiment Alignment

| Claim | Observation | 一致点 | 仍未闭合 | 升级后证据 |
| --- | --- | --- | --- | --- |

## Open Questions

| 问题 | 影响 Claim | 当前等级 | 关闭条件 | 去向 |
| --- | --- | --- | --- | --- |
```
