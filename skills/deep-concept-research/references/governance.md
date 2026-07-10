# 写作、评审与维护协议

## 目录

- [五层产物](#五层产物)
- [文章树与阅读体验](#文章树与阅读体验)
- [单篇文章合同](#单篇文章合同)
- [类比与可视化](#类比与可视化)
- [四类评审](#四类评审)
- [可选协作协议](#可选协作协议)
- [状态生命周期](#状态生命周期)
- [各模式完成定义](#各模式完成定义)
- [旧专题迁移到 v2](#旧专题迁移到-v2)
- [自动审计与人工审计](#自动审计与人工审计)
- [版本维护](#版本维护)

## 五层产物

| 层 | 回答什么 | 主要工件 |
| --- | --- | --- |
| 约束层 | 研究谁、用什么词、事实和实验边界在哪 | manifest、`CONTEXT.md`、ADR、术语表 |
| 规划层 | 总问题怎么拆，依赖、覆盖和优先级是什么 | `大纲.md`、question/coverage ledger |
| 证据层 | 哪些证据支持哪些 Claim，哪些仍有缺口 | Claim Ledger、source-map、experiment/raw、conflicts |
| 阅读层 | 读者如何按依赖建立心智模型 | Q&A、读者索引、图、总表 |
| 治理层 | 什么可以封版，变更后怎么重验 | reviews、audit report、封版矩阵、refresh record |

这五层是逻辑分离，不是为了创建最多文件。小专题可合并较薄的约束/规划文件，但不能将 raw output 和读者正文混成一份文档。

## 文章树与阅读体验

默认依赖顺序：

1. **前置与词汇底座**：标明读者已知条件，拆混淆词和正交维度。
2. **系统/对象地图**：将对象放回层级、存放域、所有权和主/副链中。
3. **主机制文**：一篇只围绕一个主问题和一组紧密 Claim。
4. **边界专文**：直接对比最容易混淆的两个契约、对象、状态、帧或路径。
5. **实现映射**：用同一坐标比较架构、运行时、库、设备或数据库实现。
6. **故障/性能/选型**：在机制已闭合后说明收益前提、退化条件和操作取舍。
7. **总表与索引**：压缩已支持 Claim，不创造新事实。

### 前置知识图

大纲为每篇文章记录：

- 必须先懂的术语/文章；
- 本文新增的心智模型；
- 哪些后续文章依赖它；
- 是否产生新 Claim，还是只汇总已有 Claim。

阅读顺序按概念依赖，不按文件创建时间或源码目录顺序。

### 读者校验

对核心文章设置 3–5 个诊断问题或反例，用来验证心智模型，而不是记忆术语。例如：

- 如果高层实体等待，carrier 是否必然等待？
- 如果缓存命中，权限检查是否被绕过？
- 如果两个版本输出相同，内部机制是否必然相同？

读者无法用文中坐标解释新反例时，文章尚未真正建立心智模型。

## 单篇文章合同

建议主线：

1. 最短结论：3–6 句给判断标准和最重要边界。
2. 为什么容易混淆：指出是同名跨层、契约/实现混淆，还是多条链交叉。
3. 概念和分层坐标：先给名称边界，再进入源码。
4. 关键对象：位置、所有/共享、生命周期、状态、作用和不是什么。
5. 主原型链路：按 routing 中该原型的问题组织，不强行套“等待/唤醒”。
6. 错误、竞争、fallback、取消、故障或恢复中与主 Claim 相关的分支。
7. 什么变了，什么没变：至少一个负结论或反直觉不变量。
8. 常见错误模型和诊断问题。
9. Claim 证据索引：说明 source-map、experiment/OBS、G 等级/向量和限制。
10. 最终心智模型：只压缩本文已支持 Claim。

不要在每段机械重复 Claim ID。在首次作出强结论、证据索引和总表中引用即可。

## 类比与可视化

### 类比

类比使用固定格式：

| 映射 | 成立的共同结构 | 失效边界 | 不能用来推导 |
| --- | --- | --- | --- |

类比不作为证据。如果去掉类比后结论就失去支撑，说明证据层未完成。

### 图

只在三个以上对象、路径或状态的关系比文字难理解时画图。优先顺序：

1. 表格：精确映射/比较。
2. 时序或状态图：事件顺序和转换。
3. 层次/所有权图：位置、嵌套、共享与生命周期。
4. 系统剖面：多条链交叉。

每张图必须有图问题、对象类别编码、箭头图例、caption 中的范围/证据边界、alt text 和正文引用。箭头区分调用、指向、所有、转换、数据移动、入队和唤醒。

图中不承载唯一关键结论。正式图、被拒图和草图状态分开；rejected 图不得被正文引用。

## 四类评审

### 1. Fact Review

逐个高风险 Claim 检查：

- Claim Type 和主证据是否匹配；
- 锚点是否来自锁定 baseline，dispatch/build 是否成立；
- 直读事实与 interpretation 是否分开；
- scope 是否小于或等于证据能支持的范围；
- 否定 Claim 是否有正证据。

### 2. Rebuttal Review

不是重述本文，而是寻找：

- 另一条同样能解释 OBS 的机制；
- 一个破坏全称/因果结论的反例；
- 规范与实现、高层与 carrier、通知与结果等偷换；
- 冲突的官方证据或版本分支。

评审结果必须是：被反驳、需缩小 scope、需新实验、或反驳不成立及其证据。

### 3. Reproduction Review

安全允许时，只按 experiment record 重跑，不使用原执行者的口头补充。记录：

- 是否能从零找到程序、命令和 raw schema；
- 环境差异；
- 哪些 OBS 复现/未复现；
- 失败是记录不足、环境差异，还是 Claim 风险。

SAFE-3/4 不为追求 RR2 而重跑，除非用户明确授权且有隔离环境。

### 4. Reader Review

评审者不依赖 source-map 细节，只读 Q&A，回答：

- 能否用文中词汇说清高层实体、carrier、关键对象和结果；
- 能否解释反例和“什么没变”；
- 是否误把类比、图、本机现象或单一实现当作普遍保证；
- 前置知识是否缺失，阅读顺序是否有循环依赖。

## 可选协作协议

只有用户明确要求委派/并行 agent，或项目约束明确要求时，才启用多 agent。

推荐角色：

| 角色 | 交付物 | 禁止 |
| --- | --- | --- |
| Scope/terminology | 问题账本、术语矛盾和范围风险 | 未核验即修改最终 Claim |
| Source tracer | source-map 与主证据锚点 | 撰写本机实验结果 |
| Experimenter | experiment/raw/OBS 与安全记录 | 将观察升格为内部机制 |
| Rebuttal reviewer | 反例、冲突与不成立的理由 | 为追求“有问题”虚构证据 |
| Integrator | Claim Ledger、Q&A、等级和 consumer 一致性 | 盲目合并冲突结论 |

共享的事实平面只包含 manifest、CONTEXT、Claim Ledger 和已核验 source-map/experiment。不让多个 agent 同时编辑同一文件；最终证据升级由 integrator 逐 Claim 执行。

前向测试 skill 时，只给测试 agent 真实用户任务、skill 路径和必需原材料，不泄露预期答案或已知缺陷。

## 状态生命周期

| 状态 | 用途 | 升级/降级条件 |
| --- | --- | --- |
| `outline` | 只是计划、线索和候选入口 | 产生首个经核验证据工件后进 draft |
| `draft` | 正文/证据已成形，仍可有已标注缺口 | 核心 Claim 对齐且审计通过后进 garden |
| `garden` | 稳定可读，允许明确边界和后续深化 | 封版范围全达标后可进 final |
| `final` | 指定 baseline 下已封版，不表示永远正确 | baseline/Claim 受影响时立即降 stale |
| `stale` | 证据锚点、provenance 或结论可能失效 | refresh 后回到 draft/garden/final |
| `archived` | 被取代且只作历史记录 | 不再作当前事实入口 |

文件状态和 Claim 状态不同。一篇 garden 文章可以引用 bounded Claim；一条 stale Claim 会使依赖它的 final 文章至少降为 stale。

## 各模式完成定义

### Scaffold Done

- 总问题可证伪，读者、included/excluded 和交付物清楚。
- 主/副原型有选择理由。
- 主事实源与实验 baseline 分开。
- 问题账本、Claim Ledger 和三类索引存在。
- 没有把候选源码入口写成已支持 Claim。

### Tracer Done

- 至少一个 Claim 在 Ledger/source-map/experiment/Q&A 双向链接。
- 实验预测、raw、OBS、Cannot Prove 和 cleanup 完整。
- Q&A 可独立阅读，无施工口吻，有证据索引和诊断问题。
- 中心链的主要竞争模型已排除或保留为明确边界。
- `audit-topic.sh --mode tracer --strict` 通过。

### Full Done

- 所有 P0 风险和会改变中心结论的 Claim 已 supported/contradicted/bounded，无 unresolved 高风险冲突。
- 所有确定性段落和总表只消费 supported/适用边界内的 bounded Claim。
- 文章依赖无循环，术语和 Claim 在全专题一致。
- 高风险 Claim 完成 Fact 和 Rebuttal Review；可安全复现的关键实验完成 Reproduction Review。
- 正式图无孤儿，rejected 图无正文引用，链接/元数据/施工口吻审计通过。
- 未闭合低风险问题有 scope、影响 Claim、优先级和重开条件。
- `audit-topic.sh --mode full --strict` 通过，逐篇封版矩阵无“需修正”。

### Audit Done

- 问题有文件/行/工件证据，不是风格偏好。
- 每项说明风险、受影响 Claim/consumer、建议修复和验收方法。
- 按 P0/P1/P2 排序，区分事实错误、证据不足、维护风险和纯编辑问题。
- 未授权修复时工作树不被改动。

### Refresh Done

- old/new baseline 与差异范围已锁定。
- 受影响 Claim 和 consumer 已全部重验、bounded、superseded 或保持 stale。
- 只行号漂移的锚点与语义变化分开。
- 需要的 CROSS/其他实验已重跑，证据向量和文件状态已更新。

## 旧专题迁移到 v2

不按文件数量大面积改标题。用一条现有主机制做迁移 tracer：

1. 先运行 `audit-topic.sh --mode audit`，将“结构迁移”与“事实错误”分开；旧 schema 警告不证明文章技术错误。
2. 补 manifest、主/副原型、Claim/Conflict Ledger，但不立即改所有正文。
3. 从一份高价值 source-map 抽取 1–3 条强主张，分配 Claim ID、Type、Scope 和证据向量。
4. 将对应实验升级为 EXP/OBS：补 hypotheses-before-running 时不伪装它当初已存在；标明“迁移时重建的预测”或重跑新实验。
5. 只修该 Claim 的 Q&A consumer：补前置、证据索引、诊断问题和最终心智模型。
6. 将它使用的正式图分配 FIG ID，补 spec/事实审图；被否决图只登记，不重新编辑。
7. 运行 `--mode tracer --strict`。该纵向闭合通过后，再按 Claim 风险而非文件名顺序扩展迁移。

迁移不改写 raw output、旧评审结论或历史时间。旧工件不满足新协议时，新建 migration note 说明哪些字段是后补、哪些结论已重验。

## 自动审计与人工审计

`scripts/audit-topic.sh` 负责可确定检查：目录/必要文件、frontmatter、Claim ID 定义与 consumer、experiment 必要段落、相对链接、孤儿/rejected 图、施工口吻与若干 provenance 线索。

人工审计仍必须检查：

- 锚点是否真的支持 Claim；
- 解释是否越过主证据范围；
- 实验是否真正区分竞争模型；
- 因果、否定、性能、安全和可移植性 Claim 是否有匹配证据；
- 文章是否能让读者处理新反例。

自动审计通过不等于事实正确；人工审计通过也不取消 baseline 变化后的 refresh 责任。

## 版本维护

每次上游更新、rebase、工具链/依赖升级或运行环境变化时：

1. 更新 manifest 的 candidate baseline，不立即覆盖 last verified baseline。
2. 生成差异索引：被 Ledger 引用的 symbol、field、config、dependency 和产物 provenance。
3. 标记受影响 Claim 和 consumer 为 stale，优先重验 P0/高风险 Claim。
4. 将纯定位变化、实现重构但语义不变、契约/语义改变三类差异分开。
5. 更新 source-map、实验、Claim 向量、Q&A 和封版状态。

不保留靠记忆的“已经复核过”。每次验证都在 Claim 主行记录 baseline 和对应 review/refresh 工件。
