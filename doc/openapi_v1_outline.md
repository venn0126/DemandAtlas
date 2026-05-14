# Demand Atlas｜需见 OpenAPI V1 Outline

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 OpenAPI V1 Outline
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：OpenAPI 编写 / 后端接口实现 / 前后端联调 / SDK 生成准备
- 上游输入：
  - `doc/api_contract_draft.md`
  - `doc/domain_model_and_schema.md`
  - `doc/query_task_and_pipeline_design.md`

---

## 2. 文档目标

本文档不是完整 OpenAPI 文件，而是用于指导正式 OpenAPI 编写的结构化 Outline。

目标：

1. 固定 V1 资源与路径
2. 固定关键 request / response schema 名称
3. 固定 security、分页、错误结构
4. 为后续生成 `openapi.yaml` 提供直接蓝本

---

## 3. OpenAPI 顶层建议

建议正式 OpenAPI 顶层结构如下：

```yaml
openapi: 3.1.0
info:
  title: Reddit Needs Discovery API
  version: 1.0.0
  description: API for Reddit demand discovery service
servers:
  - url: https://api.example.com
security:
  - bearerAuth: []
paths: {}
components: {}
tags: []
```

---

## 4. Servers 建议

正式文档建议至少包含：

```yaml
servers:
  - url: https://api.example.com
    description: production
  - url: https://staging-api.example.com
    description: staging
```

---

## 5. Security Schemes 建议

## 5.1 Bearer Auth

用于登录用户访问。

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

## 5.2 Anonymous Query Token

用于匿名查询任务后续访问。

OpenAPI 中不必强行定义成标准 security scheme，也可以在参数层表达：

```yaml
parameters:
  AnonymousQueryAccessToken:
    name: X-Query-Access-Token
    in: header
    required: false
    schema:
      type: string
```

### 建议

- 登录用户使用 `Authorization`
- 匿名任务使用 `X-Query-Access-Token`
- 具体哪个接口允许匿名 token，应在 path 级别说明

---

## 6. Tags 建议

```yaml
tags:
  - name: TopicTemplates
  - name: QueryTasks
  - name: ResultSnapshots
  - name: DemandClusters
  - name: ExportJobs
```

---

## 7. 通用参数组件

## 7.1 PageSize

```yaml
PageSize:
  name: page_size
  in: query
  required: false
  schema:
    type: integer
    default: 20
    minimum: 1
    maximum: 100
```

## 7.2 PageToken

```yaml
PageToken:
  name: page_token
  in: query
  required: false
  schema:
    type: string
```

## 7.3 RequestId Header

若支持客户端透传 request id：

```yaml
ClientRequestId:
  name: X-Request-Id
  in: header
  required: false
  schema:
    type: string
```

## 7.4 Idempotency Key

```yaml
IdempotencyKey:
  name: Idempotency-Key
  in: header
  required: false
  schema:
    type: string
```

---

## 8. 通用响应结构组件

## 8.1 ApiEnvelope

正式 OpenAPI 中建议通过各接口分别绑定具体 data schema，而不是做全泛型。

可约定统一结构：

```yaml
ApiMeta:
  type: object
  properties:
    next_page_token:
      type: string
      nullable: true
    retry_after_ms:
      type: integer
      nullable: true

ApiError:
  type: object
  required: [code, message]
  properties:
    code:
      type: string
    message:
      type: string
    details:
      type: object
      additionalProperties: true

BaseResponse:
  type: object
  required: [request_id]
  properties:
    request_id:
      type: string
    meta:
      $ref: '#/components/schemas/ApiMeta'
    error:
      $ref: '#/components/schemas/ApiError'
```

### 实践建议

正式 schema 中：

- 每个 response 通过 `allOf` 组合 `BaseResponse`
- 然后加具体 `data`

---

## 9. 通用枚举组件

```yaml
QueryType:
  type: string
  enum: [one_click, directed]

ViewType:
  type: string
  enum: [active, new]

BoardType:
  type: string
  enum: [hot, growth, opportunity]

QueryTaskStatus:
  type: string
  enum: [pending, running, partial_success, success, failed]

ContentAvailabilityStatus:
  type: string
  enum: [public, removed, deleted, private, banned, inaccessible, nsfw_excluded]

ExportJobStatus:
  type: string
  enum: [pending, running, success, failed]
```

---

## 10. 核心 Schema 组件

以下是建议正式 OpenAPI 中定义的核心 schema。

## 10.1 TopicTemplateSummary

```yaml
TopicTemplateSummary:
  type: object
  required: [template_id, template_version_id, name, default_language, default_view_type]
  properties:
    template_id:
      type: string
    template_version_id:
      type: string
    name:
      type: string
    description:
      type: string
      nullable: true
    default_language:
      type: string
    default_view_type:
      $ref: '#/components/schemas/ViewType'
```

## 10.2 TimeWindow

```yaml
TimeWindow:
  type: object
  properties:
    preset:
      type: string
      enum: [7d, 30d, 90d]
    start_at:
      type: string
      format: date-time
    end_at:
      type: string
      format: date-time
```

### 说明

正式 schema 中可用 `oneOf` 区分：

- preset 模式
- 自定义 start/end 模式

## 10.3 QueryTaskSummary

```yaml
QueryTaskSummary:
  type: object
  required: [query_task_id, status]
  properties:
    query_task_id:
      type: string
    status:
      $ref: '#/components/schemas/QueryTaskStatus'
    result_snapshot_id:
      type: string
      nullable: true
    current_stage:
      type: string
      nullable: true
    coverage_note:
      type: string
      nullable: true
```

## 10.4 QueryProgress

```yaml
QueryProgress:
  type: object
  properties:
    current_step:
      type: integer
    total_steps:
      type: integer
    percent:
      type: integer
      minimum: 0
      maximum: 100
```

## 10.5 ResultSnapshotSummary

```yaml
ResultSnapshotSummary:
  type: object
  required:
    - result_snapshot_id
    - query_task_id
    - view_type
    - generated_at
  properties:
    result_snapshot_id:
      type: string
    query_task_id:
      type: string
    query_type:
      $ref: '#/components/schemas/QueryType'
    view_type:
      $ref: '#/components/schemas/ViewType'
    time_window:
      $ref: '#/components/schemas/ResolvedTimeWindow'
    generated_at:
      type: string
      format: date-time
    coverage_note:
      type: string
      nullable: true
    sync_freshness_note:
      type: string
      nullable: true
    summary_stats:
      $ref: '#/components/schemas/SummaryStats'
    available_boards:
      type: array
      items:
        $ref: '#/components/schemas/BoardType'
```

## 10.6 ResolvedTimeWindow

```yaml
ResolvedTimeWindow:
  type: object
  required: [start_at, end_at]
  properties:
    start_at:
      type: string
      format: date-time
    end_at:
      type: string
      format: date-time
```

## 10.7 SummaryStats

```yaml
SummaryStats:
  type: object
  properties:
    cluster_count:
      type: integer
    post_count:
      type: integer
    comment_count:
      type: integer
```

## 10.8 EvidenceSnippet

```yaml
EvidenceSnippet:
  type: object
  required: [evidence_id, excerpt, subreddit, created_at, availability_status]
  properties:
    evidence_id:
      type: string
    excerpt:
      type: string
    subreddit:
      type: string
    created_at:
      type: string
      format: date-time
    availability_status:
      $ref: '#/components/schemas/ContentAvailabilityStatus'
    source_url:
      type: string
      nullable: true
```

## 10.9 BoardEntry

```yaml
BoardEntry:
  type: object
  required:
    - rank
    - cluster_id
    - title
    - board_score
    - confidence_score
  properties:
    rank:
      type: integer
    cluster_id:
      type: string
    title:
      type: string
    summary:
      type: string
      nullable: true
    board_score:
      type: number
      format: float
    discussion_score:
      type: number
      format: float
      nullable: true
    attention_score:
      type: number
      format: float
      nullable: true
    growth_score:
      type: number
      format: float
      nullable: true
    opportunity_score:
      type: number
      format: float
      nullable: true
    confidence_score:
      type: number
      format: float
    post_count:
      type: integer
    comment_count:
      type: integer
    unique_user_count:
      type: integer
    is_weak_signal:
      type: boolean
    is_low_confidence:
      type: boolean
    is_emerging_signal:
      type: boolean
    top_subreddits:
      type: array
      items:
        type: string
    highlight_evidence:
      type: array
      items:
        $ref: '#/components/schemas/EvidenceSnippet'
```

## 10.10 DemandClusterDetail

```yaml
DemandClusterDetail:
  type: object
  required:
    - cluster_id
    - title
    - summary
    - time_window
    - flags
    - scores
    - metrics
  properties:
    cluster_id:
      type: string
    title:
      type: string
    summary:
      type: string
    time_window:
      $ref: '#/components/schemas/ResolvedTimeWindow'
    flags:
      $ref: '#/components/schemas/ClusterFlags'
    scores:
      $ref: '#/components/schemas/ClusterScores'
    metrics:
      $ref: '#/components/schemas/ClusterMetrics'
    scenes:
      type: array
      items:
        type: string
    pain_points:
      type: array
      items:
        type: string
    alternatives:
      type: array
      items:
        type: string
    supporting_evidence:
      type: array
      items:
        $ref: '#/components/schemas/EvidenceSnippet'
    opposing_evidence:
      type: array
      items:
        $ref: '#/components/schemas/EvidenceSnippet'
    top_subreddits:
      type: array
      items:
        type: string
    coverage_note:
      type: string
      nullable: true
```

## 10.11 ClusterFlags

```yaml
ClusterFlags:
  type: object
  properties:
    is_weak_signal:
      type: boolean
    is_low_confidence:
      type: boolean
    is_emerging_signal:
      type: boolean
```

## 10.12 ClusterScores

```yaml
ClusterScores:
  type: object
  properties:
    discussion_score:
      type: number
      format: float
      nullable: true
    attention_score:
      type: number
      format: float
      nullable: true
    growth_score:
      type: number
      format: float
      nullable: true
    opportunity_score:
      type: number
      format: float
      nullable: true
    confidence_score:
      type: number
      format: float
```

## 10.13 ClusterMetrics

```yaml
ClusterMetrics:
  type: object
  properties:
    post_count:
      type: integer
    comment_count:
      type: integer
    unique_user_count:
      type: integer
    community_spread_count:
      type: integer
```

## 10.14 ExportJobSummary

```yaml
ExportJobSummary:
  type: object
  required: [export_job_id, status]
  properties:
    export_job_id:
      type: string
    status:
      $ref: '#/components/schemas/ExportJobStatus'
    download_url:
      type: string
      nullable: true
    expires_at:
      type: string
      format: date-time
      nullable: true
```

---

## 11. 路径定义 Outline

## 11.1 GET /api/v1/topic-templates

### tag

- `TopicTemplates`

### summary

- List active topic templates

### parameters

- `status`
- `language`

### responses

- `200` -> list of `TopicTemplateSummary`
- `500` -> `ApiError`

---

## 11.2 GET /api/v1/topic-templates/{template_id}

### tag

- `TopicTemplates`

### path params

- `template_id`

### responses

- `200` -> topic template detail
- `404` -> `NOT_FOUND`

---

## 11.3 POST /api/v1/query-tasks

### tag

- `QueryTasks`

### security

- bearer 可选
- 匿名允许

### headers

- `Idempotency-Key`

### requestBody

建议使用 `oneOf`：

- `OneClickQueryTaskCreateRequest`
- `DirectedQueryTaskCreateRequest`

### response

#### 200

- cache hit

#### 202

- async accepted

#### 400 / 401 / 422 / 429 / 500

### schema 建议

#### OneClickQueryTaskCreateRequest

```yaml
OneClickQueryTaskCreateRequest:
  type: object
  required: [query_type, template_id, time_window]
  properties:
    query_type:
      type: string
      enum: [one_click]
    template_id:
      type: string
    template_version_id:
      type: string
      nullable: true
    view_type:
      $ref: '#/components/schemas/ViewType'
    time_window:
      $ref: '#/components/schemas/TimeWindow'
    force_refresh:
      type: boolean
      default: false
```

#### DirectedQueryTaskCreateRequest

```yaml
DirectedQueryTaskCreateRequest:
  type: object
  required: [query_type, keywords, time_window]
  properties:
    query_type:
      type: string
      enum: [directed]
    keywords:
      type: array
      minItems: 1
      maxItems: 5
      items:
        type: string
    subreddits:
      type: array
      maxItems: 20
      items:
        type: string
    language:
      type: string
      default: en
    region_hints:
      type: array
      items:
        type: string
    min_engagement_threshold:
      $ref: '#/components/schemas/MinEngagementThreshold'
    view_type:
      $ref: '#/components/schemas/ViewType'
    time_window:
      $ref: '#/components/schemas/TimeWindow'
    force_refresh:
      type: boolean
      default: false
```

#### MinEngagementThreshold

```yaml
MinEngagementThreshold:
  type: object
  properties:
    min_post_score:
      type: integer
      nullable: true
    min_comment_count:
      type: integer
      nullable: true
```

---

## 11.4 GET /api/v1/query-tasks/{query_task_id}

### tag

- `QueryTasks`

### security

- bearer 或 anonymous token

### params

- path: `query_task_id`
- header: `X-Query-Access-Token`（匿名时）

### responses

- `200` -> `QueryTaskStatusResponse`
- `401` / `403` / `404`

### schema 建议

```yaml
QueryTaskStatusResponseData:
  type: object
  required: [query_task_id, status]
  properties:
    query_task_id:
      type: string
    status:
      $ref: '#/components/schemas/QueryTaskStatus'
    current_stage:
      type: string
      nullable: true
    progress:
      $ref: '#/components/schemas/QueryProgress'
    result_snapshot_id:
      type: string
      nullable: true
    coverage_note:
      type: string
      nullable: true
    warnings:
      type: array
      items:
        $ref: '#/components/schemas/WarningItem'
```

#### WarningItem

```yaml
WarningItem:
  type: object
  required: [code, message]
  properties:
    code:
      type: string
    message:
      type: string
```

---

## 11.5 GET /api/v1/result-snapshots/{result_snapshot_id}

### tag

- `ResultSnapshots`

### security

- bearer 或 anonymous token

### responses

- `200` -> `ResultSnapshotSummary`
- `401` / `403` / `404`

---

## 11.6 GET /api/v1/result-snapshots/{result_snapshot_id}/boards/{board_type}

### tag

- `ResultSnapshots`

### path params

- `result_snapshot_id`
- `board_type`

### query params

- `page_size`
- `page_token`

### responses

- `200` -> paginated board entries
- `404`

### schema 建议

```yaml
BoardListResponseData:
  type: object
  required: [board_type, items]
  properties:
    board_type:
      $ref: '#/components/schemas/BoardType'
    items:
      type: array
      items:
        $ref: '#/components/schemas/BoardEntry'
```

---

## 11.7 GET /api/v1/result-snapshots/{result_snapshot_id}/clusters/{cluster_id}

### tag

- `DemandClusters`

### query params

- `evidence_page_size`
- `evidence_page_token`

### responses

- `200` -> `DemandClusterDetail`
- `404`

### 备注

若后续证据分页复杂度提升，可将 supporting / opposing evidence 拆成单独子接口。

---

## 11.8 POST /api/v1/export-jobs

### tag

- `ExportJobs`

### security

- bearer required

### requestBody

```yaml
ExportJobCreateRequest:
  type: object
  required: [result_snapshot_id, export_type]
  properties:
    result_snapshot_id:
      type: string
    export_type:
      type: string
      enum: [markdown, csv]
```

### responses

- `202` -> accepted export job
- `401` / `404` / `422`

---

## 11.9 GET /api/v1/export-jobs/{export_job_id}

### tag

- `ExportJobs`

### security

- bearer required

### responses

- `200` -> `ExportJobSummary`
- `401` / `403` / `404`

---

## 12. V1.5 预留路径

V1 可不实现，但建议在正式 OpenAPI 中预留 future section。

## 12.1 Saved Queries

```text
POST   /api/v1/saved-queries
GET    /api/v1/saved-queries
DELETE /api/v1/saved-queries/{saved_query_id}
```

## 12.2 Alert Rules

```text
POST   /api/v1/alert-rules
GET    /api/v1/alert-rules
PATCH  /api/v1/alert-rules/{alert_rule_id}
DELETE /api/v1/alert-rules/{alert_rule_id}
```

## 12.3 Demand Library

```text
POST   /api/v1/demand-library-items
GET    /api/v1/demand-library-items
PATCH  /api/v1/demand-library-items/{item_id}
```

---

## 13. 错误响应 Schema 建议

建议所有错误响应复用统一结构：

```yaml
ErrorResponse:
  allOf:
    - $ref: '#/components/schemas/BaseResponse'
    - type: object
      properties:
        data:
          nullable: true
        error:
          $ref: '#/components/schemas/ApiError'
```

### 常用错误码

- `INVALID_INPUT`
- `AUTH_REQUIRED`
- `ACCESS_DENIED`
- `NOT_FOUND`
- `RATE_LIMITED`
- `TEMPLATE_NOT_FOUND`
- `QUERY_TOO_BROAD`
- `NO_FETCHABLE_SOURCE`
- `NO_VALID_CANDIDATE`
- `CLUSTERING_FAILED`
- `SCORING_FAILED`
- `SNAPSHOT_PERSIST_FAILED`
- `TASK_TIMEOUT`
- `EXPORT_GENERATION_FAILED`

---

## 14. OpenAPI 编写建议

## 14.1 使用 oneOf 区分查询请求

`POST /query-tasks` 最适合使用 `oneOf`：

- `OneClickQueryTaskCreateRequest`
- `DirectedQueryTaskCreateRequest`

## 14.2 不建议过度泛型化 Envelope

OpenAPI 中完全泛型 Envelope 可读性较差。

建议：

- 重复定义少量响应 wrapper
- 保持 schema 清晰

## 14.3 统一 nullable 策略

正式文档要统一：

- `nullable: true`
- 或 OpenAPI 3.1 的 `type: [string, "null"]`

不要混用得太散。

## 14.4 统一字段命名

建议：

- 全部使用 `snake_case`
- 与数据库内部命名可不同，但 API 层保持一致

## 14.5 分页 token 透明化

前端不应解析 `next_page_token`，仅透传使用。

---

## 15. 与前端状态流的关键对应关系

| API | 前端页面 |
|---|---|
| `POST /query-tasks` | 一键发现页 / 定向发现页提交 |
| `GET /query-tasks/{id}` | 查询任务页轮询 |
| `GET /result-snapshots/{id}` | 结果页头部 |
| `GET /result-snapshots/{id}/boards/{board_type}` | 榜单列表 |
| `GET /result-snapshots/{id}/clusters/{cluster_id}` | 详情页 |
| `POST /export-jobs` | 结果页 / 详情页导出 |
| `GET /export-jobs/{id}` | 导出状态查询 |

---

## 16. 正式 OpenAPI 文件推荐拆分

为便于维护，建议最终按文件拆分：

```text
openapi/
  openapi.yaml
  paths/
    topic_templates.yaml
    query_tasks.yaml
    result_snapshots.yaml
    export_jobs.yaml
  schemas/
    common.yaml
    query_tasks.yaml
    result_snapshots.yaml
    clusters.yaml
    export_jobs.yaml
```

---

## 17. 推荐下一步产出

基于本文档，建议继续输出：

1. `doc/frontend_state_management_notes.md`
2. `doc/openapi_example_responses.md`
3. 正式 `openapi/openapi.yaml`

---

## 18. 一句话结论

V1 OpenAPI 设计的关键，不是追求“接口很多”，而是：

> **用最少的一组资源，把 QueryTask -> ResultSnapshot -> Cluster Detail 的主链路稳定表达出来。**
