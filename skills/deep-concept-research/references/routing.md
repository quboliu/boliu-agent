# 研究路由与范围控制

## 目录

- [运行模式](#运行模式)
- [原型路由决策](#原型路由决策)
- [六种研究原型](#六种研究原型)
- [混合专题](#混合专题)
- [通用分解画布](#通用分解画布)
- [范围与停止规则](#范围与停止规则)

## 运行模式

### `scaffold`

用于建立可执行骨架，不伪装已经关闭机制。必须产出：

- `research-manifest.yaml`；
- `CONTEXT.md` 中的总问题、范围、事实源、实验边界和核心词汇；
- `大纲.md` 中的问题账本、原型选择、中心链和文章依赖；
- 空但结构正确的 Claim Ledger；
- source-map、experiment、Q&A 读者索引。

### `tracer`

用一个薄但端到端的闭合验证坐标系。必须至少包含：

- 一条从契约/入口到内部对象、关键分支和结果的 source-map；
- 两个竞争模型和能区分它们的实验；
- 至少一个 Claim ID 在 Ledger、source-map、experiment 和 Q&A 四处对齐；
- 一篇不依赖施工语的读者文章。

### `full`

完成全文章树、高风险评审和封版。不要把“已做 tracer”当作停止理由。

### `audit`

只检查用户指定范围。未同时要求修复时，只输出证据化问题、风险、影响和修正建议，不改文件。

### `refresh`

对比新旧 baseline，先做符号/配置/路径影响分析，再按 Claim consumer 定向重验，不默认全专题重写。

## 原型路由决策

| 如果总问题主要在问 | 主原型 | 常见副原型 |
| --- | --- | --- |
| 实体如何在状态间转换、等待或被唤醒 | State/Event | Allocation、Protocol |
| 一种表示怎样被逐步改写成另一种表示 | Transform | Lookup、Performance |
| 一个名称/地址/键如何被解析到目标 | Lookup/Translation | Allocation、Performance |
| 资源如何创建、归属、共享、回收 | Allocation/Lifetime | State、Protocol |
| 多个参与者如何达成一致并从故障中恢复 | Protocol/Recovery | State、Performance |
| 性能为什么改变，资源何时饱和或退化 | Performance/Saturation | 任一机制原型 |

主原型决定文章叙事和必答问题。副原型只补充中心链的必经部分；不为“看起来完整”同时展开六条路径。

## 六种研究原型

### State/Event：状态机与事件链

适用：调度、I/O 事件、锁、任务生命周期、连接状态。

必答：

- 实体、carrier、状态枚举/位和合法转换是什么？
- 谁触发转换，哪些是同步入口，哪些是异步事件？
- 等待关系、队列资格、通知、唤醒、重试和结果分别在哪？
- 竞争、假唤醒、取消和销毁如何处理？

中心链：`entry -> current state -> registration -> transition -> queue/notification -> retry/result -> cleanup`。

### Transform：转换流水线

适用：编译器 lowering/优化、序列化、编解码、查询优化、构建系统。

必答：

- 每个阶段的输入表示、输出表示和不变量是什么？
- 哪个 pass/规则被选中，顺序由什么配置、target 或 feature 决定？
- 语义保持条件是什么，什么信息会丢失、拆分或合并？
- 诊断、fallback、错误恢复和终止点在哪？

中心链：`contract -> input IR -> selection/config -> pass sequence -> output IR/artifact -> validation/diagnostic`。

### Lookup/Translation：查找与翻译

适用：地址翻译、路径查找、DNS/路由、符号解析、索引查询、缓存。

必答：

- 查找键、命名空间、目标和权限边界是什么？
- 快路径缓存在哪，命中、miss、失效和负缓存如何表示？
- 多级 walk 的顺序、fallback 和终止条件是什么？
- 并发更新、一致性、生命周期与可见性如何保证？

中心链：`key/context -> cache -> miss path -> multi-level walk -> permission/validation -> result -> invalidation`。

### Allocation/Lifetime：分配、所有权与生命周期

适用：内存/对象分配、fd/inode/socket、连接池、缓存页、GPU/设备资源。

必答：

- 谁请求、谁分配、谁拥有，谁能共享/引用？
- 逻辑资源、虚拟映射、物理承载和账本是否是不同对象？
- 引用计数、generation、RCU/epoch、GC 或手动释放的生命周期锚点是什么？
- 回收、reclaim、eviction、close 和销毁如何区分？

中心链：`request -> classification -> allocation/mapping -> ownership/share -> use -> reclaim/release -> final destruction`。

### Protocol/Recovery：协议、一致性与故障恢复

适用：TCP/共识/副本协议、事务、日志、文件系统恢复、分布式锁。

必答：

- 参与者、本地状态、持久化记录、消息和时序假设是什么？
- safety invariant 与 liveness 条件分别是什么？
- 正常、重试、重复、丢失、乱序、分区、崩溃与恢复路径是什么？
- “提交、可见、持久、应用”在各层分别意味什么？

中心链：`initial state -> message/log -> local transition -> quorum/order rule -> commit/visibility -> failure -> replay/recovery`。

### Performance/Saturation：性能、资源与饱和

适用：吞吐/延迟、CPU/IO/内存瓶颈、队列、cache locality、scalability。

必答：

- 响应变量、控制变量、负载形状、基线和预期机制是什么？
- 资源需求、服务时间、队列长度、等待时间和饱和点如何区分？
- warmup、频率、affinity、NUMA、缓存、后台噪声和多次运行如何控制？
- 差异是统计显著、实质显著，还是只是测量噪声？

中心链：`workload -> resource demand -> service/queue -> saturation -> observed metrics -> causal intervention -> re-measurement`。

Performance 必须以另一个机制原型解释“为什么”；只有 benchmark 数字没有机制闭合时，结论只是局部观察。

## 混合专题

对每条中心链指定一个主原型。如果需要副原型，用接口表说明它只交付什么：

| 主链 | 副链 | 交界对象 | 交付状态/结果 | 不自动意味着 |
| --- | --- | --- | --- | --- |

例如缺页专题以 Lookup/Translation 为主，Allocation/Lifetime 解释页的承载与 COW，State/Event 只解释 fault 入口和返回。这不意味着缺页必然发生 I/O 或 scheduler switch。

## 通用分解画布

不论原型，每个关键机制都要回答：

| 坐标 | 问题 |
| --- | --- |
| Contract | 对外承诺什么，什么时候结果才有效？ |
| Layer | 当前在硬件、内核、库、运行时、语言、协议或业务层？ |
| Actor/entity/carrier | 谁执行，谁被管理，谁承载它？ |
| Object/location | 哪个对象代表它，状态在哪？ |
| Ownership/lifetime | 谁拥有、共享、引用和最终销毁？ |
| State/transition | 当前状态由什么字段/记录表示，谁使它转换？ |
| Selection/config | 哪个 build、feature、target、vtable/trait impl 或后端被选中？ |
| Result | 真正结果由什么返回值、记录、持久化点或对象交付？ |
| Failure/retry | 错误、竞争、超时、取消、fallback 和恢复如何处理？ |
| Invariants | 什么没有变，哪个常见推论因此不成立？ |
| Boundary | 版本、架构、配置、provenance、权限和非目标是什么？ |

不适用的坐标标 N/A 并说明原因，不要用空表格伪装完整。

## 范围与停止规则

对每个新分支连续问：

1. 不关闭它，当前中心 Claim 会不会错？
2. 它是必经路径，还是可选实现/优化？
3. 它是当前读者必需前置，还是专家完整性？
4. 它是 P0 风险、当前主张的反证，还是一般 open question？

只有第 1 或第 4 为“是”时默认留在当前追踪弹。其他分支记入 backlog，指定影响 Claim、优先级和重开条件。

不以“没有任何 open question”作为完成标准。以“所有高风险问题已关闭，其余问题已明确限定并不改变当前结论”作为停止条件。
