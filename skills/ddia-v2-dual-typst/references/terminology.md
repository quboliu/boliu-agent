# DDIA V2 bilingual terminology baseline

This is the shared terminology baseline for every chapter agent. Read it before
translating a chapter. Prefer these Chinese forms in prose, headings, table
cells, captions, notes, and the glossary. Keep the English term in parentheses
on first use only when it improves comprehension; do not repeatedly alternate
between synonyms.

## Core architecture and requirements

| English | Canonical Chinese | Usage note |
| --- | --- | --- |
| data system | 数据系统 | Do not casually replace with “数据库系统” when the scope includes non-database components. |
| data-intensive | 数据密集型 | |
| nonfunctional requirement | 非功能性需求 | |
| reliability | 可靠性 | |
| availability | 可用性 | |
| scalability | 可扩展性 | |
| maintainability | 可维护性 | |
| operability | 可运维性 | |
| latency | 延迟 | Use “响应时间” only when the source specifically means end-to-end response time. |
| throughput | 吞吐量 | |
| durability | 持久性 | As an adjective, “持久的”. |
| fault tolerance | 容错 | |
| partial failure | 部分失效 | |
| operational system | 运营系统 | Do not translate this as “操作系统”; the latter is the operating-system term. |
| analytical system | 分析系统 | |
| observability | 可观测性 | |
| system of record | 记录系统 | The authoritative source of data; pair with “派生数据系统”. |
| source of truth | 事实来源 | A synonym/explanation for “system of record”. |
| derived data system | 派生数据系统 | |
| self-hosting | 自托管 | |
| data residency | 数据驻留 | |

## Data models, storage, and query

| English | Canonical Chinese | Usage note |
| --- | --- | --- |
| data model | 数据模型 | |
| query language | 查询语言 | |
| relational model | 关系模型 | |
| document model | 文档模型 | |
| graph model | 图模型 | |
| storage and retrieval | 存储与检索 | |
| encoding | 编码 | |
| evolution | 演进 | Use “演化” only when discussing a biological or explicitly evolutionary metaphor. |
| schema | 模式 | Database schema is “数据库模式”, not “架构”. |
| index | 索引 | |
| secondary index | 二级索引 | |
| primary key | 主键 | |
| join | 连接 | SQL join is not translated as “联接” elsewhere in this project. |
| normalized / denormalized | 规范化 / 反规范化 | Keep the pair consistent. |
| materialized view | 物化视图 | |
| derived data | 派生数据 | |
| data warehouse | 数据仓库 | |
| OLTP | 联机事务处理 | Expand on first relevant use if needed. |
| OLAP | 联机分析处理 | |
| declarative | 声明式 | |
| stored procedure | 存储过程 | |
| full-text search | 全文搜索 | |
| cache | 缓存 | |
| impedance mismatch | 阻抗失配 | |
| object-relational mismatch | 对象—关系阻抗失配 | Keep the em dash in this compound term. |
| shredding | 拆分 | In nested/document-to-columnar encoding contexts. |
| one-to-few | 一对少数 | Prefer this over the clipped “一对少”. |
| hydrating IDs | 根据 ID 加载对象 | Translate for meaning in prose; retain “hydrating” on first use if needed. |

## Distribution and replication

| English | Canonical Chinese | Usage note |
| --- | --- | --- |
| replication | 复制 | “复制” is the mechanism; “副本” is the resulting copy. |
| replica | 副本 | |
| leader | 领导者 | Keep the leader/follower pair rather than switching to primary/secondary without context. |
| follower | 追随者 | |
| primary / secondary | 主节点 / 从节点 | Use only when the source explicitly uses primary/secondary terminology. |
| node | 节点 | |
| partition | 分区 | A logical/data distribution unit; do not automatically translate every partition as “分片”. |
| sharding | 分片 | |
| shard | 分片 | |
| rebalance | 重新平衡 | |
| shared-nothing | 无共享 | |
| quorum | 法定人数 | In a protocol context, retain “quorum” on first use if ambiguity is possible. |
| failover | 故障转移 | |
| split brain | 脑裂 | |
| fencing / fencing token | 隔离 / 隔离令牌 | Distributed-systems protection against stale or split-brain actors. Reserve “屏障” for CPU/memory fence or barrier instructions. |
| hot standby | 热备节点 | Keep distinct from “read replica / 读副本”. |
| asynchronous / synchronous | 异步 / 同步 | |
| bounded / unbounded | 有界 / 无界 | |
| timeout | 超时 | |
| Byzantine fault | 拜占庭故障 | |
| skew (load distribution) | 偏斜 | Use for uneven load or shard distribution, such as “负载偏斜”. |
| read skew / write skew / clock skew | 读偏差 / 写偏差 / 时钟偏差 | Use “偏差” for timing and transaction anomalies; do not generalize this to load skew. |

## Transactions, consistency, and consensus

| English | Canonical Chinese | Usage note |
| --- | --- | --- |
| transaction | 事务 | |
| atomicity | 原子性 | |
| isolation | 隔离性 | |
| serializability | 可串行化 | |
| serializable | 可串行化的 | |
| two-phase commit (2PC) | 两阶段提交（2PC） | |
| two-phase locking (2PL) | 两阶段锁定（2PL） | |
| lock | 锁 | |
| consistency | 一致性 | Do not translate as “一致度”. |
| consensus | 共识 | |
| linearizability | 线性一致性 | |
| linearizable | 线性一致的 | |
| eventual consistency | 最终一致性 | |
| read-after-write consistency | 写后读一致性 | Also called “读己之写一致性”; never reverse it to “读后写一致性”. |
| causal consistency | 因果一致性 | |
| causality | 因果关系 | |
| happens-before | 先发生关系 | Use “happens-before 关系” when preserving the formal term helps. |
| total order | 全序 | |
| deterministic | 确定性的 | |
| idempotent / idempotence | 幂等的 / 幂等性 | |
| atomic | 原子的 | Use “原子性” only when the noun is intended. |

## Batch and stream processing

| English | Canonical Chinese | Usage note |
| --- | --- | --- |
| batch processing | 批处理 | |
| batch process | 批处理过程 | |
| stream processing | 流处理 | |
| stream | 流 | |
| event | 事件 | |
| event time | 事件时间 | |
| processing time | 处理时间 | |
| watermark | 水印 | |
| window | 窗口 | |
| backpressure | 背压 | |
| flow control | 流量控制 | |
| producer / consumer | 生产者 / 消费者 | |
| message broker | 消息代理 | |
| at-least-once | 至少一次 | |
| at-most-once | 至多一次 | |
| exactly-once | 恰好一次 | |
| ETL | 抽取、转换、加载（ETL） | |
| change data capture | 变更数据捕获 | |
| change log / changelog | 变更日志 | Use for a log that records data or state changes; do not use “变化日志” or “更改日志”. |
| change stream | 变更流 | Use for database/stream-processing APIs and streams of change events. |
| change event | 变更事件 | Use in CDC and stream-processing contexts; ordinary events that merely happen to change state may be phrased naturally. |
| event sourcing | 事件溯源 | |
| backfill | 回填 | |
| durable execution | 持久化执行 | Use in workflow-engine contexts; avoid the stiff literal form “持久执行”. |

## Agent rules for terminology

1. Read this file before editing a chapter.
2. Search the entire assigned chapter for repeated occurrences of a core term;
   translate repeated occurrences consistently unless the source clearly uses
   a different technical sense.
3. Do not create a private synonym because a sentence sounds smoother. If a
   different rendering is genuinely required, report it as a terminology issue
   for the main agent; do not edit this file from a chapter agent.
4. The main agent is the only owner of changes to this baseline. After review,
   accepted new terms are added here and then propagated in a second consistency
   pass across all translated chapters.
