# 实验与安全协议

## 目录

- [通用实验合同](#通用实验合同)
- [安全等级](#安全等级)
- [可复现性与原始产物](#可复现性与原始产物)
- [工具梯子](#工具梯子)
- [MECH 机制实验](#mech-机制实验)
- [BENCH 性能实验](#bench-性能实验)
- [CONC 并发与竞态实验](#conc-并发与竞态实验)
- [FAULT 故障注入与恢复实验](#fault-故障注入与恢复实验)
- [CROSS 跨版本与跨架构对照](#cross-跨版本与跨架构对照)
- [观察、结论与 Cannot Prove](#观察结论与-cannot-prove)

## 通用实验合同

每个实验使用稳定 ID：`EXP-<TOPIC>-<KIND>-NNN`，其中 KIND 取 `MECH|BENCH|CONC|FAULT|CROSS`。每条直接观察使用 `OBS-<EXP-SHORT>-NNN`。

必须按以下顺序执行：

1. 写 Target Question 和关联 Claim ID。
2. 写至少两个竞争模型，或一个模型和能否定它的反例。
3. 在运行前写每个模型的预测、反证条件和停止条件。
4. 定安全等级，写隔离、清理和回滚；需新授权时先停下。
5. 记录环境、provenance、程序/配置、命令和原始输出路径。
6. 执行低侵入观测；只有无法区分模型时才升级工具。
7. 先写 OBS，只记可直接读出的现象；再写 interpretation 与 Claim 变更。
8. 写 Cannot Prove、异常、方差、失败尝试和 source closure。
9. 执行 cleanup 并核验环境恢复；未恢复状态立即报告。

实验记录不得在运行后按结果重写 hypotheses。预测错误是有价值的研究产物。

## 安全等级

| 等级 | 范围 | 例子 | 执行规则 |
| --- | --- | --- | --- |
| `SAFE-0` | 只读 | 读源码、`/proc`、非特权资讯 | 可直接执行，仍记录隐私/输出边界 |
| `SAFE-1` | 进程内、临时文件 | 普通编译运行、pipe/socketpair、临时目录 | 可直接执行；记录 cleanup |
| `SAFE-2` | 隔离环境内可变 | namespace、容器、专用 VM、测试 cgroup | 确认隔离边界；写清理/快照；不越过已授权范围 |
| `SAFE-3` | 宿主全局状态 | sysctl、mount、防火墙、网络、内核模块、系统服务 | 执行前获得明确授权；记录 before/after、回滚和连接风险 |
| `SAFE-4` | 破坏性/不可逆 | 块设备写入、文件系统破坏、可能丢数据/失联的故障注入 | 不在生产/用户数据上执行；需専用可丢弃环境和明确授权 |

等级取可能后果最高者，不是“命令看起来简单”的等级。例如调整网络规则可能导致失联，即使只有一条命令也是 SAFE-3/4。

优先降级风险：用专用 VM 代替宿主、用 image/file-backed loop device 代替真实盘、用 network namespace 代替主网络、用模拟时钟/可控 fault point 代替随机杀进程。

## 可复现性与原始产物

### 环境 provenance

至少记录：

- OS/kernel、architecture、CPU/model 中与 Claim 相关的部分；
- compiler/runtime/package/dependency lock 版本；
- source commit/tag、dirty state、build flags、feature/config；
- 实际加载的 binary/shared library/kernel/image provenance；
- 权限、sysctl、tracefs/perf 限制、环境变量；
- 重要硬件/虚拟化/容器边界。

不要无差别倾倒环境中可能含秘密的全部变量。只记与实验相关且已脱敏的项。

### Raw artifact

- 原始输出放 `experiments/raw/<experiment-id>/`，摘要与 raw 分开。
- 不在原文件上清洗；清洗结果另存并记录命令。
- 记录 SHA-256、生成命令和运行序号；输出巨大时可保留完整压缩文件与未编辑摘要。
- 保留失败、超时、无权限和与假设冲突的运行，不只保留“好看”的一次。
- 原始数据可能含用户数据、地址、进程参数或凭证时，先缩小采集范围并脱敏。

## 工具梯子

1. 可控输入、程序内日志、断言和反例。
2. 普通系统观测：`/proc`、`strace`、稳定计数器、状态文件、时间戳。
3. 语言/运行时/数据库自带 trace、explain、diagnostic 和 instrumentation。
4. `perf`、ftrace、eBPF/bpftrace、调试器、系统调用/内核探针。
5. 硬件计数器、外部分析仪、专用架构、模拟器或故障注入环境。

从最低侵入层开始。新工具只在它能区分当前竞争模型时引入；“能用更高级工具”不是使用它的理由。

## MECH 机制实验

用于观察状态、路径、分支、用户可见语义。

必须增加：

- 一个可控对象和可重复的输入序列；
- 正常、边界、错误、超时/取消中至少两类路径；
- 对“发生”和“没发生”的对照；
- 从现象到内部机制的 source-map 对齐表。

不要从 syscall/trace 名称直接推导内部结构体字段值。

## BENCH 性能实验

用于 performance Claim。必须额外记录：

- 主指标和单位，辅助指标，实质意义阈值；
- 基线、处理组、唯一主变量与其他控制变量；
- workload 形状：大小、并发、读写比、数据分布、命中率、持续时间；
- warmup 规则、测量轮数、样本数、运行顺序随机化/交错方法；
- CPU affinity、NUMA、频率/turbo、温度、后台负载、容器配额和硬件状态；
- 中位数、分位数、方差/置信区间和 effect size，不只报平均值；
- 原始样本、分析命令和异常值处理规则。

因果解释至少需要一个机制干预或可预测的辅助指标变化。只看到 A 比 B 快，不足以证明预设机制。

## CONC 并发与竞态实验

用于竞争、原子性、内存顺序、唤醒丢失、调度敏感问题。

必须额外记录：

- 并发参与者、共享状态和 happens-before/协议前提；
- 可控 barrier、seed、压力方法和轮数；
- 每种 outcome 的计数，不只记录首次失败；
- sanitizer/model checker/loom 等工具的选择范围和未覆盖状态空间；
- 编译优化、CPU 架构、内存模型和运行时调度差异。

未观察到竞态不证明竞态不存在。正面安全 Claim 需要契约/实现证明，或能穷尽相关状态空间的形式/模型证据。

## FAULT 故障注入与恢复实验

用于超时、丢包、分区、进程/节点崩溃、持久化边界和恢复。

必须额外记录：

- threat/fault model：什么可失败，什么保证不失败；
- 注入点、注入时序、持续时间和触发证据；
- safety invariant、liveness 超时、数据丢失/重复检查；
- 持久化数据、日志、checkpoint 和重启顺序；
- 恢复完成的判定标准，而不是“进程又起来了”；
- 完全隔离和回滚方案。

FAULT 通常是 SAFE-2 或更高。不对用户唯一数据、实际工作树、当前连接或生产服务做故障注入。

## CROSS 跨版本与跨架构对照

用于 portability 和 refresh。

必须额外记录：

- 严格的对照矩阵：version、commit、arch、config、toolchain、dependency、hardware；
- 哪些变量是研究对象，哪些是无法消除的 confounder；
- 每个环境的同一个 OBS schema，不为某平台改变结果定义；
- 实现路径差异和对外契约差异分开；
- 结果是 invariant、implementation difference、version regression 还是环境差异。

两个环境行为相同不证明内部路径相同；行为不同也不能在未控制 confounder 时归因于版本。

## 观察、结论与 Cannot Prove

### Observation

Observation 不使用机制动词，除非该机制本身被直接 instrumentation 记录。

好：

> `OBS-PIPE-004`：部分读取后，`poll(timeout=0)` 返回 `POLLIN`，同一时刻 `epoll_wait(timeout=100)` 返回 0。

不好：

> ET 内核没有把 fd 重新放回 ready list。

后者是 source-map 闭合后的 interpretation，不是外部观察。

### Cannot Prove

至少检查：

- 内部对象、字段、队列、寄存器或调用链是否被直接观测；
- 实验版本是否等于研究 baseline；
- 是否能外推到其他架构、配置、输入、负载或时间；
- 无权限、未命中、未观察到是否被错当成否定证据；
- 机制实验是否被错用来做性能、安全或可移植性结论；
- 一次成功恢复是否被外推为所有失败点都安全。

Cannot Prove 中若有一项直接否定 Claim statement，降级或改写 Claim，不能只把它留在限制段。
