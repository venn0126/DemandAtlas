# Demand Atlas｜需见 技术架构输入文档

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 技术架构输入文档
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：技术方案设计 / 架构评审 / 数据模型设计 / 接口设计
- 输入来源：
  - `doc/prd_reddit_needs_discovery.md`

---

## 2. 文档目标

本文档用于把产品 PRD 翻译成技术架构可直接承接的输入。

本文档重点回答以下问题：

1. V1 系统边界是什么
2. 核心对象模型是什么
3. 查询任务如何执行
4. Reddit 数据如何进入系统并被分析
5. 需求聚类、评分、证据、导出如何落地
6. 哪些能力是 V1 必做，哪些是后续扩展点

### 2.1 本文档不覆盖的内容

本文档不直接给出：

- 最终选型定稿
- 详细数据库 DDL
- 详细 API schema
- 最终部署拓扑
- 最终算法实现细节

这些将在后续专项文档中继续细化。

---

## 3. V1 技术边界与关键决策

## 3.1 V1 技术边界

V1 的系统边界如下：

- 仅处理 Reddit 公开可获取内容
- 以英文内容为主
- 不承诺 Reddit 全站全量覆盖
- 不纳入私有、封禁、不可访问社区内容
- 默认不纳入 NSFW / Quarantined 社区内容
- 不提供严格国家级过滤，仅支持语言 + 地域线索
- 默认服务“需求发现”而非“全量舆情监控”

## 3.2 V1 产品闭环对应的技术闭环

V1 要闭环的是：

1. 用户发起查询
2. 系统生成查询任务
3. 系统召回 Reddit 内容
4. 系统清洗、聚类、评分、生成需求卡片
5. 返回榜单与详情
6. 支持导出结果

V1 不要求闭环的能力：

- 团队共享视图
- 复杂权限系统
- 多平台数据接入
- 自动营销执行
- 完整订阅中心

## 3.3 技术架构原则

后续架构设计建议遵循以下原则：

### A. 离线重、在线轻

- 重计算尽量放到异步任务中
- 在线查询尽量以取结果、排序、过滤、拼装为主

### B. 结果可复现

- 每次查询必须能落结果快照
- 导出、分享、复盘都基于快照而不是实时漂移结果

### C. 降级优先

- 数据不完整时允许部分成功
- 原文缺失时允许证据降级
- 不因局部失败导致全任务失败

### D. 可解释优先

- 需求卡片需要可追溯到证据
- 排序分必须能解释主要构成

### E. 扩展优先于一次性完美

- V1 要为 V1.5 的订阅、收藏、需求库保留扩展点

---

## 4. 需求到系统能力映射

| 产品需求 | 技术能力 |
|---|---|
| 一键发现 | 主题模板、候选社区池、模板化查询任务 |
| 定向发现 | 关键词召回、社区过滤、语言过滤、地域线索辅助 |
| 新发 / 活跃双视角 | 双时间索引、双统计口径 |
| 热门需求榜 | 聚类结果 + 讨论度 / 关注度综合排序 |
| 高增长需求榜 | 窗口对比、增长计算、样本门槛 |
| 高机会需求榜 | 规则 + AI 辅助评分 |
| 需求详情页 | 需求聚类对象 + 证据拼装 |
| 原话证据 | 证据抽取、证据引用规范、可访问性降级 |
| 查询任务状态 | 异步任务系统、状态流转、轮询接口 |
| 导出 | 结果快照、导出生成器 |
| 后续订阅 | 任务/聚类快照、趋势检查、通知扩展点 |

---

## 5. 高层逻辑架构

建议将系统拆为 6 层：

1. **接入层**
2. **查询编排层**
3. **数据采集与预处理层**
4. **分析计算层**
5. **结果服务层**
6. **支撑与治理层**

### 5.1 高层架构图（逻辑）

```text
用户 / 前端
   |
   v
API Gateway / BFF
   |
   v
Query Orchestrator
   |--------------------------|
   |                          |
   v                          v
Cache / Snapshot          Async Task Queue
                              |
                              v
                      Data Fetch + Normalize
                              |
                              v
                      Retrieve + Filter + Cluster
                              |
                              v
                      Score + Summarize + Evidence
                              |
                              v
                       Result Snapshot Storage
                              |
                              v
                        Result Serving APIs
```

### 5.2 各层职责

#### 1. 接入层

负责：

- 查询请求接收
- 鉴权
- 输入校验
- 结果页拼装

#### 2. 查询编排层

负责：

- 标准化查询输入
- 命中缓存判断
- 生成 `query_task`
- 同步 / 异步路由决策

#### 3. 数据采集与预处理层

负责：

- 从 Reddit 数据连接器获取帖子与评论
- 标准化原始数据
- 去重、可访问性标记、语言识别、噪声过滤

#### 4. 分析计算层

负责：

- 文本召回
- 需求抽取
- 聚类归并
- 评分计算
- 原话证据抽取
- 摘要生成

#### 5. 结果服务层

负责：

- 榜单结果读取
- 详情结果读取
- 导出
- 结果快照回放

#### 6. 支撑与治理层

负责：

- 日志
- 监控
- 任务追踪
- 模板版本管理
- 配置中心

---

## 6. 核心对象模型

下列对象是后续数据模型设计的核心输入。

## 6.1 TopicTemplate

用于驱动一键发现。

### 最低字段

- `template_id`
- `template_version`
- `name`
- `keywords`
- `synonyms`
- `exclude_terms`
- `candidate_subreddits`
- `default_language`
- `default_view_type`（active / new）
- `default_sort_strategy`
- `status`

### 说明

- 模板必须版本化
- 历史查询必须绑定模板版本

---

## 6.2 QueryTask

查询任务对象，是在线与异步执行的锚点。

### 最低字段

- `query_task_id`
- `query_type`（one_click / directed）
- `input_payload`
- `normalized_query_key`
- `template_id`（可空）
- `template_version`（可空）
- `view_type`（active / new）
- `time_window`
- `status`
- `started_at`
- `finished_at`
- `result_snapshot_id`
- `failure_reason`
- `created_by_user_id`（匿名可空）

### 状态流转

```text
pending -> running -> success
pending -> running -> partial_success
pending -> running -> failed
```

### 说明

- `normalized_query_key` 用于缓存命中
- `result_snapshot_id` 用于结果复现与导出

---

## 6.3 SourcePost

Reddit 原始帖子标准化对象。

### 最低字段

- `source_post_id`
- `reddit_post_id`
- `subreddit`
- `title`
- `body`
- `author_ref`
- `score`
- `comment_count`
- `created_at`
- `fetched_at`
- `content_availability_status`
- `is_crosspost`
- `is_pinned`
- `is_nsfw`
- `raw_payload_ref`

---

## 6.4 SourceComment

Reddit 原始评论标准化对象。

### 最低字段

- `source_comment_id`
- `reddit_comment_id`
- `reddit_post_id`
- `parent_comment_id`
- `subreddit`
- `body`
- `author_ref`
- `score`
- `depth`
- `created_at`
- `fetched_at`
- `content_availability_status`
- `raw_payload_ref`

---

## 6.5 DemandCluster

需求聚类对象，是产品输出核心。

### 最低字段

- `cluster_id`
- `canonical_title`
- `summary`
- `scenes`
- `pain_points`
- `alternatives`
- `sentiment_profile`
- `supporting_evidence_ids`
- `opposing_evidence_ids`
- `first_seen_at`
- `last_seen_at`
- `confidence_score`
- `cluster_version`

### 说明

- `cluster_id` 要尽量稳定
- `cluster_version` 用于记录后处理合并 / 拆分历史

---

## 6.6 ClusterMetricSnapshot

用于记录某个需求聚类在某个时间窗口下的指标快照。

### 最低字段

- `snapshot_id`
- `cluster_id`
- `query_task_id`
- `view_type`
- `window_start`
- `window_end`
- `post_count`
- `comment_count`
- `unique_user_count`
- `avg_comment_depth`
- `avg_post_score`
- `avg_comment_score`
- `high_engagement_post_ratio`
- `community_spread_count`
- `discussion_score`
- `attention_score`
- `growth_score`
- `opportunity_score`
- `is_weak_signal`
- `is_low_confidence`

---

## 6.7 EvidenceSnippet

结果展示与导出的证据对象。

### 最低字段

- `evidence_id`
- `cluster_id`
- `source_type`（post / comment）
- `source_ref_id`
- `excerpt`
- `subreddit`
- `created_at`
- `stance`（support / oppose / neutral）
- `availability_status`
- `source_url`

---

## 6.8 ResultSnapshot

不可变结果快照对象，用于列表、详情、导出复现。

### 最低字段

- `result_snapshot_id`
- `query_task_id`
- `query_input_snapshot`
- `template_snapshot`
- `pipeline_version`
- `generated_at`
- `summary_stats`
- `cluster_ids`
- `coverage_note`

---

## 6.9 扩展对象（V1.5+）

为后续扩展预留：

- `SavedQuery`
- `AlertRule`
- `DemandLibraryItem`

V1 不要求实现完整功能，但对象关系需要预留。

---

## 7. 查询执行架构

## 7.1 查询分类

系统需要区分三类请求：

### A. 缓存命中请求

- 直接返回已有快照

### B. 轻量新请求

- 可在较短时间内完成召回与计算
- 允许同步触发后快速轮询返回

### C. 重型请求

- 数据范围大
- 关键词过泛
- 社区范围过宽
- 需要异步任务执行

## 7.2 查询标准化

发起任务前，需做查询标准化，用于：

- 缓存命中
- 幂等去重
- 结果复现

### 标准化内容

- 去除大小写差异
- 规范关键词顺序
- 规范社区列表顺序
- 规范时间窗口表达
- 固定主题模板版本
- 固定视角（active / new）

## 7.3 Query Key 设计要求

建议由以下字段组成：

- query_type
- template_id / template_version
- normalized_keywords
- normalized_subreddit_scope
- language
- region_hints
- time_window
- view_type
- min_engagement_threshold
- pipeline_version

## 7.4 查询状态与前端状态映射

| query_task.status | 前端状态 |
|---|---|
| pending | 已创建，等待执行 |
| running | 查询进行中 |
| partial_success | 已返回部分结果，提示覆盖不完整 |
| success | 查询完成 |
| failed | 查询失败，可重试 |

## 7.5 缓存策略建议

### 缓存目标

- 降低重复查询成本
- 提升常见查询响应速度

### 缓存建议

- 结果快照缓存：按 `normalized_query_key`
- 任务状态缓存：按 `query_task_id`
- 主题模板缓存：按 `template_id + version`

### 缓存 TTL 建议

- 7 天 / 30 天热点查询：6–12 小时
- 90 天及更长窗口查询：12–24 小时
- 主题模板：发布后长期缓存，按版本失效

### 说明

- 用户拿到的是“查询时刻的结果快照”
- 刷新查询时可显式触发新任务，不覆盖历史快照

---

## 8. 数据采集与预处理架构

## 8.1 数据接入模式

建议采用双模式：

### A. 预同步模式

适用于：

- 热门社区
- 核心主题模板中的社区
- 高复用查询范围

### B. 查询触发补拉模式

适用于：

- 用户指定的长尾社区
- 不常用关键词
- 需要临时补充的数据范围

## 8.2 数据接入接口抽象

无论最终使用何种 Reddit 数据连接方式，建议统一封装为 `RedditConnector` 抽象层。

### 最低能力

- 按社区拉取帖子
- 按关键词拉取帖子
- 获取帖子评论
- 获取内容状态（可访问 / 删除 / 移除）

## 8.3 原始数据分层

建议至少分三层存储：

### 1. Raw Layer

- 原始响应
- 原始字段
- 原始追踪信息

### 2. Normalized Layer

- 标准化帖子 / 评论对象
- 统一时间、字段、状态

### 3. Derived Layer

- 聚类
- 指标
- 结果快照

## 8.4 预处理步骤

建议处理链路如下：

1. 基础字段标准化
2. 内容可访问性标记
3. 语言识别
4. 噪声过滤
5. crosspost 识别
6. pinned / megathread 标记
7. 文本切分
8. 嵌入 / 检索索引构建（如采用）

## 8.5 内容可访问性处理

| 状态 | 处理方式 |
|---|---|
| 公开可访问 | 正常纳入分析 |
| 已删除 / 已移除 | 可保留统计和最小元信息 |
| 私有 / 不可访问 | V1 排除 |
| 封禁社区 | V1 排除 |
| NSFW / Quarantined | V1 默认排除 |

---

## 9. 召回与检索架构

## 9.1 一键发现召回策略

一键发现依赖 `TopicTemplate`：

1. 模板关键词召回
2. 模板候选社区池限制
3. 模板排除词过滤
4. 模板默认语言过滤

### 说明

一键发现本质是“预定义赛道查询”。

## 9.2 定向发现召回策略

定向发现依赖：

1. 用户关键词 / 关键词组
2. 可选社区范围
3. 语言
4. 地域线索

建议采用两阶段召回：

### 第一阶段：强约束召回

- 精确关键词
- 社区过滤
- 时间窗口过滤

### 第二阶段：语义扩展召回

- 同义词
- 近义场景词
- 评论证据补足

## 9.3 输入校验与降噪

对以下情况需要前置拦截或提示：

- 过泛词，如 `best`, `tool`
- 歧义词，如 `apple`
- 关键词数量过多
- 社区范围过大

### 校验处理建议

- 直接拒绝
- 给出建议限定词
- 自动收窄

三种策略可按严重程度配置。

---

## 10. 聚类与需求识别架构

## 10.1 计算目标

将离散的帖子与评论转化为稳定的需求聚类，并保留证据链。

## 10.2 推荐计算流程

建议拆分为以下步骤：

1. 候选内容召回
2. 问题表达抽取
3. 场景与痛点抽取
4. 替代方案与立场抽取
5. 语义聚类
6. 跨帖子归并
7. 历史聚类映射
8. 标题生成与摘要生成
9. 置信度评估

## 10.3 聚类 ID 稳定性要求

V1 不要求全球绝对稳定，但要求满足：

- 同一查询内稳定
- 同主题、多窗口查询间尽量稳定
- 允许通过“历史映射表”做后处理归并

### 推荐做法

- 先生成临时 cluster
- 再通过历史相似度映射到 canonical cluster
- 保留合并 / 拆分映射日志

## 10.4 低置信度处理

低置信度结果不应与正常结果等价对待。

建议规则：

- 低置信度结果进入单独标记状态
- 不默认触发订阅
- 高机会分降级或隐藏

## 10.5 观点冲突处理

同一需求可能同时有支持与反对观点。

系统应支持：

- `supporting_evidence_ids`
- `opposing_evidence_ids`

详情页可展示：

- 为什么用户想要它
- 为什么用户不建议它

---

## 11. 评分与排序架构

## 11.1 评分引擎职责

评分引擎负责：

- 计算基础统计
- 做归一化
- 执行排序公式
- 输出榜单用分数

## 11.2 必要输入指标

至少需要以下原始统计：

- 帖子数
- 评论数
- 独立用户数
- 评论深度
- 平均帖子得分
- 平均评论得分
- 高互动帖占比
- 社区扩散数
- 上周期同类指标

## 11.3 归一化建议

V1 建议：

- 在单次查询结果集中归一化
- 对超大社区做规模平滑
- 对极端高值做截断或对数缩放

## 11.4 默认排序策略

### 热门需求榜

建议公式：

`hot_score = w1 * discussion_score + w2 * attention_score`

### 高增长需求榜

建议公式：

`growth_rank = growth_score`

并且要求：

- 满足最低证据门槛
- 上周期为 0 时标记新兴信号

### 高机会需求榜

建议公式：

`opportunity_rank = opportunity_score`

但仅作为辅助榜单。

## 11.5 Tie-break 规则

分数并列时按以下顺序：

1. `confidence_score`
2. 证据量
3. 最近活跃时间
4. 稳定 ID 排序

---

## 12. 结果服务与导出架构

## 12.1 榜单服务

榜单服务负责：

- 根据 `result_snapshot_id` 返回结果
- 支持不同榜单切换
- 支持 active / new 切换
- 支持分页 / Top N

## 12.2 详情服务

详情服务负责：

- 返回需求卡片完整信息
- 返回证据列表
- 返回指标解释
- 返回来源社区分布

## 12.3 导出服务

导出服务负责：

- 基于结果快照导出 Markdown / CSV
- 保证导出内容与页面内容一致
- 保证导出时携带模板版本、时间窗口、查询条件

## 12.4 证据展示约束

导出与页面都需要遵循：

- 证据默认展示 1–3 条代表性原话
- 使用短摘录
- 附来源社区、时间、跳转链接
- 对不可访问原文做降级说明

---

## 13. 存储架构建议

## 13.1 逻辑存储拆分

建议至少拆为以下存储角色：

### A. 事务型数据库

用于：

- 任务状态
- 模板版本
- 用户配置
- 结果快照元数据

推荐类型：

- PostgreSQL 或同类关系型数据库

### B. 搜索 / 检索索引

用于：

- 帖子 / 评论检索
- 关键词召回
- 可能的语义检索

推荐类型：

- OpenSearch / Elasticsearch
- 或关系型全文索引 + 向量扩展的组合

### C. 对象存储

用于：

- 原始抓取 payload
- 导出文件
- 任务中间产物

### D. 缓存

用于：

- 查询结果缓存
- 任务状态缓存
- 模板缓存

推荐类型：

- Redis

### E. 队列 / 任务系统

用于：

- 异步查询任务
- 数据补拉任务
- 后处理任务

## 13.2 数据隔离建议

建议将以下数据显式隔离：

- Raw 原始数据
- Normalized 结构化数据
- Derived 结果数据
- Snapshot 快照数据

原因：

- 便于回放
- 便于重算
- 便于故障定位

---

## 14. 服务拆分建议

V1 不需要过度微服务化，但建议按职责清晰拆分模块。

## 14.1 推荐服务边界

### 1. API / BFF

职责：

- 前端请求接入
- 结果拼装
- 会话与鉴权

### 2. Query Orchestrator

职责：

- 查询标准化
- query_task 创建
- 缓存判断
- 任务路由

### 3. Data Connector Service

职责：

- Reddit 数据接入
- 社区 / 关键词内容获取

### 4. Analysis Pipeline Service

职责：

- 召回
- 聚类
- 评分
- 摘要

### 5. Result Service

职责：

- 榜单读取
- 详情读取
- 导出

### 6. Template / Config Service

职责：

- TopicTemplate 管理
- 规则参数管理
- 阈值管理

## 14.2 V1 实施建议

V1 可以是“模块化单体 + 独立异步任务 worker”的形态，不必一开始就做复杂微服务拆分。

原因：

- 逻辑仍在快速迭代
- 算法链路与产品规则还会变化
- 先强调边界清晰，再决定是否物理拆分

---

## 15. 非功能要求

## 15.1 性能目标

- 缓存命中的常见查询：10 秒内返回首屏结果
- 异步查询：3 分钟内返回可用结果或失败状态
- 榜单页读取：应明显快于重新跑查询
- 导出：默认异步生成，避免阻塞主查询链路

## 15.2 可用性目标

- 局部数据源失败不应导致全任务必然失败
- 允许 `partial_success`
- 所有失败必须可观测、可回溯

## 15.3 可观测性目标

至少需要监控以下内容：

- query_task 数量与状态分布
- 平均查询耗时
- 缓存命中率
- 数据补拉成功率
- 聚类耗时
- 评分耗时
- 导出成功率

## 15.4 审计与复现

- 每次查询必须可通过 `result_snapshot_id` 回放
- 关键输出应记录 pipeline version
- 模板变更不应污染历史结果解释

---

## 16. 安全、合规与数据治理

## 16.1 数据最小化原则

- 作者信息只保留必要引用字段
- 不为 V1 引入不必要的个人画像数据

## 16.2 内容状态尊重

- 对已删除 / 已移除内容做降级处理
- 对不可访问内容不强制展示原文

## 16.3 社区边界尊重

- 不纳入私有、封禁、不可访问社区
- 不默认纳入 NSFW / Quarantined 社区

## 16.4 导出治理

- 导出仅包含结果所需字段
- 导出文件应包含时间窗口、模板版本、查询条件、生成时间

---

## 17. 页面与接口设计必须承接的状态

后续交互设计与 API 设计，必须覆盖以下状态：

## 17.1 查询页

- 空白态
- 输入校验失败
- 正在执行
- 已转异步
- 执行失败

## 17.2 榜单页

- 正常结果
- 无结果
- 样本不足
- 低置信度
- 部分成功

## 17.3 详情页

- 完整证据
- 原文部分不可访问
- 低置信度
- 观点冲突

## 17.4 导出

- 导出中
- 导出完成
- 导出失败

---

## 18. V1 与后续版本的架构分层

## 18.1 V1 必须实现

- 查询任务
- 主题模板
- Reddit 数据接入
- 候选社区池 + 查询补拉
- 需求聚类
- 热门需求榜
- 高增长需求榜
- 需求详情页
- 结果快照
- 导出

## 18.2 V1.5 扩展点

- 提醒 / 订阅
- 收藏 / 标签
- 基础需求库
- 飞书 / Notion 导出扩展

## 18.3 V2 扩展点

- 多赛道模板运营平台
- 竞品对比分析
- AI Brief 自动生成

## 18.4 V3 扩展点

- 多平台接入
- 跨平台交叉验证

---

## 19. 技术评审前必须确认的事项

架构设计正式启动前，建议产品、技术共同拍板以下事项：

1. Reddit 数据连接方式与接入策略
2. V1 是否允许匿名查询
3. V1 是否实现保存查询，还是仅保留接口扩展点
4. V1 是否实现收藏 / 标签，还是延后到 V1.5
5. V1 的社区候选池维护方式
6. V1 的模板管理是否需要后台
7. V1 的向量检索是否首版就上
8. V1 的导出是同步还是异步

这些事项不决定，会影响具体技术方案稳定性。

---

## 20. 推荐下一步产出

基于本文档，建议后续按顺序继续输出：

1. `doc/domain_model_and_schema.md`
   - 详细对象模型
   - 表结构建议
   - 索引建议

2. `doc/query_task_and_pipeline_design.md`
   - 查询任务状态机
   - 异步流程
   - Pipeline 分阶段设计

3. `doc/api_contract_draft.md`
   - 查询接口
   - 结果接口
   - 导出接口

4. `doc/information_architecture_and_state_flow.md`
   - 页面流
   - 状态流
   - 前后端状态映射

---

## 21. 一句话结论

本产品的技术架构，不应被设计成一个“实时全量 Reddit 搜索系统”，而应被设计成一个：

> **以查询任务为中心、以结果快照为交付物、以异步分析管线为核心的 Reddit 需求发现系统。**
