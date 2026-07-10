# Claim 与证据协议

## 目录

- [先判定 Claim 类型](#先判定-claim-类型)
- [来源角色 P0–P4](#来源角色-p0p4)
- [闭合摘要 G0–G3](#闭合摘要-g0g3)
- [多维证据向量](#多维证据向量)
- [Claim ID 与 Ledger](#claim-id-与-ledger)
- [证据包与双向链接](#证据包与双向链接)
- [源码深钻协议](#源码深钻协议)
- [否定、推论和冲突](#否定推论和冲突)
- [G0 升级清单](#g0-升级清单)
- [版本失效与重验](#版本失效与重验)

## 先判定 Claim 类型

不同 Claim 要求不同主证据。不要因为本地有源码，就用实现源码代替规范契约或性能数据。

| Claim Type | 典型问题 | 主证据 | 不足以单独支持 |
| --- | --- | --- | --- |
| `contract` | API/协议对调用者承诺什么 | 官方标准、规范、稳定 API 文档 | 某次实现的当前行为 |
| `implementation` | 当前版本如何实现 | 锁定版本的官方源码、build/dispatch 证据 | 二手解释、只看类型名 |
| `observation` | 特定环境观察到什么 | 可复现原始实验、环境和 OBS ID | 源码推断的“应该” |
| `performance` | 某负载下延迟/吞吐/资源如何变化 | 受控 benchmark、统计、基线、机制干预 | 单次计时、纯机制分析 |
| `historical` | 为什么引入/修改某机制 | 官方 commit、评审记录、release note、设计文档 | 从现代代码反推当年动机 |
| `portability` | 结论能否跨版本/架构/实现 | 标准或多实现、多环境直接对照 | 单一实现或单机观察 |
| `security` | 安全边界、攻击面或隔离保证 | threat model、官方安全契约、实现和负向测试 | “看起来没有路径” |

一句话同时包含两种 Claim 时拆开。例如“API 保证非阻塞，所以在本机比阻塞 API 快”必须拆成 contract、implementation 和 performance 三条。

## 来源角色 P0–P4

| 等级 | 角色 | 使用方式 |
| --- | --- | --- |
| P0 | 原始材料/用户知识点 | 控制 coverage；生成问题、矛盾和待核验主张，不关闭事实 |
| P1 | 官方主实现/一级记录 | 关闭 implementation、historical 或实现层 security Claim |
| P2 | 官方规范/标准 | 关闭 contract 与标准层 portability Claim |
| P3 | 官方文档/手册/设计说明 | 解释公开行为；能否单独关闭取决于 Claim 类型 |
| P4 | 书籍、博客、论坛、AI 摘要 | 只作搜索线索、反例和读者误解样本 |

P0–P4 不是简单的“可信度排名”。例如 contract Claim 优先看 P2，而不是用 P1 代码把实现细节写成规范保证。

## 闭合摘要 G0–G3

| 等级 | 含义 |
| --- | --- |
| G0 | 主证据路径与实验闭合，版本/二进制 provenance、架构、配置和 Claim 范围无实质缺口 |
| G1 | 适合该 Claim Type 的主证据闭合，但无对齐实验或对齐不足 |
| G2 | 特定环境的实验观察，内部机制或 provenance 未闭合 |
| G3 | 推论、线索、冲突、stale 或待核验 |

G 等级是人类阅读摘要，不负责表达所有边界。一律同时记证据向量。

## 多维证据向量

标准形式：

```text
G1 [PE2 EX1 VA1 AC2 RR0 TS=implementation]
```

| 维度 | 0 | 1 | 2 |
| --- | --- | --- | --- |
| `PE` Primary Evidence | 无主证据 | 有局部锚点，主路径/前提未全闭合 | 该 Claim Type 需要的主证据路径闭合 |
| `EX` Experiment | 未实验/不适用 | 单环境可复现观察 | 多次或独立复现并有原始记录 |
| `VA` Version/Artifact | 版本或二进制来源不明 | 版本可比但存在修订/build 缺口 | commit/package/build/loaded artifact 已对齐 |
| `AC` Architecture/Config | 未记录 | 已限定范围但未对齐 | 架构、特性、配置与 Claim 对齐 |
| `RR` Reproduction | 未重验 | 原执行者重跑一致 | 独立执行者/环境复现 |

`TS` Transfer Scope 只能取：

- `local`：当前一次环境/二进制；
- `implementation`：锁定实现和版本范围；
- `family`：有多版本/架构/实现对照的族系范围；
- `standard`：规范保证的可移植契约。

G0 通常要求 `PE2 EX1+ VA2 AC2`。`RR2` 可标为 G0-R，但不强制所有机制 Claim 都独立复现。contract Claim 若实验不能增加其规范证明力，保持 G1/`TS=standard`，不为追求 G0 做无意义实验。

## Claim ID 与 Ledger

### ID

使用 `CLM-<TOPIC>-NNN`：

- `<TOPIC>` 是 2–12 位稳定大写英数缩写，不含版本；
- `NNN` 是只增不复用的三位数；
- 主张修改到语义不再等价时，旧 ID 标 `superseded`，新建 ID；
- 纯编辑改写不换 ID。

### 状态

| 状态 | 含义 |
| --- | --- |
| `open` | 尚未达到所需证据门槛 |
| `supported` | 在 Scope 内已闭合 |
| `bounded` | 主体可用，但有不影响当前结论的明确边界 |
| `contradicted` | 有更强证据反驳当前表述 |
| `superseded` | 被新 Claim 取代 |
| `stale` | baseline 变化或锚点失效，必须重验 |

### Ledger 是唯一主索引

Ledger 每个 Claim 只有一个主行，包含：ID、精确 statement、type、scope、status、G 等级/向量、source-map、experiment/OBS、consumer、conflict/supersedes、last verified baseline。

文章可以改写 Claim，但必须引用 ID；总表只能消费 `supported` 或符合它表述边界的 `bounded` Claim。

## 证据包与双向链接

一个 Claim 的证据包包含：

1. 主证据锚点：规范章节，或仓库 commit + path + symbol/field + 当前行号。
2. 直读事实：锚点明确表达什么。
3. 解释链：哪些结论由多个锚点推导，而非某一行直接说明。
4. 实验观察：`OBS-<EXP>-NNN`、raw artifact 和环境。
5. 反证与冲突：哪个可能解释已被排除，哪个仍未排除。
6. Consumer：使用该 Claim 的 Q&A、总表、图和其他 Claim。

要求两向可查：从 Q&A 能回到 Claim，从 Claim 能找到所有 consumer。

## 源码深钻协议

1. 从适合 Claim Type 的公开契约/规范开始，再进入实现，不在仓库中无目标漫游。
2. 用 `rg` 定位入口、类型、函数指针/vtable/trait impl、状态字段和注释。
3. 证明 build/dispatch 选择：宏、代码生成、target、feature、动态分发、加载库和后端如何选中这个实现。
4. 按研究原型追踪主链，并单独检查 fast/slow、error/fallback、cancel/cleanup、failure/recovery 分支。
5. 分开“直读事实”与“由已闭合锚点得出的推论”；推论不是一行注释的伪引用。
6. 行号只是当前 checkout 的定位助手；symbol/field、commit 和 dispatch 关系是更稳定的锚点。
7. 记录 dirty state、submodule/dependency lock、build flag 与实际加载 artifact；“有一份对应源码”不等于“运行了这份源码”。

## 否定、推论和冲突

### 否定 Claim

对“不保存、不调度、不阻塞、不共享”等结论，至少需要一类正证据：

- 契约明确排除；
- 对象结构与结果记录中缺位，且可能的替代路径已检查；
- 路径分离证明两个动作不是同一事件；
- 反例能稳定否定全称命题。

“没搜到”不是否定证据。

### 冲突证据

在 `claims/conflicts.md` 保留：

- 冲突 ID 和影响 Claim；
- 各方原话的合规摘要与证据类型；
- 版本、规范/实现、配置和术语层级差异；
- 当前处理：resolved、scoped、unresolved；
- 为什么选择、并列或拒绝某个说法。

不得静默删除不符合预期的官方证据。

## G0 升级清单

只有全部回答“是”才升 G0：

1. Claim statement 是单一、可反驳且 scope 精确的吗？
2. 对应 Claim Type 的主证据已端到端闭合吗？
3. 运行二进制/库/内核与研究源码的 provenance 已闭合吗？
4. 架构、配置、feature、build flag 与 Claim 一致吗？
5. 实验确实区分了相关竞争模型，而不是只观察到相容现象吗？
6. raw output、命令、程序、环境与 OBS ID 都可定位吗？
7. 已记录 `Cannot Prove`，且没有一项直接破坏当前 statement 吗？
8. 冲突证据已解决或限定，没有 unresolved 高风险冲突吗？

无意义或不可能的实验不得为追求 G0 而强行执行。此时将 G1 写成正常的最高可达等级。

## 版本失效与重验

### 失效触发器

- baseline commit/tag/package 变化；
- 关键 symbol/field 删除、改名或 dispatch 变化；
- 架构、配置、feature 或 compiler/runtime 变化；
- 实验无法再现、输出语义变化；
- 更强主证据与现有 Claim 冲突。

### Refresh 流程

1. 固定 old/new baseline，保存版本差异范围。
2. 对比被 Claim Ledger 引用的 symbol、field、路径、配置和依赖锁。
3. 将受影响 Claim 标 `stale`，从 consumer 反向列出影响 Q&A/图/总表。
4. 只重追受影响主链；无影响的 Claim 保留旧验证记录。
5. 需要新语义时新建 Claim 并 supersede 旧 ID；只是行号漂移时更新锚点。
6. 重跑受影响实验，更新证据向量、封版矩阵和 `last_verified`。

文章不得在 Claim 仍为 stale 时保持 final 口径。
