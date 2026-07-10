# 研究计划与领域适配

## 目录

- [何时使用 program 模式](#何时使用-program-模式)
- [研究计划结构](#研究计划结构)
- [深度梯子](#深度梯子)
- [多仓库与多组件拓扑](#多仓库与多组件拓扑)
- [证据可用性等级](#证据可用性等级)
- [领域适配器](#领域适配器)
- [源码语言与构建适配](#源码语言与构建适配)
- [实验室和数据集](#实验室和数据集)
- [跨专题复用与一致性](#跨专题复用与一致性)
- [Program 完成定义](#program-完成定义)

## 何时使用 program 模式

满足任一条时，先建研究计划，再在其下开专题：

- 研究跨越多个产品/项目，需要共享概念坐标、实验室或视觉语言；
- 一个系统本身由多仓库/多组件组成，不锁定组件拓扑就无法表述 Claim；
- 需要持续追踪上游版本，或对多实现做同坐标比较；
- 专题数量足以产生术语重复、Claim 冲突、baseline 漂移和图示不一致。

Program 是治理层，不直接容纳所有实现细节。具体 Claim、source-map、experiment 和 Q&A 仍归属于边界清晰的 topic。

默认限制同时进行中的高成本工作：最多两个 source-tracing topic 加一个实验 topic。只有在用户、计算/实验资源和 integrator 容量明确允许时才提高 WIP；否则 baseline 漂移、Claim 待整合和 raw artifact 积压会形成隐形的第二研究计划。

## 研究计划结构

```text
<research-program>/
├── research-program.yaml
├── 00-index/
│   ├── topic-registry.md
│   ├── component-registry.md
│   ├── baseline-registry.md
│   ├── concept-registry.md
│   ├── cross-topic-claims.md
│   ├── coverage-matrix.md
│   └── visual-registry.md
├── labs/
│   ├── README.md
│   ├── environments/
│   ├── datasets/
│   └── workloads/
└── topics/
    └── <topic>/
```

现有知识库不必重排为该物理结构。保留当前目录组织，通过 registry 记逻辑关系即可。

### `research-program.yaml` 最小字段

```yaml
schema_version: 1
program_id: "<ID>"
title: "<title>"
status: "active"
domains: []
topic_registry: "00-index/topic-registry.md"
component_registry: "00-index/component-registry.md"
baseline_registry: "00-index/baseline-registry.md"
concept_registry: "00-index/concept-registry.md"
visual_registry: "00-index/visual-registry.md"
lab_root: "labs"
```

### Topic Registry

| Topic ID | 标题 | Domain | Components | Target depth | Mode/status | Baseline set | Depends on | Highest risk | Entry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

### Baseline Registry

| Baseline ID | Project/component | Repository/spec | Version/tag | Commit | Branch/dirty | Build/config | Artifact provenance | Topics | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Program 中不允许同一 `Baseline ID` 在不同专题指向不同 commit。需要升级时新建 candidate baseline，refresh 完成后再切换当前指针。

`00-index/*.md` 和 `labs/README.md` 使用项目统一 frontmatter，至少有 `title`、`type`、`status`；空的环境/数据集/workload 子目录不需为占位创建。

## 深度梯子

为每个 topic 声明目标深度，避免用“完整研究某大型系统”伪装无边界的完成。

| 深度 | 产出 | 不宣称 |
| --- | --- | --- |
| D0 Landscape | 系统边界、组件、用户契约、问题地图 | 内部机制已闭合 |
| D1 Concept | 严格术语、分层、对象地图、主误解 | 关键源码路径已追通 |
| D2 Source | 主链 source-map、Claim Ledger 与 build/dispatch provenance | 实机行为已对齐 |
| D3 Experimental | 关键机制 Claim 有可复现实验与 OBS | 性能/故障/可移植性已完成 |
| D4 Adversarial | 边界、竞争、故障、性能、跨版本/架构和反驳评审 | 所有实现或负载普遍成立 |
| D5 Synthesis | 文章树、视觉图谱、跨实现总表、封版与 refresh 能力 | 专题不再需要维护 |

深度是目标与验收维度，不是简单的文件数量。一个 D2 专题可以比一个篇幅巨大但无 source-map 的文章更深。

## 多仓库与多组件拓扑

对分布式数据库、云服务、编译工具链或 agent 平台，一条用户路径可能跨越多仓库和多进程。先建 component topology，再分配 Claim。

| Component ID | Role | Repository | Baseline | Process/runtime | Data/control plane | Public contract | Upstream/downstream | Lab entry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

每条跨组件 Claim 还要记：

- 发起组件和接收组件；
- 协议/API/schema 版本；
- 序列化和持久化边界；
- 请求/任务/transaction ID 如何跨组件关联；
- 哪个组件做决策，哪个只执行或缓存；
- 网络、时钟、重试、重复和部分失败条件。

例如 TiDB/TiKV/PD 类系统不应以“TiDB 源码”统称整条事务路径；应先按当前锁定版本的组件责任和协议边界拆分。

## 证据可用性等级

| 类型 | 条件 | 研究策略 | 内部机制 Claim 上限 |
| --- | --- | --- | --- |
| `OPEN-LOCAL` | 有锁定的本地官方源码，可编译/运行 | 本地源码为主，本地实验闭合 | 可到 G0 |
| `OPEN-REMOTE` | 官方开源，但当前无本地锁定仓库 | 先固定官方 tag/commit，必要时获取本地副本 | 未锁定前保守 G3/G1-doc |
| `MIXED` | 部分开源、部分托管/专有 | 将开源组件机制、公开 contract 和黑盒行为分开 | 专有边界最高为 contract G1 或 observation G2 |
| `CLOSED` | 无可核验实现源码 | 官方文档/契约+黑盒实验，不猜内部对象 | 内部 implementation Claim 保持 G3 |

对会快速变化的开发者工具、AI agent 和托管服务，答复当前 API/功能/版本时先核验官方最新文档和 release source；如项目有专用文档 skill/连接器，优先使用。对 OpenAI/Codex 类官方产品问题，使用当前可用的官方文档能力，不以记忆代替当前契约。

## 领域适配器

### Linux/内核/系统软件

- 主原型：State、Lookup、Allocation；性能文加 Performance。
- 源码关键：架构分支、Kconfig、宏/函数指针、内核对象、per-CPU、快/慢路径、生命周期。
- 实验关键：运行内核与研究源码差异、权限、架构、sysctl/config、trace 可见性。
- 视觉核心：整机剖面、内存/对象位置、入口与主路径、状态机、架构对照。

### PostgreSQL/MySQL/Redis 类数据库核心

- 主原型：Transform（parser/planner/executor）、Lookup（index/cache）、Allocation（buffer/object）、Protocol（transaction/log/recovery）。
- 源码关键：构建选项、extension/plugin、catalog/schema、存储格式、事务/日志边界、后台线程/进程、配置选中路径。
- 实验关键：固定 schema/dataset/workload、缓存冷热、计划可见性、WAL/binlog/AOF 持久化、crash recovery、并发隔离。
- 视觉核心：query pipeline、对象/缓存层、事务时序、日志到恢复、计划/数据流。

### Neon/TiDB/TiKV/PD 类多组件数据系统

- 主原型：Protocol、Allocation、Lookup；查询层另加 Transform。
- 先建 component topology，区分 compute/storage/control plane、元数据、日志、共识/副本、路由和调度责任。
- 源码关键：多仓库版本组合、protocol/schema compatibility、client/server 边界、生成代码和特性开关。
- 实验关键：多进程日志关联、网络故障、重试/重复、leader/调度变化、持久化和数据不变量。
- 视觉核心：组件拓扑、请求跨进程时序、数据/控制面分离、副本状态机、故障恢复。

### Go/Rust/TypeScript 类语言、编译器与运行时

- 主原型：Transform（编译/lowering）、State（runtime/task/GC）、Allocation（heap/object）。
- 源码关键：前端/IR/backend 与 runtime 分层，标准库与语言语义分层，build tag/cfg/feature/target、生成代码和实际加载 runtime。
- 实验关键：安装工具链与研究源码版本，compiler flags、优化级别、平台 target、runtime trace、生成产物反编译/诊断。
- 视觉核心：源码到 IR/产物、编译时与运行时边界、对象布局、scheduler/GC 状态。

### Codex/OpenClaw/Hermes 类 AI agent 与开发者工具

- 先确定精确项目、仓库/产品、版本和托管/本地边界；名称有歧义时不自行选一个实现。
- 主原型：State（agent loop/task）、Protocol（tool/MCP/API）、Transform（prompt/context/output）、Allocation（context/artifact/session）。
- 源码关键：开源与专有边界、插件/skill/tool 加载、沙箱/权限、消息与事件 schema、模型或远程服务的外部 contract。
- 实验关键：固定版本/配置/工具集、使用可重放任务和安全 fixture、保存脱敏 trace、分开随机性与系统机制、不将单次模型输出当实现保证。
- 视觉核心：agent loop、context assembly、tool call 时序、权限/沙箱边界、插件拓扑、产物生命周期。

## 源码语言与构建适配

| 生态 | 必查选择边界 | 常见错误 |
| --- | --- | --- |
| C/C++ | preprocessor、Kconfig/configure/CMake/Meson、函数指针/vtable、架构 asm、生成文件、动态链接 | 只看一个 `#ifdef` 分支，不证明它被构建/运行 |
| Go | module/workspace、build tags、GOOS/GOARCH、runtime asm、generated code、linkname、实际 Go toolchain | 把安装 Go 的行为当本地 study tree 的证据 |
| Rust | Cargo.lock、features、cfg/target、trait impl、proc macro/build script、MIR/LLVM、panic/allocator/runtime | 把 trait contract、compiler lowering 和 executor/runtime 当成一层 |
| TypeScript/Node | package lock、tsconfig、transpiler/bundler、ESM/CJS、Node/browser/runtime、generated JS/source map | 只读 TS 源码，不确认实际执行产物和 runtime |
| SQL/DB | build flags、extension/plugin、server config、catalog/schema、plan cache、storage format、background worker | 把 SQL 规范、产品契约和某个 execution plan 当成一件事 |
| Multi-repo RPC | dependency lock、IDL/schema generation、client/server compatibility、feature gates、deployment manifest | 分别读到两端代码却没证明它们是可互操作的版本组合 |

使用当前生态的官方构建和依赖工具验证 provenance，不手工猜测 lockfile 或生成产物关系。

## 实验室和数据集

Program 级 `labs/` 只保存可被多 topic 复用的资产：

- 环境配方：VM/container/image、配置和资源边界；
- 合成/脱敏数据集：schema、生成方法、大小、hash、license；
- workload：请求分布、并发、持续时间、冷热状态和 seed；
- 可控故障注入配方与回滚；
- 可重放 trace/fixture，不含凭证和用户隐私。

具体实验的 raw output 仍放在 topic 下，并引用 lab asset ID 与 hash。共享 workload 升级后，依赖它的 performance Claim 应评估是否 stale。

## 跨专题复用与一致性

### Concept Registry

| Concept ID | Canonical term | Definition | Layer/domain | Not equivalent to | Owning topic | Consumers |
| --- | --- | --- | --- | --- | --- | --- |

一个 topic 可为术语增加领域限定，但不得静默改写共享定义。两个领域同名不同义时，使用层/产品前缀，不强行合并。

### Cross-topic Claim

只在结论真的跨 topic 被消费时才提升到 program 级索引：

| Program Claim ID | Statement | Source topic claims | Transfer scope | Consumers | Refresh trigger |
| --- | --- | --- | --- | --- | --- |

Program Claim 不复制底层证据，只引用 topic Claim ID。任一来源 Claim stale 时，Program Claim 一并 stale。

## Program 完成定义

Program scaffold 完成时：

- 领域、topic 边界、优先级和目标深度已登记；
- 多组件系统有 component topology，所有 baseline ID 唯一且可定位；
- 共享术语、跨 topic Claim、lab asset 和视觉资产都有 owner 与 consumer；
- 每个活跃 topic 至少处于 scaffold，不存在无边界的“研究整个项目”任务；
- 有 baseline 升级、Claim stale 传播和定向 refresh 规则；
- `audit-topic.sh --mode program --strict <program-root>` 通过。

Program 不会在所有 topic 完成后“终结”。它的完成标准是治理和重验能力完整，而不是没有研究 backlog。
