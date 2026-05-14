# Demand Atlas｜需见 领域模型与 Schema 设计文档

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 领域模型与 Schema 设计文档
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：数据模型设计 / 数据库设计 / 检索索引设计 / 接口设计
- 上游输入：
  - `doc/prd_reddit_needs_discovery.md`
  - `doc/technical_architecture_input.md`

---

## 2. 文档目标

本文档用于明确系统的核心领域对象，以及这些对象在存储层的落地方式。

本文档重点回答：

1. V1 需要哪些核心数据对象
2. 每个对象的最小字段集合是什么
3. 各对象之间是什么关系
4. 哪些数据放关系库，哪些放检索索引，哪些放对象存储
5. 后续 V1.5 / V2 如何扩展而不推翻 V1

### 2.1 本文档不直接覆盖

- 最终 SQL DDL
- ORM 实现
- 最终搜索引擎 mapping
- 向量索引具体实现
- 数据迁移脚本

---

## 3. 设计原则

## 3.1 快照优先

- 所有面向用户的结果都应可通过快照复现
- 查询结果不能依赖“再次实时计算”才能重建

## 3.2 原始数据与衍生数据分层

至少区分：

- 原始数据
- 标准化数据
- 结果快照数据

## 3.3 内部主键与外部 ID 分离

- 系统内部对象使用内部 ID
- Reddit 原始对象使用外部 ID 单独保存
- 避免业务逻辑直接绑死在外部平台 ID 上

## 3.4 支持可追溯

任何需求卡片、指标、建议都应能追溯到：

- 查询任务
- 时间窗口
- 模板版本
- 证据对象

## 3.5 支持演进

V1 的模型必须能平滑扩展到：

- 收藏与需求库
- 订阅与提醒
- 多平台
- 聚类版本演进

---

## 4. 存储分层建议

建议系统至少使用 4 类存储：

## 4.1 关系型数据库

用于存储：

- 主题模板
- 查询任务
- 结果快照元数据
- 需求聚类主数据
- 聚类指标快照
- 用户行为与后续扩展对象

推荐：

- PostgreSQL

## 4.2 搜索 / 检索索引

用于存储：

- SourcePost
- SourceComment
- 全文检索字段
- 结构化过滤字段

推荐：

- OpenSearch / Elasticsearch

## 4.3 对象存储

用于存储：

- 原始抓取 payload
- 导出文件
- 大型中间结果

## 4.4 缓存

用于存储：

- 查询状态
- 热门查询缓存
- 模板缓存

推荐：

- Redis

---

## 5. 领域模型总览

## 5.1 核心实体

V1 核心实体如下：

1. User
2. TopicTemplate
3. TopicTemplateVersion
4. SubredditCatalog
5. QueryTask
6. QueryTaskRunLog
7. SourcePost
8. SourceComment
9. DemandCluster
10. DemandClusterAlias
11. ClusterEvidence
12. ClusterMetricSnapshot
13. ResultSnapshot
14. ResultSnapshotCluster
15. ExportJob

### V1.5 预留实体

16. SavedQuery
17. AlertRule
18. DemandLibraryItem

## 5.2 核心关系

```text
User
  └── QueryTask
        ├── ResultSnapshot
        │     └── ResultSnapshotCluster
        │            └── DemandCluster
        │                   ├── ClusterEvidence -> SourcePost / SourceComment
        │                   └── ClusterMetricSnapshot
        └── QueryTaskRunLog

TopicTemplate
  └── TopicTemplateVersion
         └── TopicTemplateVersionSubreddit

SubredditCatalog
SourcePost
  └── SourceComment
```

---

## 6. ID 与命名约定

## 6.1 内部 ID 约定

建议：

- 关系型主键统一使用 `uuid`
- 优先采用 UUID v7 或等价可排序 ID

## 6.2 外部 ID 约定

对 Reddit 外部对象：

- `reddit_post_id` 使用 text
- `reddit_comment_id` 使用 text
- `reddit_subreddit_name` 使用 text

## 6.3 时间字段约定

统一使用：

- `created_at`
- `updated_at`
- `deleted_at`（如有软删除）

所有时间字段建议使用：

- `timestamptz`

## 6.4 JSON 字段约定

对高变结构建议使用：

- `jsonb`

但不应滥用，核心检索字段仍应结构化。

---

## 7. 关系库 Schema 设计

以下为逻辑表结构建议，不是最终 DDL。

## 7.1 users

### 用途

存储用户基础身份信息。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | 内部用户 ID |
| email | text unique nullable | 邮箱 |
| auth_provider | text | 登录来源 |
| display_name | text | 展示名 |
| status | text | active / disabled |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 索引建议

- unique(email)

### 说明

- 匿名查询不要求 user 记录
- 登录后能力均绑定到 `users.id`

---

## 7.2 topic_templates

### 用途

主题模板主表。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | 模板 ID |
| code | text unique | 模板编码 |
| name | text | 模板名称 |
| description | text | 模板说明 |
| default_language | text | 默认语言 |
| status | text | draft / active / archived |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 索引建议

- unique(code)
- index(status)

---

## 7.3 topic_template_versions

### 用途

保存主题模板版本快照。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | 模板版本 ID |
| template_id | uuid fk | 关联模板 |
| version_no | integer | 版本号 |
| keywords | jsonb | 关键词组 |
| synonyms | jsonb | 同义词组 |
| exclude_terms | jsonb | 排除词 |
| default_view_type | text | active / new |
| default_sort_strategy | text | 默认排序 |
| config_snapshot | jsonb | 其他配置快照 |
| created_at | timestamptz | 创建时间 |

### 约束建议

- unique(template_id, version_no)

### 索引建议

- index(template_id)

---

## 7.4 topic_template_version_subreddits

### 用途

记录某模板版本绑定的候选社区池。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | 主键 |
| template_version_id | uuid fk | 模板版本 |
| subreddit_name | text | 社区名 |
| priority | integer | 优先级 |
| created_at | timestamptz | 创建时间 |

### 约束建议

- unique(template_version_id, subreddit_name)

### 索引建议

- index(template_version_id)
- index(subreddit_name)

---

## 7.5 subreddit_catalog

### 用途

Subreddit 维表，用于维护社区元信息。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | 主键 |
| subreddit_name | text unique | 社区名 |
| title | text | 社区标题 |
| description | text | 社区简介 |
| is_nsfw | boolean | 是否 NSFW |
| is_quarantined | boolean | 是否 Quarantined |
| is_private | boolean | 是否私有 |
| is_banned | boolean | 是否封禁 |
| region_hints | jsonb | 地域线索 |
| language_hints | jsonb | 语言线索 |
| member_count | bigint nullable | 订阅人数 |
| last_synced_at | timestamptz | 最近同步时间 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 索引建议

- unique(subreddit_name)
- index(is_nsfw, is_quarantined, is_private, is_banned)

---

## 7.6 query_tasks

### 用途

查询任务主表。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | query_task_id |
| user_id | uuid fk nullable | 用户 ID，匿名可空 |
| query_type | text | one_click / directed |
| template_id | uuid nullable | 主题模板 ID |
| template_version_id | uuid nullable | 模板版本 ID |
| input_payload | jsonb | 原始输入 |
| normalized_query_key | text | 标准化查询 key |
| language | text | 语言 |
| region_hints | jsonb | 地域线索 |
| min_engagement_threshold | jsonb | 最低互动阈值 |
| view_type | text | active / new |
| window_start | timestamptz | 查询窗口开始 |
| window_end | timestamptz | 查询窗口结束 |
| compare_window_start | timestamptz nullable | 对比窗口开始 |
| compare_window_end | timestamptz nullable | 对比窗口结束 |
| status | text | pending / running / partial_success / success / failed |
| pipeline_version | text | 分析 pipeline 版本 |
| cached_from_snapshot_id | uuid nullable | 若命中缓存，记录来源 |
| result_snapshot_id | uuid nullable | 结果快照 |
| failure_reason | text nullable | 失败原因 |
| started_at | timestamptz nullable | 开始时间 |
| finished_at | timestamptz nullable | 结束时间 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 约束建议

- 视 query 类型约束 template 字段是否必填

### 索引建议

- unique(normalized_query_key, pipeline_version, view_type, window_start, window_end) 可按需要调整
- index(user_id, created_at desc)
- index(status, created_at desc)
- index(result_snapshot_id)

### 说明

- 如不希望 unique 过强，可改为普通索引 + 缓存层去重

---

## 7.7 query_task_run_logs

### 用途

记录任务执行阶段日志，便于追踪与排障。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | 主键 |
| query_task_id | uuid fk | 任务 ID |
| stage | text | validate / fetch / normalize / cluster / score / snapshot / export |
| status | text | pending / running / success / failed |
| message | text | 日志摘要 |
| meta | jsonb | 补充信息 |
| started_at | timestamptz nullable | 开始时间 |
| finished_at | timestamptz nullable | 结束时间 |
| created_at | timestamptz | 创建时间 |

### 索引建议

- index(query_task_id, created_at)
- index(stage, status)

---

## 7.8 demand_clusters

### 用途

需求聚类主表。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | cluster_id |
| canonical_title | text | 规范标题 |
| summary | text | 摘要 |
| scenes | jsonb | 场景列表 |
| pain_points | jsonb | 痛点列表 |
| alternatives | jsonb | 替代方案列表 |
| sentiment_profile | jsonb | 情绪画像 |
| confidence_score | numeric(5,2) | 置信度 |
| cluster_status | text | active / merged / split / archived |
| current_version | integer | 当前版本 |
| first_seen_at | timestamptz | 首次出现时间 |
| last_seen_at | timestamptz | 最近活跃时间 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 索引建议

- index(cluster_status)
- index(last_seen_at desc)
- index(confidence_score desc)

---

## 7.9 demand_cluster_aliases

### 用途

记录同义表达、历史归并、候选标题等。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | 主键 |
| cluster_id | uuid fk | 需求聚类 |
| alias_text | text | 别名 / 同义表达 |
| alias_type | text | synonym / generated_title / historical_label |
| source | text | rule / llm / manual |
| created_at | timestamptz | 创建时间 |

### 约束建议

- unique(cluster_id, alias_text)

### 索引建议

- index(cluster_id)
- index(alias_text)

---

## 7.10 cluster_metric_snapshots

### 用途

记录某个 cluster 在某个查询窗口下的指标快照。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | snapshot_id |
| cluster_id | uuid fk | 需求聚类 |
| query_task_id | uuid fk | 来源任务 |
| result_snapshot_id | uuid fk | 来源结果快照 |
| view_type | text | active / new |
| window_start | timestamptz | 当前窗口开始 |
| window_end | timestamptz | 当前窗口结束 |
| compare_window_start | timestamptz nullable | 对比窗口开始 |
| compare_window_end | timestamptz nullable | 对比窗口结束 |
| post_count | integer | 帖子数 |
| comment_count | integer | 评论数 |
| unique_user_count | integer | 独立用户数 |
| avg_comment_depth | numeric(8,2) | 平均评论深度 |
| avg_post_score | numeric(10,2) | 平均帖子分 |
| avg_comment_score | numeric(10,2) | 平均评论分 |
| high_engagement_post_ratio | numeric(5,2) | 高互动帖占比 |
| community_spread_count | integer | 社区扩散数 |
| discussion_score | numeric(5,2) | 讨论度分 |
| attention_score | numeric(5,2) | 关注度分 |
| growth_score | numeric(5,2) nullable | 增长分 |
| opportunity_score | numeric(5,2) nullable | 机会分 |
| is_weak_signal | boolean | 是否弱信号 |
| is_low_confidence | boolean | 是否低置信度 |
| created_at | timestamptz | 创建时间 |

### 约束建议

- unique(cluster_id, query_task_id)

### 索引建议

- index(query_task_id)
- index(result_snapshot_id)
- index(cluster_id, window_end desc)
- index(discussion_score desc)
- index(growth_score desc)

---

## 7.11 result_snapshots

### 用途

结果快照主表。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | result_snapshot_id |
| query_task_id | uuid fk | 来源任务 |
| query_input_snapshot | jsonb | 查询输入快照 |
| template_snapshot | jsonb nullable | 模板快照 |
| summary_stats | jsonb | 汇总统计 |
| coverage_note | text | 覆盖说明 |
| sync_freshness_note | text | 数据新鲜度说明 |
| pipeline_version | text | 生成版本 |
| generated_at | timestamptz | 生成时间 |
| created_at | timestamptz | 创建时间 |

### 索引建议

- unique(query_task_id)
- index(generated_at desc)

---

## 7.12 result_snapshot_clusters

### 用途

保存某个结果快照中的榜单结果顺序。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | 主键 |
| result_snapshot_id | uuid fk | 结果快照 |
| cluster_id | uuid fk | 需求聚类 |
| board_type | text | hot / growth / opportunity |
| rank_no | integer | 排名 |
| board_score | numeric(5,2) | 榜单分值 |
| tie_break_meta | jsonb | 并列裁决元数据 |
| created_at | timestamptz | 创建时间 |

### 约束建议

- unique(result_snapshot_id, board_type, rank_no)
- unique(result_snapshot_id, board_type, cluster_id)

### 索引建议

- index(result_snapshot_id, board_type, rank_no)
- index(cluster_id)

---

## 7.13 cluster_evidences

### 用途

保存需求聚类与证据的映射。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | evidence_id |
| cluster_id | uuid fk | 需求聚类 |
| source_type | text | post / comment |
| source_ref_id | text | 对应 source_post/source_comment 外部引用 |
| source_internal_id | uuid nullable | 若落关系库，可填内部 ID |
| excerpt | text | 摘录 |
| subreddit_name | text | 来源社区 |
| source_created_at | timestamptz | 来源时间 |
| stance | text | support / oppose / neutral |
| availability_status | text | public / removed / deleted / inaccessible |
| source_url | text nullable | 原帖跳转 |
| score_hint | numeric(10,2) nullable | 证据本身权重 |
| created_at | timestamptz | 创建时间 |

### 索引建议

- index(cluster_id)
- index(source_type, source_ref_id)
- index(stance)

---

## 7.14 export_jobs

### 用途

记录导出任务。

### 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid pk | 导出任务 ID |
| user_id | uuid fk nullable | 用户 |
| result_snapshot_id | uuid fk | 来源快照 |
| export_type | text | markdown / csv / feishu / notion |
| status | text | pending / running / success / failed |
| output_file_ref | text nullable | 对象存储路径 |
| failure_reason | text nullable | 失败原因 |
| created_at | timestamptz | 创建时间 |
| finished_at | timestamptz nullable | 完成时间 |

### 索引建议

- index(user_id, created_at desc)
- index(result_snapshot_id)
- index(status)

---

## 7.15 V1.5 预留表

以下表建议预留，但 V1 可不实际启用：

### saved_queries

- 保存查询配置

### alert_rules

- 订阅规则

### demand_library_items

- 需求库条目

---

## 8. 搜索索引设计建议

SourcePost 与 SourceComment 更适合放检索引擎。

## 8.1 posts_index

### 建议字段

- `internal_id`
- `reddit_post_id`
- `subreddit_name`
- `title`
- `body`
- `combined_text`
- `author_ref`
- `score`
- `comment_count`
- `created_at`
- `fetched_at`
- `language`
- `region_hints`
- `content_availability_status`
- `is_crosspost`
- `is_pinned`
- `is_nsfw`
- `raw_payload_ref`

### 索引建议

- title/body 全文检索
- subreddit_name keyword
- created_at range
- score 排序
- language keyword
- content_availability_status keyword

## 8.2 comments_index

### 建议字段

- `internal_id`
- `reddit_comment_id`
- `reddit_post_id`
- `parent_comment_id`
- `subreddit_name`
- `body`
- `author_ref`
- `score`
- `depth`
- `created_at`
- `fetched_at`
- `language`
- `region_hints`
- `content_availability_status`
- `raw_payload_ref`

### 索引建议

- body 全文检索
- reddit_post_id keyword
- subreddit_name keyword
- created_at range
- score 排序

## 8.3 是否需要向量字段

V1 可选：

- 若定向发现需要更强语义召回，可为 post/comment 增加 embedding 字段
- 若首版不引入向量检索，也不影响基本闭环

建议：

- 向量检索作为增强项，不应阻塞 V1 落地

---

## 9. 对象存储结构建议

## 9.1 原始数据

建议路径：

```text
raw/reddit/{date}/{subreddit}/{entity_type}/{external_id}.json
```

## 9.2 导出文件

建议路径：

```text
exports/{date}/{user_id_or_anonymous}/{export_job_id}.{ext}
```

## 9.3 中间产物

如需保存中间分析结果：

```text
pipeline/{date}/{query_task_id}/{stage}.json
```

---

## 10. 核心状态枚举建议

为避免接口与存储枚举漂移，建议统一。

## 10.1 query_tasks.status

- `pending`
- `running`
- `partial_success`
- `success`
- `failed`

## 10.2 demand_clusters.cluster_status

- `active`
- `merged`
- `split`
- `archived`

## 10.3 cluster_evidences.stance

- `support`
- `oppose`
- `neutral`

## 10.4 内容可用性状态

- `public`
- `removed`
- `deleted`
- `private`
- `banned`
- `inaccessible`
- `nsfw_excluded`

## 10.5 export_jobs.status

- `pending`
- `running`
- `success`
- `failed`

---

## 11. 关键索引与查询路径

## 11.1 常见查询路径

### 路径 A：通过 query_task_id 获取结果

1. `query_tasks`
2. `result_snapshots`
3. `result_snapshot_clusters`
4. `cluster_metric_snapshots`
5. `demand_clusters`
6. `cluster_evidences`

### 路径 B：通过 normalized_query_key 找缓存结果

1. 缓存层
2. 命中后回 `result_snapshot_id`
3. 读取结果快照

### 路径 C：需求详情页

1. `demand_clusters`
2. `cluster_metric_snapshots`
3. `cluster_evidences`
4. 来源检索索引补充更多上下文

## 11.2 关键索引清单

最关键的索引建议：

- `query_tasks(status, created_at)`
- `query_tasks(user_id, created_at desc)`
- `result_snapshot_clusters(result_snapshot_id, board_type, rank_no)`
- `cluster_metric_snapshots(cluster_id, window_end desc)`
- `cluster_evidences(cluster_id)`
- `topic_template_versions(template_id, version_no)`
- `subreddit_catalog(subreddit_name)`

---

## 12. 数据保留与归档建议

## 12.1 原始数据

- 原始 payload 可设置长期归档
- 若成本敏感，可冷热分层

## 12.2 任务日志

- `query_task_run_logs` 建议至少保留 90–180 天

## 12.3 结果快照

- 用户可见结果快照建议长期保留
- 若后续有成本压力，可对匿名快照设保留期

## 12.4 检索索引

- 检索索引可保留近一段时间热点数据
- 历史原始数据可以只保留在对象存储 + 冷归档中

---

## 13. V1 实施建议

## 13.1 关系库优先实现清单

V1 建议优先落以下表：

1. `users`
2. `topic_templates`
3. `topic_template_versions`
4. `topic_template_version_subreddits`
5. `subreddit_catalog`
6. `query_tasks`
7. `query_task_run_logs`
8. `demand_clusters`
9. `demand_cluster_aliases`
10. `cluster_metric_snapshots`
11. `result_snapshots`
12. `result_snapshot_clusters`
13. `cluster_evidences`
14. `export_jobs`

## 13.2 可先不做强规范化的部分

V1 可先通过 `jsonb` 放宽实现成本的字段：

- scenes
- pain_points
- alternatives
- sentiment_profile
- summary_stats
- min_engagement_threshold

## 13.3 不建议 V1 过早细拆的部分

以下内容首版不建议单独过细拆表：

- 痛点词表
- 场景词表
- 情绪词表
- 区域词表

首版可先使用 `jsonb`，等分析链路稳定后再考虑规范化。

---

## 14. 待确认事项

以下事项建议在进入详细 DDL 前确认：

1. 内部主键是否统一采用 UUID v7
2. 检索层是否首版就引入向量字段
3. `normalized_query_key` 是否做强唯一
4. 匿名查询结果是否长期保留
5. 收藏 / 需求库是否在 V1 直接上线
6. 导出是否允许匿名触发
7. 原始 payload 的保留周期
8. subreddit catalog 的维护策略

---

## 15. 一句话结论

V1 的数据模型核心，不是“存下所有 Reddit 内容”，而是：

> **围绕 QueryTask、DemandCluster、ResultSnapshot 三个核心对象，建立一套可追溯、可复现、可演进的结果型数据结构。**
