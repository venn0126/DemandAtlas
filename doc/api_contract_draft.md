# Demand Atlas｜需见 API Contract Draft

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 API Contract Draft
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：前后端联调设计 / 后端接口设计 / BFF 设计 / 技术评审
- 上游输入：
  - `doc/prd_reddit_needs_discovery.md`
  - `doc/technical_architecture_input.md`
  - `doc/domain_model_and_schema.md`
  - `doc/query_task_and_pipeline_design.md`

---

## 2. 文档目标

本文档用于定义 V1 阶段的 API 草案，包括：

1. 资源模型
2. 核心接口
3. 请求与响应结构
4. 异步任务协议
5. 错误码与状态码约定
6. V1 与 V1.5 的接口边界

### 2.1 本文档不覆盖

- 最终 OpenAPI 文件
- GraphQL 方案
- 最终鉴权实现细节
- 最终 SDK 设计

---

## 3. API 设计原则

## 3.1 结果快照优先

所有查询结果的读取，都优先围绕 `ResultSnapshot` 展开。

即：

- 创建查询 -> 返回 `query_task_id`
- 查询完成 -> 产生 `result_snapshot_id`
- 榜单 / 详情 / 导出 -> 基于 `result_snapshot_id` 读取

## 3.2 异步优先，缓存加速

- 常见查询命中缓存时可直接返回结果快照
- 新查询或重查询默认进入异步任务

## 3.3 面向资源设计

V1 API 核心资源：

- topic template
- query task
- result snapshot
- board result
- demand cluster detail
- export job

## 3.4 匿名可查询，写操作需登录

V1 建议：

- 匿名用户可以发起基础查询
- 匿名用户可以查询自己刚创建任务的状态与结果
- 收藏 / 保存 / 订阅 / 第三方导出等写能力需要登录

## 3.5 API 响应可解释

响应中应尽量带上：

- request_id
- status
- 当前 stage
- coverage_note
- low_confidence / weak_signal 等解释标签

---

## 4. 协议与通用约定

## 4.1 基本协议

- 风格：REST + JSON
- Base path：`/api/v1`
- Content-Type：`application/json`
- 时间格式：ISO 8601, UTC

## 4.2 认证方式

V1 建议支持两种访问模式：

### A. 登录态访问

通过标准用户鉴权访问受保护资源。

建议请求头：

```text
Authorization: Bearer <user_access_token>
```

### B. 匿名任务访问

匿名创建查询任务后，服务端返回一个临时访问 token，用于后续查询该任务状态和结果。

建议请求头：

```text
X-Query-Access-Token: <anonymous_query_access_token>
```

### 说明

这样可以避免匿名用户仅凭 `query_task_id` 猜测和读取他人任务。

## 4.3 幂等头

创建类接口建议支持：

```text
Idempotency-Key: <client_generated_key>
```

适用接口：

- `POST /query-tasks`
- `POST /export-jobs`

## 4.4 分页约定

V1 草案建议使用 cursor 分页。

通用参数：

- `page_size`
- `page_token`

通用响应：

- `next_page_token`

### 默认值建议

- `page_size` 默认 20
- `page_size` 最大 100

## 4.5 响应包裹结构

建议统一返回格式：

```json
{
  "request_id": "req_123",
  "data": {},
  "meta": {},
  "error": null
}
```

失败响应：

```json
{
  "request_id": "req_123",
  "data": null,
  "meta": {},
  "error": {
    "code": "INVALID_INPUT",
    "message": "time range exceeds limit",
    "details": {}
  }
}
```

---

## 5. 核心枚举定义

## 5.1 query_type

- `one_click`
- `directed`

## 5.2 view_type

- `active`
- `new`

## 5.3 board_type

- `hot`
- `growth`
- `opportunity`

## 5.4 query_task.status

- `pending`
- `running`
- `partial_success`
- `success`
- `failed`

## 5.5 content_availability_status

- `public`
- `removed`
- `deleted`
- `private`
- `banned`
- `inaccessible`
- `nsfw_excluded`

## 5.6 cluster flags

- `is_weak_signal`
- `is_low_confidence`
- `is_emerging_signal`

---

## 6. 核心资源概览

| 资源 | 说明 |
|---|---|
| TopicTemplate | 一键发现模板 |
| QueryTask | 查询任务 |
| ResultSnapshot | 查询结果快照 |
| BoardEntry | 榜单条目 |
| DemandClusterDetail | 需求详情 |
| EvidenceSnippet | 原话证据 |
| ExportJob | 导出任务 |

---

## 7. Topic Template 相关接口

## 7.1 获取可用主题模板列表

### Endpoint

`GET /api/v1/topic-templates`

### 用途

一键发现页加载可用模板。

### Query 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| status | string | 否 | 默认 `active` |
| language | string | 否 | 按语言过滤 |

### Response 示例

```json
{
  "request_id": "req_x1",
  "data": {
    "items": [
      {
        "template_id": "tpl_ai_tools",
        "template_version_id": "tplv_001",
        "name": "AI Tools",
        "description": "AI productivity and tooling",
        "default_language": "en",
        "default_view_type": "active"
      }
    ]
  },
  "meta": {},
  "error": null
}
```

## 7.2 获取主题模板详情

### Endpoint

`GET /api/v1/topic-templates/{template_id}`

### 用途

用于一键发现页查看模板详情。

### Response 重点字段

- `template_id`
- `template_version_id`
- `name`
- `description`
- `default_language`
- `default_view_type`
- `candidate_subreddit_count`

### 说明

V1 不建议把模板内部完整关键词与排除词全部暴露给前端，避免后续配置耦合过深。

---

## 8. Query Task 相关接口

## 8.1 创建查询任务

### Endpoint

`POST /api/v1/query-tasks`

### 用途

发起一键发现或定向发现任务。

### 请求体结构

```json
{
  "query_type": "one_click",
  "template_id": "tpl_ai_tools",
  "template_version_id": "tplv_001",
  "view_type": "active",
  "time_window": {
    "preset": "30d"
  },
  "force_refresh": false
}
```

或：

```json
{
  "query_type": "directed",
  "keywords": ["wired earbuds", "corded earphones"],
  "subreddits": ["Earbuds", "HeadphoneAdvice"],
  "language": "en",
  "region_hints": ["US"],
  "view_type": "active",
  "time_window": {
    "start_at": "2026-04-01T00:00:00Z",
    "end_at": "2026-05-01T00:00:00Z"
  },
  "min_engagement_threshold": {
    "min_post_score": 5,
    "min_comment_count": 3
  },
  "force_refresh": false
}
```

### 请求字段说明

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| query_type | string | 是 | `one_click` / `directed` |
| template_id | string | 条件必填 | 一键发现必填 |
| template_version_id | string | 否 | 不传则默认当前 active 版本 |
| keywords | string[] | 条件必填 | 定向发现必填 |
| subreddits | string[] | 否 | 定向发现可选 |
| language | string | 否 | 默认 `en` |
| region_hints | string[] | 否 | 地域线索 |
| view_type | string | 否 | 默认 `active` |
| time_window | object | 是 | preset 或 start/end |
| min_engagement_threshold | object | 否 | 最低互动门槛 |
| force_refresh | boolean | 否 | 默认 false |

### 响应场景 A：命中缓存

HTTP 200

```json
{
  "request_id": "req_x2",
  "data": {
    "execution_mode": "cache_hit",
    "query_task_id": "qt_001",
    "status": "success",
    "result_snapshot_id": "rs_001",
    "cached": true
  },
  "meta": {},
  "error": null
}
```

### 响应场景 B：创建异步任务

HTTP 202

```json
{
  "request_id": "req_x3",
  "data": {
    "execution_mode": "async",
    "query_task_id": "qt_002",
    "status": "pending",
    "poll_url": "/api/v1/query-tasks/qt_002",
    "anonymous_query_access_token": "anon_tok_xxx"
  },
  "meta": {
    "retry_after_ms": 1500
  },
  "error": null
}
```

### 错误码建议

- `INVALID_INPUT`
- `QUERY_TOO_BROAD`
- `TEMPLATE_NOT_FOUND`
- `TEMPLATE_NOT_ACTIVE`
- `AUTH_REQUIRED`
- `RATE_LIMITED`

### 说明

- `view_type` 切换本质上是不同 QueryTask
- 前端切换 active/new 时，应复用同条件参数重新请求创建或命中缓存

## 8.2 获取查询任务状态

### Endpoint

`GET /api/v1/query-tasks/{query_task_id}`

### 用途

轮询异步任务状态。

### 请求头

登录用户：

```text
Authorization: Bearer <token>
```

匿名用户：

```text
X-Query-Access-Token: <anonymous_query_access_token>
```

### Response 示例

```json
{
  "request_id": "req_x4",
  "data": {
    "query_task_id": "qt_002",
    "status": "running",
    "current_stage": "cluster",
    "progress": {
      "current_step": 6,
      "total_steps": 8,
      "percent": 72
    },
    "result_snapshot_id": null,
    "coverage_note": null,
    "warnings": []
  },
  "meta": {},
  "error": null
}
```

### Response 示例：partial_success

```json
{
  "request_id": "req_x5",
  "data": {
    "query_task_id": "qt_002",
    "status": "partial_success",
    "current_stage": "snapshot",
    "progress": {
      "current_step": 8,
      "total_steps": 8,
      "percent": 100
    },
    "result_snapshot_id": "rs_002",
    "coverage_note": "2 candidate subreddits failed during fetch",
    "warnings": [
      {
        "code": "PARTIAL_FETCH_FAILURE",
        "message": "some subreddit data was unavailable"
      }
    ]
  },
  "meta": {},
  "error": null
}
```

### Response 示例：failed

```json
{
  "request_id": "req_x6",
  "data": {
    "query_task_id": "qt_002",
    "status": "failed",
    "current_stage": "fetch",
    "result_snapshot_id": null,
    "coverage_note": null
  },
  "meta": {},
  "error": {
    "code": "NO_FETCHABLE_SOURCE",
    "message": "unable to fetch any valid source data",
    "details": {}
  }
}
```

## 8.3 获取查询任务执行日志（可选调试接口）

### Endpoint

`GET /api/v1/query-tasks/{query_task_id}/run-logs`

### 用途

内部调试或管理后台查看任务阶段日志。

### 说明

V1 面向普通用户可不开放，建议内部管理端使用。

---

## 9. Result Snapshot 相关接口

## 9.1 获取结果快照摘要

### Endpoint

`GET /api/v1/result-snapshots/{result_snapshot_id}`

### 用途

加载结果页顶部摘要与全局状态。

### Response 示例

```json
{
  "request_id": "req_x7",
  "data": {
    "result_snapshot_id": "rs_001",
    "query_task_id": "qt_001",
    "query_type": "directed",
    "view_type": "active",
    "time_window": {
      "start_at": "2026-04-01T00:00:00Z",
      "end_at": "2026-05-01T00:00:00Z"
    },
    "generated_at": "2026-05-12T09:00:00Z",
    "coverage_note": "full coverage on candidate sources",
    "sync_freshness_note": "latest source sync at 2026-05-12T08:40:00Z",
    "summary_stats": {
      "cluster_count": 18,
      "post_count": 236,
      "comment_count": 1943
    },
    "available_boards": ["hot", "growth", "opportunity"]
  },
  "meta": {},
  "error": null
}
```

## 9.2 获取榜单列表

### Endpoint

`GET /api/v1/result-snapshots/{result_snapshot_id}/boards/{board_type}`

### Path 参数

| 参数 | 说明 |
|---|---|
| board_type | `hot` / `growth` / `opportunity` |

### Query 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| page_size | integer | 否 | 默认 20，最大 100 |
| page_token | string | 否 | 分页 token |

### Response 示例

```json
{
  "request_id": "req_x8",
  "data": {
    "board_type": "hot",
    "items": [
      {
        "rank": 1,
        "cluster_id": "clu_001",
        "title": "Users still prefer wired earbuds for reliability",
        "summary": "Users repeatedly mention reliability, no charging anxiety, and low latency.",
        "board_score": 87.2,
        "discussion_score": 82.0,
        "attention_score": 79.5,
        "growth_score": 41.0,
        "opportunity_score": 73.0,
        "confidence_score": 88.0,
        "post_count": 12,
        "comment_count": 143,
        "unique_user_count": 56,
        "is_weak_signal": false,
        "is_low_confidence": false,
        "is_emerging_signal": false,
        "top_subreddits": ["Earbuds", "HeadphoneAdvice"],
        "highlight_evidence": [
          {
            "excerpt": "Wired just works.",
            "subreddit": "Earbuds",
            "source_url": "https://reddit.com/..."
          }
        ]
      }
    ]
  },
  "meta": {
    "next_page_token": null
  },
  "error": null
}
```

### 说明

- 榜单条目建议返回“轻详情”
- 详情页需要再请求 cluster detail 接口

## 9.3 获取需求详情

### Endpoint

`GET /api/v1/result-snapshots/{result_snapshot_id}/clusters/{cluster_id}`

### 用途

加载需求详情页。

### Query 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| evidence_page_size | integer | 否 | 默认 20 |
| evidence_page_token | string | 否 | 证据分页 |

### Response 示例

```json
{
  "request_id": "req_x9",
  "data": {
    "cluster_id": "clu_001",
    "title": "Users still prefer wired earbuds for reliability",
    "summary": "In the last 30 days, users repeatedly discussed stability, lower latency, and no charging overhead.",
    "time_window": {
      "start_at": "2026-04-01T00:00:00Z",
      "end_at": "2026-05-01T00:00:00Z"
    },
    "flags": {
      "is_weak_signal": false,
      "is_low_confidence": false,
      "is_emerging_signal": false
    },
    "scores": {
      "discussion_score": 82.0,
      "attention_score": 79.5,
      "growth_score": 41.0,
      "opportunity_score": 73.0,
      "confidence_score": 88.0
    },
    "metrics": {
      "post_count": 12,
      "comment_count": 143,
      "unique_user_count": 56,
      "community_spread_count": 4
    },
    "scenes": ["commuting", "gaming", "video editing"],
    "pain_points": [
      "bluetooth instability",
      "charging burden",
      "higher latency"
    ],
    "alternatives": ["wireless earbuds", "budget bluetooth headsets"],
    "supporting_evidence": [
      {
        "evidence_id": "ev_001",
        "excerpt": "Wired just works.",
        "subreddit": "Earbuds",
        "created_at": "2026-04-22T09:00:00Z",
        "availability_status": "public",
        "source_url": "https://reddit.com/..."
      }
    ],
    "opposing_evidence": [
      {
        "evidence_id": "ev_002",
        "excerpt": "Cables break too often for me.",
        "subreddit": "HeadphoneAdvice",
        "created_at": "2026-04-25T12:00:00Z",
        "availability_status": "public",
        "source_url": "https://reddit.com/..."
      }
    ],
    "top_subreddits": ["Earbuds", "HeadphoneAdvice"],
    "coverage_note": "full coverage on candidate sources"
  },
  "meta": {
    "evidence_next_page_token": null
  },
  "error": null
}
```

## 9.4 获取结果快照下的聚类列表（可选）

### Endpoint

`GET /api/v1/result-snapshots/{result_snapshot_id}/clusters`

### 用途

供管理台或高级筛选页使用。

### 说明

V1 前台未必需要，但后端可以预留。

---

## 10. Export Job 相关接口

## 10.1 创建导出任务

### Endpoint

`POST /api/v1/export-jobs`

### 鉴权

建议需要登录。

### 请求体示例

```json
{
  "result_snapshot_id": "rs_001",
  "export_type": "markdown"
}
```

### 请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| result_snapshot_id | string | 是 | 来源快照 |
| export_type | string | 是 | `markdown` / `csv` |

### Response 示例

HTTP 202

```json
{
  "request_id": "req_x10",
  "data": {
    "export_job_id": "exp_001",
    "status": "pending",
    "poll_url": "/api/v1/export-jobs/exp_001"
  },
  "meta": {},
  "error": null
}
```

## 10.2 获取导出任务状态

### Endpoint

`GET /api/v1/export-jobs/{export_job_id}`

### Response 示例

```json
{
  "request_id": "req_x11",
  "data": {
    "export_job_id": "exp_001",
    "status": "success",
    "download_url": "https://storage.example.com/exports/exp_001.md",
    "expires_at": "2026-05-13T09:00:00Z"
  },
  "meta": {},
  "error": null
}
```

### 错误码建议

- `AUTH_REQUIRED`
- `EXPORT_TYPE_UNSUPPORTED`
- `RESULT_SNAPSHOT_NOT_FOUND`
- `EXPORT_GENERATION_FAILED`

---

## 11. V1.5 预留接口

以下接口建议预留，但 V1 可不实现：

## 11.1 Saved Query

- `POST /api/v1/saved-queries`
- `GET /api/v1/saved-queries`
- `DELETE /api/v1/saved-queries/{id}`

## 11.2 Alert Rule

- `POST /api/v1/alert-rules`
- `GET /api/v1/alert-rules`
- `PATCH /api/v1/alert-rules/{id}`
- `DELETE /api/v1/alert-rules/{id}`

## 11.3 Demand Library

- `POST /api/v1/demand-library-items`
- `GET /api/v1/demand-library-items`
- `PATCH /api/v1/demand-library-items/{id}`

---

## 12. 错误码设计建议

## 12.1 通用错误码

| code | 含义 |
|---|---|
| INVALID_INPUT | 输入不合法 |
| AUTH_REQUIRED | 需要登录 |
| ACCESS_DENIED | 无权访问 |
| NOT_FOUND | 资源不存在 |
| RATE_LIMITED | 触发限流 |
| SYSTEM_ERROR | 系统错误 |

## 12.2 查询相关错误码

| code | 含义 |
|---|---|
| TEMPLATE_NOT_FOUND | 模板不存在 |
| TEMPLATE_NOT_ACTIVE | 模板不可用 |
| QUERY_TOO_BROAD | 查询范围过大 |
| UNSUPPORTED_LANGUAGE | 不支持该语言 |
| TIME_RANGE_EXCEEDED | 时间范围超限 |
| NO_FETCHABLE_SOURCE | 无法获取可用源数据 |
| NO_VALID_CANDIDATE | 无法形成有效候选内容 |
| CLUSTERING_FAILED | 聚类失败 |
| SCORING_FAILED | 评分失败 |
| SNAPSHOT_PERSIST_FAILED | 快照持久化失败 |
| TASK_TIMEOUT | 任务超时 |

## 12.3 导出相关错误码

| code | 含义 |
|---|---|
| EXPORT_TYPE_UNSUPPORTED | 不支持的导出类型 |
| EXPORT_GENERATION_FAILED | 导出生成失败 |

---

## 13. HTTP 状态码建议

| HTTP 状态码 | 说明 |
|---|---|
| 200 | 请求成功 |
| 201 | 资源已创建 |
| 202 | 任务已受理，异步处理中 |
| 400 | 参数错误 |
| 401 | 未认证 |
| 403 | 已认证但无权访问 |
| 404 | 资源不存在 |
| 409 | 资源状态冲突 |
| 422 | 语义合法但业务不可执行 |
| 429 | 限流 |
| 500 | 系统内部错误 |

### 建议用法

- 创建新 QueryTask：缓存命中时可 200，异步受理时 202
- 创建导出任务：202

---

## 14. API 与状态流的关键约束

## 14.1 active / new 视角切换

V1 建议：

- 不在同一个 `result_snapshot_id` 内混放两种视角
- active/new 切换视为另一条查询路径
- 前端通过相同条件 + 不同 `view_type` 发起或命中另一条 QueryTask

## 14.2 结果读取一律基于 result_snapshot_id

建议避免：

- 直接通过 query 条件重新实时计算详情页

应采用：

- 先通过 QueryTask 获取 `result_snapshot_id`
- 再通过 `result_snapshot_id` 读榜单和详情

## 14.3 匿名访问控制

匿名模式下：

- 创建查询时返回 `anonymous_query_access_token`
- 后续状态、快照、详情读取需附带该 token
- 导出建议不对匿名用户开放

## 14.4 低置信度与样本不足透传

接口必须显式透传：

- `is_weak_signal`
- `is_low_confidence`
- `is_emerging_signal`
- `coverage_note`

避免前端自行推断。

---

## 15. 前后端联调重点

联调阶段优先确认以下问题：

1. 创建查询时缓存命中 / 异步任务两种返回是否能被前端统一处理
2. 轮询频率与超时策略
3. `partial_success` 页面如何展示
4. 榜单默认分页与“查看更多”交互
5. 详情页证据分页是否需要首版开放
6. 匿名 token 如何保存与续用

---

## 16. 推荐下一步产出

基于本文档，建议继续输出：

1. `doc/information_architecture_and_state_flow.md`
2. `doc/scoring_engine_design.md`
3. `doc/openapi_v1_outline.md`

---

## 17. 一句话结论

V1 API 的核心，不是“开放很多接口”，而是：

> **围绕 QueryTask 和 ResultSnapshot，建立一套对异步查询友好、对前端状态友好、对结果复现友好的最小接口集合。**
