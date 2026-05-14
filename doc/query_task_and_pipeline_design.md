# Demand Atlas｜需见 Query Task 与 Pipeline 设计文档

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 Query Task 与 Pipeline 设计文档
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：任务系统设计 / Worker 设计 / 后端接口设计 / 技术评审
- 上游输入：
  - `doc/prd_reddit_needs_discovery.md`
  - `doc/technical_architecture_input.md`
  - `doc/domain_model_and_schema.md`

---

## 2. 文档目标

本文档用于定义：

1. 查询任务的生命周期
2. 查询任务的状态机
3. 查询请求如何命中缓存或转入异步执行
4. Pipeline 各阶段的输入、输出与失败处理
5. `partial_success`、`failed`、`success` 的判定标准
6. 任务系统的幂等、重试、超时、可观测要求

---

## 3. 设计原则

## 3.1 查询任务是系统执行主轴

系统不以“单次 HTTP 请求”作为完整执行单位，而以 `QueryTask` 作为真正执行单位。

这意味着：

- HTTP 请求只负责触发、查询状态、读取结果
- 重计算通过异步任务系统完成
- 结果通过 `ResultSnapshot` 持久化交付

## 3.2 快照优先于实时拼装

- 面向用户展示的列表与详情尽量来自快照
- 避免每次刷新页面都触发全量重算

## 3.3 部分成功优于整体失败

- 某些社区拉取失败时，允许继续生成有限结果
- 某些证据缺失时，允许结果降级展示

## 3.4 每个阶段都必须可追踪

每个 QueryTask 至少要能回答：

- 当前跑到哪一阶段
- 哪一阶段失败
- 哪一阶段耗时异常
- 当前结果是否可展示

## 3.5 幂等优先

- 同样的标准化查询，不应因为重复点击无限创建等价任务
- 任务执行具备可去重与可重放能力

---

## 4. Query Task 生命周期

## 4.1 用户视角生命周期

```text
发起查询
  -> 系统校验输入
  -> 命中缓存则直接返回结果
  -> 未命中缓存则创建任务
  -> 任务执行中
  -> 返回成功 / 部分成功 / 失败
  -> 结果可查看 / 导出 / 后续复用
```

## 4.2 系统视角生命周期

```text
receive_request
  -> normalize_query
  -> cache_lookup
  -> create_query_task
  -> enqueue_pipeline
  -> execute_pipeline_stages
  -> persist_result_snapshot
  -> finalize_task_status
```

## 4.3 生命周期核心对象

生命周期中涉及的核心对象：

- `QueryTask`
- `QueryTaskRunLog`
- `ResultSnapshot`
- `ClusterMetricSnapshot`
- `ResultSnapshotCluster`
- `ExportJob`（后续）

---

## 5. Query Task 状态机

## 5.1 主状态

V1 主状态定义为：

- `pending`
- `running`
- `partial_success`
- `success`
- `failed`

## 5.2 状态语义

### pending

- 任务已创建
- 还未真正进入执行

### running

- 至少一个 pipeline 阶段正在执行
- 可以存在阶段级成功与失败，但整体尚未结束

### partial_success

- 任务完成
- 但结果覆盖不完整，或部分阶段失败后降级返回

### success

- 任务完成
- 满足可用结果要求
- 已生成结果快照

### failed

- 任务无法生成可交付结果
- 或输入 / 数据 / 执行链路失败且无降级路径

## 5.3 状态流转

```text
pending -> running -> success
pending -> running -> partial_success
pending -> running -> failed
```

## 5.4 不允许的状态流转

V1 不允许：

- `success -> running`
- `failed -> running`
- `partial_success -> running`

若要重跑，应创建新 `QueryTask` 或显式 replay 子任务。

## 5.5 阶段状态与主状态关系

主状态由阶段执行结果综合决定，不应由单一阶段直接粗暴覆盖。

建议规则：

- 所有关键阶段成功，且满足最小结果要求 -> `success`
- 关键阶段部分失败，但仍产出满足最低交付门槛的结果 -> `partial_success`
- 关键阶段失败，且无法形成最低可交付结果 -> `failed`

---

## 6. 查询入口到任务创建流程

## 6.1 请求入口流程

建议流程：

1. 接收查询请求
2. 基础参数校验
3. 标准化查询输入
4. 计算 `normalized_query_key`
5. 查询缓存 / 快照
6. 命中则直接返回
7. 未命中则创建任务
8. 将任务投递到队列
9. 返回 `query_task_id`

## 6.2 输入校验

V1 至少校验：

- 时间范围是否合法
- 关键词数量是否超限
- Subreddit 数量是否超限
- 关键词是否过泛 / 过于歧义
- 一键发现是否提供有效模板
- 语言是否在支持列表内

### 输入校验结果类型

- `accept`
- `accept_with_warning`
- `reject`

## 6.3 查询标准化

标准化内容至少包括：

- query_type
- template_id / template_version_id
- 关键词排序与清洗
- subreddit 列表排序与清洗
- language
- region_hints
- view_type
- 时间窗口
- 最低互动阈值
- pipeline_version

## 6.4 缓存命中逻辑

命中缓存的前提建议包括：

1. `normalized_query_key` 一致
2. `pipeline_version` 一致
3. 快照仍在有效新鲜度范围内
4. 非用户强制刷新请求

## 6.5 强制刷新

系统建议支持显式 `force_refresh`。

行为：

- 忽略现有结果缓存
- 创建新任务
- 产出新快照
- 保留历史快照不覆盖

---

## 7. Pipeline 总体设计

## 7.1 阶段划分

V1 建议将主 Pipeline 划分为 8 个阶段：

1. `validate`
2. `plan`
3. `fetch`
4. `normalize`
5. `retrieve`
6. `cluster`
7. `score`
8. `snapshot`

可选附加阶段：

9. `post_process`
10. `export`

## 7.2 阶段高层流程图

```text
validate
  -> plan
  -> fetch
  -> normalize
  -> retrieve
  -> cluster
  -> score
  -> snapshot
  -> finalize
```

## 7.3 阶段执行原则

- 每个阶段必须有明确输入与输出
- 每个阶段必须可记录耗时
- 每个阶段必须定义失败可否降级

---

## 8. 阶段设计详解

## 8.1 validate 阶段

### 目标

对输入做最终技术校验。

### 输入

- 用户请求
- 标准化查询对象

### 输出

- 合法执行参数
- 风险提示
- 是否进入下一阶段

### 失败条件

- 必填参数缺失
- 时间范围超限
- 模板不存在或状态不可用
- 输入明显不合法

### 降级策略

- 无降级，直接失败

---

## 8.2 plan 阶段

### 目标

生成本次任务的执行计划。

### 输入

- 标准化查询
- 主题模板
- 社区候选池
- 数据新鲜度信息

### 输出

- 需要拉取的 subreddit 列表
- 需要执行的 fetch 策略
- 时间窗口执行方案
- active / new 视角执行方案

### 失败条件

- 无有效执行范围

### 降级策略

- 若候选范围过大，可主动裁剪并记录覆盖说明

---

## 8.3 fetch 阶段

### 目标

从 Reddit 数据连接器获取原始帖子与评论。

### 输入

- 执行计划
- 关键词
- 候选社区范围
- 时间窗口

### 输出

- 原始帖子集合
- 原始评论集合
- 拉取统计
- 拉取失败清单

### 失败条件

- 全量拉取失败
- 数据连接器不可用

### 降级策略

- 某些 subreddit 失败时允许继续
- 部分评论失败时允许继续
- 结果覆盖说明中必须记录缺失范围

### 产物

- Raw payload 入对象存储
- 标准化前对象暂存

---

## 8.4 normalize 阶段

### 目标

将原始帖子与评论标准化为统一结构。

### 输入

- Raw post/comment 数据

### 输出

- `SourcePost`
- `SourceComment`
- 内容可访问性状态
- 语言标记
- crosspost 标记
- pinned / megathread 标记

### 失败条件

- 原始数据解析失败且无法恢复

### 降级策略

- 单条数据解析失败不阻断全局
- 记录坏数据数量与比例

### 说明

- Normalize 阶段后，数据应可写入检索层

---

## 8.5 retrieve 阶段

### 目标

在标准化数据中召回和本次需求发现相关的候选内容。

### 输入

- 标准化 post/comment
- 关键词
- 模板配置
- 语言
- 地域线索

### 输出

- 候选帖子集
- 候选评论集
- 召回统计
- 被过滤内容统计

### 失败条件

- 无法形成任何候选内容

### 降级策略

- 召回结果极少时允许继续，但标记“样本不足”
- 若只有帖子无评论，仍允许继续

### 备注

- retrieve 阶段是“召回”，不是“聚类”

---

## 8.6 cluster 阶段

### 目标

把离散候选内容转成需求聚类。

### 输入

- 候选帖子集
- 候选评论集

### 输出

- `DemandCluster`
- `ClusterEvidence`
- 支持 / 反对观点
- cluster 置信度

### 失败条件

- 无法形成任何满足最低结构的 cluster

### 降级策略

- 允许形成低置信度 cluster
- 允许形成弱信号 cluster
- 但必须打标签

### 关键子步骤

1. 问题表达抽取
2. 场景抽取
3. 痛点抽取
4. 替代方案抽取
5. 语义聚类
6. 历史 cluster 映射
7. 标题生成
8. 摘要生成

---

## 8.7 score 阶段

### 目标

对 cluster 计算榜单所需指标与分数。

### 输入

- 聚类结果
- 候选内容统计
- 对比窗口统计

### 输出

- `ClusterMetricSnapshot`
- 热门榜排序结果
- 高增长榜排序结果
- 高机会榜排序结果

### 失败条件

- 指标计算逻辑错误导致无法产出有效排序

### 降级策略

- 机会分失败时不阻断热门榜与高增长榜
- 对比窗口缺失时可不产出增长分
- 低样本结果可进入弱信号区

### 关键规则

- 排序依赖最低证据门槛
- 增长分不能因为分母为 0 崩溃
- 并列时执行 tie-break

---

## 8.8 snapshot 阶段

### 目标

生成不可变结果快照。

### 输入

- QueryTask
- 聚类结果
- 指标结果
- 排名结果
- 覆盖说明

### 输出

- `ResultSnapshot`
- `ResultSnapshotCluster`
- 任务最终可读结果

### 失败条件

- 无法持久化关键结果对象

### 降级策略

- 无降级；若无法落快照，则任务不能视作 `success`
- 但可考虑 `partial_success` + 内部告警，前提是已有临时结果缓存且产品允许

### 说明

- snapshot 是“可交付完成”的关键门槛

---

## 9. partial_success 判定标准

## 9.1 必须进入 partial_success 的典型情况

以下情况建议进入 `partial_success`：

1. 部分 subreddit 拉取失败，但其他社区足以形成结果
2. 评论数据不完整，但帖子数据足以形成榜单
3. 增长分无法完整计算，但热门榜可用
4. 部分证据原文不可访问，但统计和摘要可用

## 9.2 partial_success 的最低交付门槛

建议至少满足：

- 成功生成 `ResultSnapshot`
- 至少一个正式榜单可展示
- 至少一部分需求详情可展示
- 结果页有清晰覆盖说明

## 9.3 不应进入 partial_success 的情况

以下情况应直接 `failed`：

1. 无有效候选数据
2. 无法形成任何可展示 cluster
3. 无法生成结果快照
4. 查询输入本身非法

---

## 10. success 判定标准

任务进入 `success` 的建议条件：

1. 所有关键阶段完成
2. 成功生成 `ResultSnapshot`
3. 至少产出热门需求榜
4. 详情页所需核心字段齐备
5. 无重大覆盖缺口

### V1 推荐最低成功标准

- 热门需求榜可用
- 至少存在一个可展示 cluster
- 榜单与详情均有可追溯证据

---

## 11. failed 判定标准

建议失败原因至少分为以下几类：

### 11.1 输入失败

- 参数不合法
- 模板失效
- 查询范围超限

### 11.2 数据失败

- 数据连接器不可用
- 拉取结果完全为空
- 全部数据不可访问

### 11.3 计算失败

- 聚类阶段崩溃
- 评分阶段崩溃
- 快照阶段失败

### 11.4 系统失败

- 队列异常
- 存储异常
- 超时

### 11.5 failure_reason 建议结构

建议不仅存自由文本，还应有结构化 code：

- `INVALID_INPUT`
- `NO_FETCHABLE_SOURCE`
- `NO_VALID_CANDIDATE`
- `CLUSTERING_FAILED`
- `SCORING_FAILED`
- `SNAPSHOT_PERSIST_FAILED`
- `TASK_TIMEOUT`
- `SYSTEM_ERROR`

---

## 12. 幂等、重试与回放

## 12.1 幂等要求

系统需要防止：

- 用户连续点击产生重复任务
- Worker 重试导致重复写快照

### 幂等策略建议

- 基于 `normalized_query_key + pipeline_version + time_window + view_type`
- 对“正在运行中的等价任务”可直接复用

## 12.2 阶段重试

建议区分可重试与不可重试阶段：

### 可重试

- fetch
- normalize
- retrieve
- snapshot（有限重试）

### 谨慎重试

- cluster
- score

若这些阶段依赖外部 AI 组件，重试要注意结果漂移。

## 12.3 重试策略建议

- 指数退避
- 最大重试次数 2–3 次
- 达到上限后失败出队

## 12.4 任务回放

建议支持以 `query_task_id` 或 `result_snapshot_id` 进行回放定位。

### 回放目的

- 排障
- 算法对比
- 结果复查

### 回放要求

- 原始 payload 可追溯
- template version 固定
- pipeline version 可追溯

---

## 13. 超时与资源控制

## 13.1 任务级超时

建议设置任务总超时，例如：

- 常规任务：3 分钟
- 大任务：5 分钟（如产品允许）

超时后：

- 若已有最低可交付结果 -> `partial_success`
- 否则 -> `failed`

## 13.2 阶段级超时

建议各阶段分别记录耗时与阈值：

- fetch timeout
- normalize timeout
- retrieve timeout
- cluster timeout
- score timeout
- snapshot timeout

## 13.3 并发控制

需控制以下并发：

- 同一用户的同时重任务数
- 同一模板的大范围任务数
- 同一 subreddit 的抓取并发
- AI / embedding 阶段并发

---

## 14. Worker 设计建议

## 14.1 Worker 角色拆分

V1 可按职责拆成以下 worker：

### A. Fetch Worker

负责：

- 数据拉取
- 原始 payload 存储

### B. Normalize Worker

负责：

- 标准化
- 检索层写入

### C. Analysis Worker

负责：

- retrieve
- cluster
- score

### D. Snapshot Worker

负责：

- 结果持久化
- 排名结果写入

### E. Export Worker

负责：

- Markdown / CSV 导出

## 14.2 V1 实施建议

V1 可以先从：

- 单个通用 pipeline worker
- 内部按 stage 划分模块

开始。

当负载变高后，再物理拆分 Fetch Worker / Analysis Worker。

---

## 15. 日志、监控与审计

## 15.1 QueryTaskRunLog 记录要求

每个阶段至少记录：

- stage
- status
- started_at
- finished_at
- duration_ms
- input_count
- output_count
- warning_count
- error_code
- error_message

## 15.2 核心监控指标

### 任务层

- 任务创建数
- success rate
- partial_success rate
- failure rate
- timeout rate

### 阶段层

- fetch 平均耗时
- normalize 平均耗时
- cluster 平均耗时
- score 平均耗时
- snapshot 平均耗时

### 质量层

- 平均 cluster 数
- 平均证据数
- 样本不足比例
- 低置信度比例

## 15.3 审计要求

每个结果至少可追溯：

- 来源任务
- 模板版本
- pipeline version
- 数据覆盖说明
- 证据来源

---

## 16. API 设计承接要求

虽然本文档不定义完整 API，但对接口层有以下要求：

## 16.1 创建查询接口

必须返回：

- `query_task_id`
- 当前状态
- 是否命中缓存
- 若命中缓存则返回 `result_snapshot_id`

## 16.2 查询状态接口

必须返回：

- `query_task_id`
- `status`
- 当前 stage
- 进度信息
- `result_snapshot_id`（若已有）
- 覆盖说明（若 partial_success）

## 16.3 查询结果接口

必须支持：

- 通过 `result_snapshot_id` 读取
- 榜单类型切换
- 视角切换
- 分页

## 16.4 详情接口

必须支持：

- 按 `cluster_id + result_snapshot_id` 读取
- 返回指标、证据、状态标签

---

## 17. V1 与后续版本的任务系统演进

## 17.1 V1

- 一次性查询任务
- 手动触发
- 结果快照持久化

## 17.2 V1.5

- 定时查询任务
- 订阅任务
- 趋势检查任务
- 通知任务

## 17.3 V2

- 多模板批量分析任务
- 竞品对比任务
- 内容 Brief 生成任务

### 演进原则

后续所有任务类型，仍建议统一挂在 `QueryTask` 或其兼容扩展体系下。

---

## 18. 推荐下一步产出

基于本文档，建议后续继续输出：

1. `doc/api_contract_draft.md`
2. `doc/information_architecture_and_state_flow.md`
3. `doc/scoring_engine_design.md`

---

## 19. 一句话结论

本系统的执行核心，不是“查一下 Reddit”，而是：

> **把一次需求发现请求，转成一个可追踪、可降级、可复现的 QueryTask Pipeline。**
