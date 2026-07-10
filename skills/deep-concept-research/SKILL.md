---
name: deep-concept-research
description: 构建和维护术语严格、主张可追溯、源码可核验、实验可复现、图表可审计、版本可重验的底层技术专题与跨领域研究计划。Use when 新建、深钻、审计或升级操作系统、运行时、编译器、网络、存储、数据库、分布式系统、硬件、AI agent 或开发者工具等专题，或要求概念辨析、多仓库源码追踪、机制/性能/并发/故障实验、跨层对比、深度图文表、证据封版与版本重验时。
---

# Deep Concept Research

## 产出合同

交付可审计的专题或研究计划：术语有坐标，机制落到对象和转换，每条强主张有 Claim ID 与证据包，实验能复现且说明不能证明什么，图表绑定 Claim 并通过事实审图，版本变化后能定向重验。

## 选择运行模式

| 模式 | 用途 | 默认停止点 |
| --- | --- | --- |
| `program` | 规划多领域/多项目/多仓库长期研究 | topic/component/baseline/concept/visual registry 与共享实验室建立 |
| `scaffold` | 新专题骨架 | manifest、CONTEXT、大纲、Claim Ledger 和三类索引 |
| `tracer` | 验证方法是否可行 | 一条 source-map、一个最小实验、一篇 Q&A 闭合 |
| `full` | 完成整个专题 | 文章树、证据依赖、评审和封版全部达标 |
| `audit` | 只诊断现有专题 | 输出风险和修正队列，未授权时不改文件 |
| `refresh` | 上游版本/架构变更 | 受影响 Claim 全部重验或标为 stale/bounded |

从用户请求推断模式；跨多个产品/领域的长期布局选 `program`；“完成/做完专题”选 `full`，不在 tracer 后自行停工。详细完成定义见 [references/governance.md](references/governance.md)。

## 执行工作流

1. **读约束**：读当前及父目录的 `AGENTS.md`、`CONTEXT.md`、ADR、索引；检查工作树，不覆盖用户改动。
2. **选模式与原型**：跨领域/多组件时先读 [references/programs-and-domains.md](references/programs-and-domains.md)；单专题从状态机、转换流水线、查找/翻译、分配/生命周期、协议/恢复、性能/饱和中选主/副原型。先读 [references/routing.md](references/routing.md)。
3. **固定边界**：写总问题、读者、范围/非目标和 `research-manifest.yaml`；分别记录主事实源与实验二进制的版本、commit、架构、配置和 provenance。
4. **建坐标与账本**：定义混淆词的“是 / 不是 / 所属层 / 实现名”；为每条强主张分配 `CLM-<TOPIC>-NNN`，建 Claim Ledger。先读 [references/evidence.md](references/evidence.md)。
5. **走通追踪弹**：按所选原型追一条中心链；先写 source-map 和竞争模型，再做能区分它们的最小实验，为观察分配 `OBS-<EXP>-NNN`。
6. **闭合证据**：将观察、主证据锚点和 Claim 双向链接；保留冲突证据、否定结论和版本/架构缺口，不得用模糊副词掩盖。
7. **写阅读层与图谱**：按词汇底座 → 分层/对象地图 → 主机制 → 边界对比 → 实现/场景 → 总表组织；总表不引入新 Claim。按 [references/visuals.md](references/visuals.md) 创建 FIG ID、visual spec、机制子图、表格与实验数据图。
8. **审计与重验**：做事实、反驳、复现、读者四类评审；运行 `scripts/audit-topic.sh`，修复错误，处理严格警告，更新封版矩阵。

## 硬性门禁

- 原始笔记、AI 对话和二手材料只生成问题/覆盖点，不关闭最终事实。
- 区分 API/规范契约、实现机制、实验观察、性能、历史与可移植性 Claim；不用一类证据代替另一类。
- 每个跨层结论同时命名高层实体与 carrier；每个关键对象说明位置、所有/共享、生命周期、状态和不变量。
- 实验先写假设与反证，后运行；保留原始输出；必须有 `Cannot Prove`；不从外部现象直接猜内部字段。
- 实验前按 [references/experiments.md](references/experiments.md) 定安全等级；需要提权、修改宿主全局状态或有数据/连接风险时必须先取得授权。
- G3、冲突、stale 和未闭合 Claim 不进入确定性总结；“未命中代码/未观察到/无权限”不能证明机制不存在。
- 图只组织关系，不是证据；精确路径、字段、Claim ID 和边界保留在文本。
- accepted 图必须有 FIG ID、Claim/证据绑定、visual spec、caption/alt text、正文 consumer 和事实审图；stale/rejected 图不得被正文引用。

## 资源路由

- 创建 manifest、CONTEXT、大纲、Claim Ledger 或 source-map 前读 [references/templates-core.md](references/templates-core.md)。
- 创建实验记录前读 [references/templates-experiments.md](references/templates-experiments.md)；创建 Q&A、review、refresh 或封版矩阵前读 [references/templates-writing.md](references/templates-writing.md)。
- 规划 Linux、数据库、语言/编译器、分布式系统或 agent 工具等多领域研究时读 [references/programs-and-domains.md](references/programs-and-domains.md)。
- 做机制、benchmark、并发、故障注入或跨版本实验前读 [references/experiments.md](references/experiments.md)。
- 创建 atlas、机制图、时序/状态图、精确表格或实验数据图前读 [references/visuals.md](references/visuals.md)。
- 设计文章树、评审、协作、封版或 refresh 时读 [references/governance.md](references/governance.md)。
- 遇到新类型专题或路由不确定时读 [references/examples.md](references/examples.md)。

## 确定性审计

从本 `SKILL.md` 所在目录执行：

```sh
bash scripts/audit-topic.sh --mode <program|scaffold|tracer|full|audit|refresh> [--strict] <topic-or-program-dir>
```

脚本只读。它不代替事实审计；自动检查通过后仍要核验最高风险 Claim。
