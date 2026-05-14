# Demand Atlas｜需见 Mock 数据说明

## 1. 目录目标

本目录用于提供前端开发与联调前期可直接使用的 mock 数据。

这些 mock 数据来源于：

- `doc/api_contract_draft.md`
- `doc/openapi_example_responses.md`
- `openapi/openapi.yaml`

## 2. 使用建议

建议前端优先用以下文件打通主链路：

1. `topic-templates.list.json`
2. `query-task.create.async.json`
3. `query-task.status.running.json`
4. `query-task.status.success.json`
5. `result-snapshot.summary.normal.json`
6. `result-snapshot.board.hot.json`
7. `cluster-detail.normal.json`

## 3. 推荐联调顺序

### 一键发现 / 定向发现提交

- `query-task.create.cache-hit.json`
- `query-task.create.async.json`

### 查询任务页

- `query-task.status.pending.json`
- `query-task.status.running.json`
- `query-task.status.partial-success.json`
- `query-task.status.failed.json`

### 结果页

- `result-snapshot.summary.normal.json`
- `result-snapshot.summary.empty.json`
- `result-snapshot.summary.partial.json`
- `result-snapshot.board.hot.json`
- `result-snapshot.board.growth.json`
- `result-snapshot.board.opportunity.json`
- `result-snapshot.board.empty.json`

### 详情页

- `cluster-detail.normal.json`
- `cluster-detail.partial-evidence.json`

### 导出

- `export-job.create.accepted.json`
- `export-job.status.running.json`
- `export-job.status.success.json`
- `export-job.status.failed.json`

## 4. 约定

- 所有时间均为 UTC ISO 8601
- 所有 ID 为演示用途
- 字段命名与 OpenAPI 草案保持一致

