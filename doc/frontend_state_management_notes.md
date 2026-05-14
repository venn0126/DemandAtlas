# Demand Atlas｜需见 前端状态管理说明

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 前端状态管理说明
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：前端架构设计 / 页面实现 / 状态管理实现 / 联调设计
- 上游输入：
  - `doc/information_architecture_and_state_flow.md`
  - `doc/api_contract_draft.md`
  - `doc/query_task_and_pipeline_design.md`

---

## 2. 文档目标

本文档用于定义前端状态层如何承接：

- QueryTask 异步查询
- ResultSnapshot 快照读取
- 榜单与详情联动
- 匿名查询 token
- 导出任务状态

本文档重点解决：

1. 前端应该存哪些状态
2. 哪些状态来自服务端，哪些状态只存在本地
3. 如何处理轮询、刷新、切换视角、切换榜单
4. 如何避免状态打架与页面漂移

---

## 3. 状态管理原则

## 3.1 服务端为真源

以下状态以服务端为准：

- QueryTask 状态
- ResultSnapshot 内容
- 榜单排序结果
- DemandCluster 详情
- ExportJob 状态

前端不自行推导这些核心业务状态。

## 3.2 本地只存 UI 与输入态

以下状态适合前端本地维护：

- 当前输入中的表单值
- 当前选中的 board type
- 当前展开的 UI 组件
- 页面级 loading 状态

## 3.3 快照上下文不可丢

一旦进入结果页，页面上下文必须绑定：

- `result_snapshot_id`
- `view_type`
- `query_task_id`（可选保留）

避免详情页脱离当前结果快照去取“最新结果”。

## 3.4 匿名任务要可恢复

匿名用户创建查询后：

- 前端需要持久化 `query_task_id`
- 持久化 `anonymous_query_access_token`

否则刷新页面后无法继续访问任务结果。

## 3.5 刷新不应隐式重跑

页面刷新后应恢复快照与任务状态，不应默认重新创建 QueryTask。

---

## 4. 状态分层建议

建议将前端状态拆成 6 层：

1. 会话层
2. 输入层
3. 任务层
4. 结果层
5. 导出层
6. UI 层

---

## 5. 会话层状态

## 5.1 authSession

### 作用

记录登录态用户信息。

### 建议字段

- `user`
- `access_token`
- `is_authenticated`
- `auth_loading`

## 5.2 anonymousQuerySession

### 作用

记录匿名查询任务访问凭据。

### 建议字段

- `query_task_id`
- `anonymous_query_access_token`
- `created_at`
- `expires_at`（若后端提供）

### 持久化建议

- `sessionStorage` 优先
- key 可设计为：

```text
anon_query_session:{query_task_id}
```

### 说明

- 匿名 token 不建议长期保存在 localStorage
- 同一浏览器会话内恢复即可

---

## 6. 输入层状态

输入层建议按页面拆分。

## 6.1 oneClickQueryForm

### 建议字段

- `template_id`
- `template_version_id`
- `time_window`
- `view_type`
- `force_refresh`

### 本地状态

- `is_submitting`
- `validation_errors`
- `warnings`

## 6.2 directedQueryForm

### 建议字段

- `keywords`
- `subreddits`
- `language`
- `region_hints`
- `time_window`
- `min_engagement_threshold`
- `view_type`
- `force_refresh`

### 本地状态

- `is_submitting`
- `validation_errors`
- `warnings`

## 6.3 输入层持久化建议

建议：

- 草稿输入保留在内存
- 如需提升体验，可对最近一次查询条件做 session 级缓存

不建议：

- 默认对所有未提交输入做长期持久化

---

## 7. 任务层状态

## 7.1 taskRuntimeStore

### 作用

管理 QueryTask 生命周期和轮询状态。

### 建议字段

- `current_query_task_id`
- `status`
- `current_stage`
- `progress`
- `result_snapshot_id`
- `coverage_note`
- `warnings`
- `last_polled_at`
- `polling_enabled`

## 7.2 数据来源

全部来自：

- `GET /api/v1/query-tasks/{query_task_id}`

## 7.3 轮询策略

建议：

- `pending` / `running` 时轮询
- `partial_success` / `success` / `failed` 时停止轮询

### 轮询间隔建议

- 默认 1.5s–3s
- 可按阶段动态退避

### 推荐策略

```text
初始 1.5s
若连续 3 次仍 running -> 3s
若页面失焦 -> 5s 或暂停
```

## 7.4 页面刷新恢复

如果当前 URL 中有 `query_task_id`：

- 前端应尝试恢复任务状态
- 若匿名任务则读取匿名 token

---

## 8. 结果层状态

结果层建议以 `result_snapshot_id` 为主键组织。

## 8.1 resultSnapshotStore

### 建议字段

- `active_result_snapshot_id`
- `result_snapshot_map`

其中 `result_snapshot_map[result_snapshot_id]` 可包含：

- `summary`
- `boards`
- `detail_cache`
- `fetched_at`

## 8.2 summary 状态

来自：

- `GET /api/v1/result-snapshots/{result_snapshot_id}`

建议字段：

- `query_type`
- `view_type`
- `time_window`
- `generated_at`
- `coverage_note`
- `sync_freshness_note`
- `summary_stats`
- `available_boards`

## 8.3 boards 状态

建议结构：

```text
boards[result_snapshot_id][board_type] = {
  items,
  next_page_token,
  loading,
  loaded
}
```

### 数据来源

- `GET /api/v1/result-snapshots/{result_snapshot_id}/boards/{board_type}`

## 8.4 detail_cache 状态

建议结构：

```text
detail_cache[result_snapshot_id][cluster_id] = {
  data,
  loading,
  loaded
}
```

### 数据来源

- `GET /api/v1/result-snapshots/{result_snapshot_id}/clusters/{cluster_id}`

## 8.5 缓存策略

前端结果缓存可用来：

- 减少同 session 内重复请求
- 支持返回榜单时快速恢复

### 建议

- 内存缓存为主
- URL 驱动上下文恢复

### 不建议

- 把完整结果快照长期放本地持久化

---

## 9. 导出层状态

## 9.1 exportJobStore

### 建议字段

- `export_job_map`
- `active_export_job_id`

### export_job_map 结构

- `status`
- `result_snapshot_id`
- `export_type`
- `download_url`
- `expires_at`
- `last_polled_at`

## 9.2 状态流

```text
点击导出
  -> 创建 ExportJob
  -> 进入 pending/running
  -> 轮询 export job
  -> success / failed
```

## 9.3 UX 建议

- 导出中不应阻塞浏览结果页
- success 后显示下载入口

---

## 10. UI 层状态

UI 层状态只负责展示，不承载核心业务真值。

## 10.1 建议包含

- 当前选中的 `board_type`
- 当前选中的详情 tab
- 当前是否展示帮助说明
- 当前 toast / banner
- 当前 modal 状态

## 10.2 不建议包含

不建议 UI 层自己维护：

- QueryTask 是否成功
- 哪个 cluster 是低置信度
- coverage 是否部分成功

这些应完全来自服务端返回。

---

## 11. 路由状态设计建议

## 11.1 推荐路由结构

```text
/
/discover/one-click
/discover/directed
/tasks/:queryTaskId
/results/:resultSnapshotId
/results/:resultSnapshotId/boards/:boardType
/results/:resultSnapshotId/clusters/:clusterId
/settings
```

### 说明

- `boardType` 可选放 querystring 或 path
- 为了可分享与恢复，`resultSnapshotId` 应在 URL 中显式存在

## 11.2 querystring 建议

结果页可使用：

```text
?view=active
?source=queryTask
```

但不建议把完整查询条件全放在 URL 中。

## 11.3 URL 与状态同步原则

### URL 应表达

- 当前页面资源身份
- 当前结果快照身份
- 当前榜单或详情上下文

### URL 不应表达

- 全量缓存数据
- 匿名 token

匿名 token 应保存在 sessionStorage，而不是 URL。

---

## 12. 页面级状态恢复策略

## 12.1 查询任务页刷新恢复

前提：

- URL 有 `query_task_id`
- 本地有对应匿名 token 或用户已登录

恢复流程：

1. 读取 URL
2. 读取访问凭据
3. 重新请求 task status
4. 根据状态恢复页面

## 12.2 结果页刷新恢复

前提：

- URL 有 `result_snapshot_id`

恢复流程：

1. 拉取 snapshot summary
2. 拉取默认榜单
3. 若 URL 指向具体 board 或 detail，则继续拉取对应资源

## 12.3 详情页刷新恢复

前提：

- URL 有 `result_snapshot_id + cluster_id`

恢复流程：

1. 拉取 snapshot summary（可选）
2. 拉取 cluster detail

---

## 13. 关键交互与状态机建议

## 13.1 创建查询交互状态机

```text
idle
  -> validating
  -> submitting
  -> cache_hit_success
  -> async_task_created
  -> submit_failed
```

## 13.2 查询任务页状态机

```text
pending
  -> running
  -> partial_success
  -> success
  -> failed
```

## 13.3 结果页状态机

```text
loading_summary
  -> loading_board
  -> ready
  -> no_result
  -> weak_signal
  -> low_confidence
  -> partial_success_note
  -> load_failed
```

### 注意

这些状态可以并存：

- `ready + partial_success_note`
- `ready + low_confidence`
- `ready + weak_signal`

因此前端不应把它们当互斥大状态。

---

## 14. 推荐技术实现方式

以下仅为建议，不是强约束。

## 14.1 数据请求层

建议使用：

- 具备请求缓存、轮询、错误重试能力的 query 库

例如：

- TanStack Query

## 14.2 本地 UI 状态层

建议使用：

- 轻量 store 管理 UI 与跨页状态

例如：

- Zustand
- Redux Toolkit

## 14.3 推荐职责分离

### Query 库管理

- 服务端真值
- 异步请求
- 请求缓存

### 本地 store 管理

- 当前表单输入
- 匿名 token
- 轻量 UI 状态

---

## 15. 轮询与失焦策略

## 15.1 页面聚焦时

- 正常轮询 QueryTask / ExportJob

## 15.2 页面失焦时

建议：

- QueryTask 轮询降频
- ExportJob 轮询降频

## 15.3 页面隐藏过久恢复

当页面重新聚焦：

- 应立即主动刷新一次 task / export 状态

---

## 16. 匿名 token 持久化与清理策略

## 16.1 持久化建议

保存在：

- `sessionStorage`

结构建议：

```json
{
  "query_task_id": "qt_001",
  "anonymous_query_access_token": "anon_xxx",
  "created_at": "2026-05-12T09:00:00Z"
}
```

## 16.2 清理策略

建议在以下情况清理：

- 用户主动退出当前匿名任务
- 任务已过有效期
- 浏览器会话结束

## 16.3 不建议

- 把 token 放到 URL
- 把 token 放到长期 localStorage 且永久不清理

---

## 17. 错误处理建议

## 17.1 表单级错误

例如：

- 关键词过多
- 时间范围超限
- 模板无效

表现方式：

- 表单下方错误提示

## 17.2 页面级错误

例如：

- 查询任务加载失败
- 结果快照读取失败

表现方式：

- 页面级错误块 + 重试按钮

## 17.3 全局错误

例如：

- 系统不可用
- 认证失效

表现方式：

- 顶部 banner / toast

---

## 18. 与 API 的关键协作约定

## 18.1 创建查询

前端必须兼容：

- HTTP 200 cache hit
- HTTP 202 async accepted

## 18.2 详情页读取

必须通过：

- `result_snapshot_id`
- `cluster_id`

读取，不做“只用 cluster_id”兜底。

## 18.3 coverage 与 flags

前端必须直接消费以下字段，不做自行推断：

- `coverage_note`
- `is_weak_signal`
- `is_low_confidence`
- `is_emerging_signal`

## 18.4 导出

导出必须按异步任务处理，不假设同步可得下载地址。

---

## 19. 推荐下一步产出

基于本文档，建议继续输出：

1. `doc/openapi_example_responses.md`
2. `doc/frontend_component_breakdown.md`
3. 前端原型或线框图

---

## 20. 一句话结论

前端状态管理的关键，不是保存尽可能多的数据，而是：

> **围绕 QueryTask、ResultSnapshot 和匿名访问凭据，把服务端真值稳定映射成可恢复、可轮询、可切换的页面状态。**
