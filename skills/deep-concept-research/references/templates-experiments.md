# 实验产物模板

## 目录

- [Experiment Record](#experiment-record)
- [专项实验附加字段](#专项实验附加字段)

## Experiment Record

````md
---
title: <experiment name>
type: experiment
status: draft
---

# <Experiment Name>

## Identity

- Experiment ID: `EXP-ABC-MECH-001`
- Kind: `MECH`
- Related claims: `CLM-ABC-001`
- Safety: `SAFE-1`

> [!question] Target Question
> <要区分的竞争模型>

## Safety And Isolation

| 项 | 内容 |
| --- | --- |
| risk level | |
| affected scope | |
| isolation | |
| cleanup | |
| rollback | |
| approval | |

## Environment And Provenance

| 项 | 值 |
| --- | --- |
| OS/kernel | |
| architecture/hardware | |
| compiler/runtime/dependencies | |
| source commit/dirty state | |
| build flags/features/config | |
| loaded artifact provenance | |
| permissions/sysctls | |
| source baseline difference | |

## Hypotheses Before Running

| 模型 | 预测 | 反证条件 | 停止条件 |
| --- | --- | --- | --- |

## Source Or Program

<路径、hash 和程序结构；大段源码单独存文件>

## Commands

```sh
<环境采集、编译、运行、观测、分析和 cleanup 命令>
```

## Raw Output

| Run | Raw path | SHA-256 | Result | Notes |
| --- | --- | --- | --- | --- |

## Observations

### OBS-ABC-MECH-001: <纯观察句>

- Raw anchor:
- Variance:
- Does not interpret:

## Conclusions

| Claim | Observation | Result | Evidence update | Reason |
| --- | --- | --- | --- | --- |

## Failed Or Conflicting Runs

## Cannot Prove

- <内部状态、版本、架构、性能、安全或可移植性外推>

## Source Closure

| Observation | Source-map/anchor | 闭合结果 | 剩余缺口 |
| --- | --- | --- | --- |

## Cleanup Verification

| 状态 | Before | After | Restored |
| --- | --- | --- | --- |

## Reproduction Record

| Reviewer/environment | Runs | Reproduced OBS | Differences | RR update |
| --- | --- | --- | --- | --- |
````

## 专项实验附加字段

### BENCH

```md
## Benchmark Design

| 项 | 内容 |
| --- | --- |
| primary metric/unit | |
| practical threshold | |
| baseline/treatment | |
| workload shape | |
| controlled variables | |
| warmup | |
| repetitions/sample size | |
| run ordering | |
| affinity/NUMA/frequency/thermal | |

## Statistical Analysis

| Metric | Baseline | Treatment | Effect size | Variance/CI | Practical conclusion |
| --- | --- | --- | --- | --- | --- |

## Mechanism Intervention

<改变哪个机制参数，哪个辅助指标应同时变化？>
```

### CONC

```md
## Concurrency Model

| participant | shared state | operation | ordering/happens-before | expected outcomes |
| --- | --- | --- | --- | --- |

## Stress And State-space Strategy

- barriers/seeds:
- iterations:
- scheduler perturbation:
- sanitizer/model checker:
- uncovered state space:

## Outcome Counts

| Outcome | Count | Allowed/forbidden | Evidence |
| --- | --- | --- | --- |
```

### FAULT

```md
## Fault Model

| 故障 | 注入点 | 时序 | 持续时间 | 预期 safety/liveness |
| --- | --- | --- | --- | --- |

## Persistence And Recovery

| 时刻 | 持久化状态 | 内存状态 | 恢复动作 | 不变量 |
| --- | --- | --- | --- | --- |
```

### CROSS

```md
## Comparison Matrix

| Environment | Version/commit | Arch/config | Toolchain/deps | Hardware | Known confounders |
| --- | --- | --- | --- | --- | --- |

## Normalized Observations

| Observation schema | Env A | Env B | Invariant/difference | Attribution confidence |
| --- | --- | --- | --- | --- |
```
