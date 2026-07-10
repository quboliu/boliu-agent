# 路由与产出示例

## 目录

- [从现有两个专题抽象](#从现有两个专题抽象)
- [Linux 虚拟内存与缺页](#linux-虚拟内存与缺页)
- [PostgreSQL 查询从 SQL 到执行](#postgresql-查询从-sql-到执行)
- [TiDB/TiKV/PD 多组件事务路径](#tidbtikvpd-多组件事务路径)
- [Go/Rust/TypeScript 语言与运行时](#gorusttypescript-语言与运行时)
- [Codex/OpenClaw/Hermes 类 agent 工具](#codexopenclawhermes-类-agent-工具)
- [大型研究计划的组织示例](#大型研究计划的组织示例)

以下都是路由和工件示例，不是对任何当前版本的事实声明。真正执行时必须锁定本地或官方 baseline 后重建 Claim、路径和实验。

## 从现有两个专题抽象

| 通用坐标 | 调度与上下文切换 | IO 与事件 | 抽象后的原型 |
| --- | --- | --- | --- |
| 总问题 | 谁调度谁，切换什么，现场在哪 | 谁等什么，交付 readiness 还是 completion | State/Event |
| 正交词轴 | entry / scheduler switch / execution state / resource view | sync/async / blocking/nonblocking / readiness/completion | 先拆正交维度 |
| 高层实体 | process、pthread、goroutine、task | request、Future、goroutine、callback | 命名 managed entity |
| Carrier | Linux task、runtime worker | Linux task、event-loop/runtime worker | 命名低层承载者 |
| 独立链 | 特权入口与 task switch | data path 与 notification path | 对交叉链分主/副原型 |
| 实验 | yield/block/preempt 对照 | 空/部分消费/新输入/rearm 对照 | 用反例区分竞争模型 |
| 负结论 | 进内核不等于切 task | 收到 event 不等于 I/O 完成 | 每篇必写不变量/不自动意味着 |

泛化时保留左侧坐标与最后一列方法，不把 T0–T8、LT/ET/ONESHOT 等专题内部分类强行套到其他领域。

## Linux 虚拟内存与缺页

### 路由

- 主原型：Lookup/Translation。
- 副原型：Allocation/Lifetime；State/Event 只解释 fault 入口/返回。
- 目标深度：先 D3，再决定是否扩到 THP、swap、NUMA 等 D4 分支。

### 总问题

> 一段虚拟地址从映射到首次可读写，经过哪些查找、权限、分配和页表转换；外部指标分别能证明什么？

### 追踪弹

```text
API/allocator contract
  -> address-space object + mapping metadata
  -> CPU translation attempt
  -> fault entry and classification
  -> backing allocation/lookup/COW branch
  -> translation structure update
  -> return and retry
```

实验用固定大小匿名映射，对照未触碰、首读、首写、fork 后写入与解映射；记录页大小、THP/overcommit 和当前内核差异。

`Cannot Prove`：RSS/fault count 不直接证明具体 PTE 位，本机内核不自动证明锁定 study tree，单次延迟不支持性能 Claim。

### 视觉计划

- Atlas：虚拟区间、翻译结构、物理承载和 fault 路径的分层图。
- Subgraph：匿名页首写的对象/路径图。
- Table：mapped/committed/resident，minor/major，RSS/PSS 边界表。
- Experiment figure：操作阶段与可观察计数时线。

## PostgreSQL 查询从 SQL 到执行

### 路由

- 主原型：Transform。
- 副原型：Lookup/Translation（catalog/index）和 Performance（plan 选择后的实际成本）。
- 先固定数据库版本、build、extension、server config、schema、statistics 和 dataset。

### Claim 拆分

不写一条“优化器选了更快计划”。拆为：

1. contract：用户可见 SQL/EXPLAIN 交付什么；
2. implementation：当前 baseline 经过哪些 parse/rewrite/plan/execution 对象和 pass；
3. observation：锁定 schema/statistics/config 时观察到什么 plan 与 runtime counters；
4. performance：指定 dataset/workload/cache state 下差异多大；
5. portability：哪些是 SQL 契约，哪些仅属于当前 PostgreSQL 实现。

### 实验组

- MECH：固定 SQL/schema，只改变一个 statistics/config/index 条件，观察 plan 表示与执行计数。
- BENCH：固定冷/热缓存、数据分布、并发和重复轮数，把 plan 差异与延迟/资源指标对齐。

### 视觉计划

- Transform pipeline：SQL representation 在各阶段如何变化。
- Object map：catalog/statistics/plan/executor 对象的位置与生命周期。
- Comparison table：estimated/actual，contract/implementation，plan/execution。
- Data chart：完整样本分布和资源辅助指标，不只画平均延迟。

## TiDB/TiKV/PD 多组件事务路径

### Program 前置

先建 component/baseline registry，不把多个仓库与进程用一个产品名代替。锁定可互操作的版本组合、协议/schema 和部署配置。

### 路由

- 主原型：Protocol/Recovery。
- 副原型：Lookup（路由/元数据）、Allocation（region/range/resource lifetime）、State（transaction/replica state）。

### 追踪弹

只选一个边界清晰的事务路径：

```text
client-visible contract
  -> SQL/gateway component request
  -> metadata/routing decision
  -> storage transaction request
  -> replica/log/commit boundary
  -> response and client-visible result
```

为每段分配 component-specific Claim，只在协议锚点与版本组合已闭合时写 cross-component Claim。

### 实验组

- MECH：用请求/transaction ID 关联多进程日志与状态。
- FAULT：在可丢弃实验集群中对明确故障点做网络/进程注入，检查 safety/liveness 与恢复。
- CROSS：升级单个组件或特性开关时，区分协议兼容、行为差异和 confounder。

### 视觉计划

- Atlas：data plane/control plane 和组件责任。
- Sequence：请求跨组件时序，单独画正常与故障子图。
- State machine：只画锁定 baseline 中有实现锚点的状态。
- Evidence table：每段路径归属哪个仓库、Claim、source-map 和 experiment。

## Go/Rust/TypeScript 语言与运行时

用同一套边界追问，但分开语言契约、compiler transform、standard library、runtime/executor 和 OS carrier。

| 问题 | Go 实例路由 | Rust 实例路由 | TypeScript 实例路由 |
| --- | --- | --- | --- |
| 编译时转换 | source -> IR/SSA -> target artifact | source -> HIR/MIR/LLVM/artifact | TS -> emitted JS/bundle/source map |
| 运行时对象 | runtime scheduler/GC/object | Future/executor/runtime/allocation | JS objects/event loop/runtime host |
| 必查选择 | build tags、GOOS/GOARCH、toolchain | features、cfg、target、trait impl | tsconfig、bundler、module mode、host runtime |
| 最大误用 | 安装工具链行为=本地 study tree | compiler lowering=executor/runtime | TS 源码=实际执行 JS 与 host contract |

选一个具体语言构造做 tracer，不一开始将整个 compiler/runtime 作为一条中心链。

## Codex/OpenClaw/Hermes 类 agent 工具

### 先解决名称和证据可用性

1. 确定精确项目/产品、官方仓库/文档和当前版本；同名项目有歧义时请用户确认。
2. 将 OPEN-LOCAL、OPEN-REMOTE、MIXED、CLOSED 组件分开。
3. 对专有服务只写官方 contract 和可重现 observation，不从网络现象猜内部 scheduler、queue 或 model routing。

### 可用的主原型

- State/Event：agent loop、task lifecycle、approval/tool call state。
- Protocol/Recovery：tool/MCP/API 请求、重试、取消、断线恢复。
- Transform：instruction/context assembly -> model/tool request -> output/artifact。
- Allocation/Lifetime：session、context、artifact、plugin/skill 加载与销毁。

### 实验组

- 使用可重放、无秘密、无生产副作用的 fixture task。
- 固定工具集、skill/plugin、权限、模型/API 版本与配置；保存脱敏事件/trace。
- 多次运行分开随机输出差异和稳定机制差异；不以一次成功/失败宣称系统保证。
- 调用外部服务、发送消息或修改远程资源的实验不因“只是研究”而自动获得授权。

### 视觉计划

- Agent loop 状态机：只画已有契约/源码/trace 的状态。
- Context assembly 转换图：区分指令、用户输入、skill/plugin 资源、tool result 与产物。
- Tool call 时序图：显示 approval/sandbox/remote side effect 边界。
- Evidence table：开源内部、官方 contract、黑盒 observation 和不可知内部分开。

## 大型研究计划的组织示例

对同时涉及 Linux、PostgreSQL、MySQL、Redis、Go、Rust、TypeScript、Neon、TiDB/TiKV/PD 和多种 agent 工具的研究，不按项目名创建十几个无边界“终极大全”。

可建立逻辑 program：

```text
Program: Deep Systems And Runtime Research
  Domain A: Hardware / Linux mechanisms
  Domain B: Language / compiler / runtime
  Domain C: Database kernel
  Domain D: Distributed data systems
  Domain E: Agent / developer tooling
  Shared labs: VM, datasets, workloads, tracing, visual language
  Shared registries: concepts, baselines, components, cross-topic claims, figures
```

再以可反骏问题开 topic，例如：

- “一次用户请求中，高层异步 task 与 Linux task 各在什么时候等待？”
- “查询优化器的估算对象与实际执行计数在哪一层交界？”
- “多组件事务的 commit、visibility 和 durability 分别由哪个组件/记录定义？”
- “agent 的 tool result 如何进入下一轮 context，哪些属于本地开源机制，哪些只有托管 contract？”

每个 topic 声明 D0–D5 目标、baseline 组合、主/副原型和视觉计划。这样可以同时达到广度与深度，且不会失去证据边界和维护能力。
