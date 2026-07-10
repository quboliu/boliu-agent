# 深度图表与视觉证据协议

## 目录

- [视觉产出合同](#视觉产出合同)
- [图、表与数据图的选择](#图表与数据图的选择)
- [图谱类型](#图谱类型)
- [FIG ID 与 Visual Registry](#fig-id-与-visual-registry)
- [Visual Specification](#visual-specification)
- [表格协议](#表格协议)
- [实验与性能数据图](#实验与性能数据图)
- [生成和编辑方式](#生成和编辑方式)
- [双层图谱与细节密度](#双层图谱与细节密度)
- [视觉生产流程](#视觉生产流程)
- [事实审图和排版审图](#事实审图和排版审图)
- [封版标准](#封版标准)

## 视觉产出合同

图文表并茂不是“每篇加几张图”，而是为不同认知任务选择最小有效视觉工件：

- 文字负责定义、因果、边界、反例和证据解释；
- 表格负责精确映射、多维对比和状态/证据盘点；
- 机制图负责层次、拓扑、对象、顺序、所有权和状态转换；
- 数据图负责展示实验样本、分布、方差、效应量与饱和转折。

图不是证据源，但必须绑定已审核 Claim 和证据工件。任何无 Claim/证据来源的精确机制标注都是待审内容。

## 图、表与数据图的选择

| 读者任务 | 优先工件 | 辅助工件 |
| --- | --- | --- |
| 精确比较 3 个以上对象/实现 | 表格 | 差异概览图 |
| 理解系统分层与组件边界 | 层次/拓扑图 | 组件责任表 |
| 理解调用、数据或控制如何流动 | 路径/数据流图 | 逐步文字 |
| 理解多参与者时序和协议 | 时序图 | 消息/状态表 |
| 理解对象嵌套、所有权和生命周期 | 对象/内存布局图 | 对象分类表 |
| 理解有限状态和合法转换 | 状态机 | 转换条件表 |
| 理解实验如何区分模型 | 实验拓扑/时线 | OBS 表 |
| 判断性能差异、方差和饱和 | 数据图 | 统计摘要表 |

两个对象的单一维度差异通常用一句话或小表，不需要大图。图形必须比线性文字更容易回答一个明确问题。

## 图谱类型

| 类型 | 核心问题 | 必须表达 | 常见风险 |
| --- | --- | --- | --- |
| Landscape | 专题在整个系统的哪里 | 层、边界、主/副链和非目标 | 过度宏观，没有可追溯对象 |
| Component topology | 多仓库/多进程如何组成系统 | 组件责任、协议、数据/控制面 | 把产品名当一个进程/仓库 |
| Layer map | 同名概念在不同层是什么 | 每层 actor/entity/carrier/contract | 跨层箭头语义模糊 |
| Object/ownership | 对象在哪，谁拥有和共享 | 位置、嵌套/指向、生命周期 | 把指针、内嵌和拷贝画成同一箭头 |
| Call/control path | 哪条代码路径被选中 | dispatch、快/慢、error/cleanup | 把函数调用当数据流 |
| Data path | 数据从哪来到哪 | 表示、复制/引用、缓存、持久化 | 把通知/控制箭头当数据移动 |
| State machine | 什么事件使状态转换 | 状态、触发、guard、非法转换 | 把队列位置或口语当源码状态 |
| Sequence/protocol | 参与者如何交互 | 时间、消息、本地状态、重试/故障 | 只画正常路径，隐藏部分失败 |
| Storage/layout | 表示如何落到内存/页/文件/块 | 偏移、所属空间、虚拟/物理、编码 | 伪造精确比例或地址 |
| Transform pipeline | 表示如何逐阶段转换 | input/output IR、pass、不变量、fallback | 把 compiler/runtime 或 plan/execution 混成一层 |
| Experiment setup | 实验操作了什么，在哪观测 | 控制组/处理组、注入点、观测点、隔离 | 用图中预期结果伪装实验观察 |
| Decision map | 什么前提下选什么 | 条件、分支、成本、反例 | 将局部 benchmark 变成普遍选型 |

## FIG ID 与 Visual Registry

使用 `FIG-<TOPIC>-NNN`，只增不复用。图语义改变时新建 ID；同一语义的分辨率/尺寸导出共用 ID 并记 variant。

| FIG ID | Question | Type | Claims | Source/experiment | Generation policy/method | Spec | Accepted artifact | Variants | Consumers | Status | Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Status 取：`planned|draft|fact-reviewed|accepted|rejected|stale|superseded`。

- `rejected` 保留拒绝原因和产物路径，不被正文引用。
- 任一绑定 Claim stale 时，图至少标 `stale`，直到事实审图重做。
- 图只有在正文中被引用并有 caption/alt text 时才可 `accepted`。

## Visual Specification

每张深度机制图先写 spec：

```md
# FIG-ABC-001 Visual Specification

## Question
<读者看完应能回答的单一问题>

## Evidence Binding
- Claims:
- Source maps:
- Experiments/OBS:
- Baseline/scope:

## Audience And Reading Order
- Reader:
- Prerequisites:
- Entry point:
- Reading path:

## Canvas And Composition
- Type:
- Layers/panels:
- Main visual hierarchy:
- Detail inset/subgraph:

## Generation Policy And Provenance
- Project/user policy:
- Chosen method:
- Image Gen prompt/candidate:
- Deterministic exception reason:
- Overlay/post-processing:
- Tool/mode/date:

## Objects
| Visual object | Source object/concept | Category | Label | Must show | Must not imply |
| --- | --- | --- | --- | --- | --- |

## Arrows And Transitions
| From | To | Meaning | Style | Condition | Evidence |
| --- | --- | --- | --- | --- | --- |

## States, Time And Ownership
<状态、时间、所有/共享和生命周期如何视觉编码>

## Text Budget
- Title:
- Required labels:
- Legend:
- Text kept in caption instead:

## Caption And Alt Text
- Caption:
- Alt text:
- Evidence boundary:

## Rejection Criteria
- <事实错误、伪文字、箭头歧义、过载等>
```

图像生成 prompt 不是 visual spec 的替代品。prompt 可以派生自 spec，但事实约束、语义和拒绝标准必须独立可审计。

## 表格协议

表格是深度产出，不是排版装饰。优先使用：

| 表格类型 | 固定主轴 |
| --- | --- |
| Term boundary | 定义、维度、层、不是、实现名 |
| Object classification | 位置、所有/共享、生命周期、状态、作用、非作用 |
| State transition | from、event/guard、to、actor、side effect、invalid transition |
| Cross-implementation | 统一契约、对象、carrier、结果、边界、证据 |
| Claim/evidence | statement、type、scope、status/vector、source、experiment、consumer |
| Experiment | hypothesis、controlled input、OBS、variance、conclusion、Cannot Prove |
| Decision | 前提、选项、收益、成本、反例、不适用 |

表头必须表达比较维度，不使用“备注”承载所有难以归类内容。单元格有多个独立结论时拆列或拆表。

## 实验与性能数据图

每张数据图必须绑定 EXP/OBS 和 raw artifact，并标明：

- x/y 轴名、单位、尺度和零点处理；
- 样本数、轮数、汇总方法和误差/置信表示；
- baseline/treatment、workload 和关键环境；
- 异常值处理、截断坐标轴或对数轴；
- 数据图能支持的 observation 与不能支持的机制/因果结论。

不用只画平均值的柱状图隐藏分布；尾延迟问题优先展示分位数或分布；饱和问题同时画负载、吞吐、延迟和主资源利用率。

## 生成和编辑方式

先遵循用户和当前项目的图形资产规则；局部政策可以比本协议更严格。无特定约束时，按下列顺序路由：

1. **Image Gen first**：面向读者的 atlas、layer map、机制概览、流程/时序解释图、概念插画和非数据 infographic，默认先用 Image Gen 产生候选位图。在 spec 保留 prompt、候选路径、工具/模式和日期。
2. **精确机制图**：仍先评估 Image Gen；图内只放必要、稀疏、可审的标签，把字段、函数路径、条件矩阵和 Claim ID 放到 caption/表格/正文。如果必须保证每个箭头、对齐或文本的机械正确性，可对 Image Gen 视觉层叠加确定性标注，或改用确定性图形；必须记录例外原因和后处理 provenance。
3. **数据图与精确表格**：从 raw artifact 确定性生成，不让 Image Gen 发明数字、坐标、样本或误差线。Image Gen 可用于无数值的背景/解释层，但不得成为数据事实层。
4. **Mermaid 只作草图**：可用于研究中间的快速关系校验，但默认不得成为 accepted 正式图。只有用户/项目明确允许时才能封版。
5. **导出与源文件**：面向读者的正式资产优先 PNG/WebP。SVG 可作确定性标注的可编辑源，但不是默认视觉路线，也不得绕过项目的 Image Gen-only 规则。

任何路线都不允许伪代码、伪字段、伪地址、伪数据或视觉上暗示未证明的对象关系。不把 prompt 中的“accurate”当成事实审核；每个候选结果都按 spec 逐对象、逐箭头、逐标签复核。

## 双层图谱与细节密度

高密度不等于把所有文字挤入一张图。对复杂系统默认采用：

1. **Atlas/overview**：一张稳定的全景图，只给层、组件、主链和子图入口。
2. **Mechanism subgraphs**：每张只关闭一个问题，展开对象、字段类别、转换、时序或故障。
3. **Quick-reference tables**：把精确名称、条件、差异、Claim 和证据放表格，不堵塞图面。

全景图与子图使用同一对象类别颜色、形状和箭头语义。子图标明它在 atlas 的位置；atlas 不复制子图全部细节。

## 视觉生产流程

1. **Visual plan**：在大纲中为每张候选图写问题、类型、绑定 Claim、consumer 和优先级。
2. **Spec**：只有主 Claim 至少 G1/G2 且边界清楚时写精确 visual spec；G3 图只能标为探索草图。
3. **Draft**：先按项目政策与 Image Gen-first 路由生成或编辑图，保留源文件/prompt、工具、模式、日期、variant 和例外原因。
4. **Fact review**：逐对象、逐箭头、逐状态、逐标签与 Claim/source-map 核验。
5. **Editorial review**：检查视觉层次、阅读顺序、文字密度、对比度、尺寸、alt/caption 和与系列图的一致性。
6. **Integration**：正文引用，caption 说明图能/不能表达什么，更新 Visual Registry。
7. **Export audit**：检查最终尺寸、缩放可读性、文件名、格式、链接、孤儿/rejected 引用和派生 variant。

不先批量生成图再寻找正文安放位置。每张 accepted 图必须从一个真实读者问题和已审 Claim 开始。

## 事实审图和排版审图

### Fact Review

- 图中每个精确对象是否有对应 source/spec/OBS？
- 嵌套、指向、共享、复制和所有权是否用不同语义表达？
- 箭头是调用、数据、控制、通知、状态转换还是时间顺序？
- 图是否把可选路径画成必经，把局部实现画成标准契约？
- 图中状态/字段是源码名还是教学分类，是否明确区分？
- 架构、版本、配置和非目标是否在 caption 中可见？
- 是否遵循项目生成政策？Image Gen 候选、确定性叠加或例外路由的 provenance 是否完整？
- Image Gen 产物中的所有文字、数值、箭头和对象是否逐项核验？无法核验的细节是否删除或退回 caption/表格？

### Editorial Review

- 不看正文时，读者是否知道从哪开始、按什么顺序读？
- 主链、次链和边界是否有明显视觉层次？
- 精确文字是否太小，图例是否与内容争夺注意力？
- 颜色是否是唯一语义编码；灰阶/色觉差异下是否仍能区分？
- 中英文、代码名、大小写、箭头和标点是否统一？
- 是否应拆成 overview + subgraph，而不是继续往一张图加文字？

## 封版标准

一个 D5 专题的视觉产出至少满足：

- 有一张稳定 atlas/landscape 作为图谱入口，子图使用一致语言；
- 每个高复杂中心机制至少有表格、机制图或时序/状态图中最合适的一种；
- 实验图表绑定 raw/OBS，不隐藏方差、样本数或负载边界；
- 全部 accepted 图有 FIG ID、spec、Claim 绑定、caption、alt text、consumer 和 fact review；
- 全部 rejected/stale 图无正文引用，正式图无孤儿；
- 图可以帮读者处理新反例，而不是只复述文章标题。

视觉封版不弥补证据层缺口。如果图需要一条尚为 G3 的精确机制 Claim，先闭合 Claim，而不是把它画得更像真的。
