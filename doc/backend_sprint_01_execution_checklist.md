# Demand Atlas｜需见 后端 Sprint 01 执行清单

## 1. 说明

本清单用于按 `doc/sprint_01_backlog.md` 的后端相关工作项，逐阶段执行、验证与勾选。

当前范围包含：

- BE-01 项目骨架初始化
- BE-02 数据库基础 migration
- BE-03 TopicTemplate 读取接口
- BE-04 QueryTask 创建接口骨架
- BE-05 QueryTask 状态查询接口骨架
- BE-06 ResultSnapshot 基础读取接口骨架

当前阶段：`已完成`

---

## 2. 执行清单

- [x] BE-01 项目骨架初始化
- [x] BE-02 数据库基础 migration
- [x] BE-03 TopicTemplate 读取接口
- [x] BE-04 QueryTask 创建接口骨架
- [x] BE-05 QueryTask 状态查询接口骨架
- [x] BE-06 ResultSnapshot 基础读取接口骨架

---

## 3. 阶段验证记录

### BE-01

- 状态：已完成
- 验证项：
  - [x] 后端项目结构已初始化
  - [x] 本地可启动基础服务
  - [x] 有健康检查基础能力
- 验证结果：
  - 已创建 `apps/api` 基础目录结构
  - 已创建 `pyproject.toml`
  - 已接入 `FastAPI` / `uvicorn` / `pydantic-settings` / `sqlalchemy` / `alembic`
  - 已实现：
    - `app/core/config.py`
    - `app/core/logging.py`
    - `app/api/v1/router.py`
    - `app/api/v1/routes/health.py`
    - `app/main.py`
  - 已成功执行 `uv sync`
  - 已成功执行 `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000`
  - 健康检查通过：
    - `GET /api/v1/healthz`
    - 返回 `200 OK`
    - 返回体：`{\"status\":\"ok\"}`

### BE-02

- 状态：已完成（代码、离线验证、测试机在线验证）
- 验证项：
  - [x] 核心表 migration 已建立
  - [x] 本地数据库初始化路径明确
  - [x] 表结构与领域模型文档一致
- 验证结果：
  - 已创建：
    - `app/db/base.py`
    - `app/db/session.py`
    - `app/models/topic_template.py`
    - `app/models/query_task.py`
    - `app/models/result_snapshot.py`
  - 已创建 Alembic 配置：
    - `alembic.ini`
    - `alembic/env.py`
    - `alembic/script.py.mako`
    - `alembic/versions/20260514_01_initial_sprint_01_schema.py`
  - 已补充基础工程文件：
    - 根目录 `.env.example`
    - 根目录 `docker-compose.yml`
  - 已确认 metadata 中存在首批表：
    - `topic_templates`
    - `topic_template_versions`
    - `topic_template_version_subreddits`
    - `query_tasks`
    - `query_task_run_logs`
    - `result_snapshots`
  - 已通过离线 SQL 验证：
    - `uv run alembic upgrade head --sql`
    - 成功生成建表 SQL
  - 已通过 Python 编译验证：
    - `uv run python -m compileall app`
  - 已在 Ubuntu 测试机完成在线验证：
    - `uv run alembic upgrade head`
    - 执行通过

### BE-03

- 状态：已完成
- 验证项：
  - [x] TopicTemplate 读取接口已实现
  - [x] 接口字段与 OpenAPI 一致
  - [x] 可返回种子模板数据或静态响应
- 验证结果：
  - 已新增：
    - `app/api/v1/schemas/topic_template.py`
    - `app/services/topic_template_service.py`
    - `app/api/v1/routes/topic_templates.py`
    - `app/common/response.py`
  - 已接入路由：
    - `GET /api/v1/topic-templates`
    - `GET /api/v1/topic-templates/{template_id}`
  - 已提供首批静态模板数据：
    - `tpl_ai_tools`
    - `tpl_consumer_audio`
  - 已完成代码级验证：
    - 直接调用路由函数返回结构正确
    - `app.routes` 中已包含两个 TopicTemplate 路由
    - `uv run python -m compileall app` 通过

### BE-04

- 状态：已完成
- 验证项：
  - [x] QueryTask 创建接口已实现
  - [x] 支持 one_click / directed 两类请求
  - [x] 返回结构符合 OpenAPI 的 cache_hit / accepted 分支
- 验证结果：
  - 已新增：
    - `app/api/v1/schemas/query_task.py`
    - `app/services/query_task_service.py`
    - `app/api/v1/routes/query_tasks.py`
  - 已接入路由：
    - `POST /api/v1/query-tasks`
  - 当前已演进为数据库优先创建链路：
    - `one_click`
      - 成功缓存命中 -> `200 cache_hit`
      - 进行中任务复用 -> `202 accepted`
      - 未命中 -> `202 accepted`
    - `directed`
      - 成功缓存命中 -> `200 cache_hit`
      - 进行中任务复用 -> `202 accepted`
      - 未命中 -> `202 accepted`
    - 关键词过宽 -> `422 QUERY_TOO_BROAD`
    - `force_refresh=true` -> 显式绕过缓存与 inflight 复用
  - 已完成代码级验证：
    - 直接调用 service 分支逻辑正确
    - 直接调用 route 函数返回结构正确
    - `app.routes` 中已包含 `/api/v1/query-tasks`
    - `uv run python -m compileall app` 通过
  - 已完成测试机验证：
    - OneClick 二次 `cache_hit` 通过
    - Directed 二次 `cache_hit` 通过
    - OneClick / Directed `force_refresh=true` 绕过缓存通过

### BE-05

- 状态：已完成
- 验证项：
  - [x] QueryTask 状态查询接口已实现
  - [x] 返回结构包含 status / current_stage / progress / warnings
  - [x] 可覆盖 pending / running / success / failed 等状态
- 验证结果：
  - 已新增：
    - `app/api/v1/routes/query_task_status.py`
  - 已扩展：
    - `app/api/v1/schemas/query_task.py`
    - `app/services/query_task_service.py`
  - 已接入路由：
    - `GET /api/v1/query-tasks/{query_task_id}`
  - 已实现静态状态覆盖：
    - `pending`
    - `running`
    - `partial_success`
    - `success`
    - `failed`
  - 已完成代码级验证：
    - service 返回结构正确
    - route 函数返回结构正确
    - `app.routes` 中已包含 `/api/v1/query-tasks/{query_task_id}`
    - `uv run python -m compileall app` 通过

### BE-06

- 状态：已完成
- 验证项：
  - [x] ResultSnapshot 基础读取接口已实现
  - [x] 返回字段与 OpenAPI 一致
  - [x] 可返回 normal / empty / partial 其中一种静态摘要
- 验证结果：
  - 已新增：
    - `app/api/v1/schemas/result_snapshot.py`
    - `app/services/result_snapshot_service.py`
    - `app/api/v1/routes/result_snapshots.py`
  - 已接入路由：
    - `GET /api/v1/result-snapshots/{result_snapshot_id}`
  - 已实现静态摘要场景：
    - `normal`
    - `empty`
    - `partial`
  - 已完成代码级验证：
    - service 返回三种摘要结构正确
    - route 函数返回结构正确
    - `app.routes` 中已包含 `/api/v1/result-snapshots/{result_snapshot_id}`
    - `uv run python -m compileall app` 通过

---

## 4. 当前阶段总结

Sprint 01 后端骨架主链已完成：

- FastAPI 基础骨架
- 数据库模型与 Alembic 初版
- TopicTemplate 读取接口
- QueryTask 创建接口骨架
- QueryTask 状态查询接口骨架
- ResultSnapshot 摘要读取接口骨架

当前说明：

- 当前接口已进入“数据库优先 + 静态回退”阶段
- Ubuntu 测试机已完成在线 migration 与最小真实异步链路验证
