# Demand Atlas｜需见 测试机启动说明

## 1. 说明

本文档用于在海外测试机上启动 **Demand Atlas｜需见** 当前仓库版本。

当前说明适用于：

- 单台测试机
- 手工启动验证
- 当前代码仓库现状
- Ubuntu
- 机器上可能已安装宝塔面板

---

## 2. 前提条件

启动前请先完成：

- `doc/test_server_preparation_checklist.md`

---

## 3. 推荐目录

```text
/srv/demand-atlas
```

示例：

```bash
cd /srv/demand-atlas
```

---

## 4. 首次初始化

### Step 1：拉取代码

```bash
git clone <repo-url> /srv/demand-atlas
cd /srv/demand-atlas
```

### Step 2：复制环境变量模板

```bash
cp .env.example .env
```

### Step 2.5：若是全新 Ubuntu，先一键安装依赖

```bash
./scripts/server-bootstrap-ubuntu.sh
```

说明：

- 会尝试安装 Docker
- 会尝试安装 `uv`
- 会尝试安装 Node.js
- 会尝试安装 `pnpm`

### Step 3：初始化依赖

```bash
./scripts/bootstrap.sh
```

说明：

- 会初始化 `apps/api`
- 会初始化 `apps/web`
- 会初始化 `apps/worker`

### Step 3.5：若机器上已有宝塔，请先改端口

优先检查端口占用：

```bash
sudo lsof -nP -iTCP -sTCP:LISTEN
```

若冲突，请修改 `.env` 中以下字段：

```bash
API_PORT=
WEB_PORT=
POSTGRES_BIND_PORT=
REDIS_BIND_PORT=
MINIO_BIND_PORT=
MINIO_CONSOLE_BIND_PORT=
```

---

## 5. 启动依赖服务

### Step 4：启动 PostgreSQL / Redis / MinIO

```bash
./scripts/dev-up.sh
```

若脚本失败，请优先检查：

- Docker daemon 是否运行
- 当前用户是否可执行 Docker

---

## 5.5 一键启动方式

若你希望直接按当前仓库的一键流程拉起，可执行：

```bash
./scripts/server-deploy.sh
```

它会依次执行：

1. `bootstrap`
2. `dev-up`
3. `alembic upgrade head`
4. 启动 API
5. 启动 Worker
6. 启动 Web
7. 执行 smoke test

日志位置：

```text
.runtime/logs/api.log
.runtime/logs/worker.log
.runtime/logs/web.log
```

---

## 6. 数据库初始化

### Step 5：执行 migration

```bash
cd apps/api
uv run alembic upgrade head
```

说明：

- 若数据库不可达，先检查 `.env` 中的 `DATABASE_URL`
- 当前仓库已具备 Alembic 配置与首批 migration

---

## 7. 启动应用

建议使用 3 个终端分别启动。

### Step 6：启动 API

```bash
cd /srv/demand-atlas
./scripts/run-api.sh
```

默认端口：

- `8000`

如需无痛重启 API，建议直接使用：

```bash
./scripts/restart-api.sh
```

### Step 7：启动 Worker

```bash
cd /srv/demand-atlas
./scripts/run-worker.sh
```

说明：

- 当前 worker 已具备：
  - `ping`
  - `run_query_task_pipeline`
- 若 Redis 不可达，worker 无法正常消费任务

如需无痛重启 Worker，建议使用：

```bash
./scripts/restart-worker.sh
```

### Step 8：启动 Web

```bash
cd /srv/demand-atlas
./scripts/run-web.sh
```

默认端口：

- `4173`

---

## 8. 启动后验证

### Step 9：执行 smoke test

```bash
cd /srv/demand-atlas
./scripts/smoke-test.sh
```

当前 smoke test 会检查：

1. API health
2. TopicTemplate 列表
3. QueryTask 创建
4. QueryTask 状态读取
5. ResultSnapshot 摘要读取
6. Web 根页面

---

## 9. 手工检查建议

如果需要更细验证，可手工执行：

### API health

```bash
curl http://127.0.0.1:8000/api/v1/healthz
```

### Topic templates

```bash
curl http://127.0.0.1:8000/api/v1/topic-templates
```

### Query task create

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"query_type":"one_click","template_id":"tpl_ai_tools","time_window":{"preset":"30d"}}' \
  http://127.0.0.1:8000/api/v1/query-tasks
```

### Query task status

```bash
curl http://127.0.0.1:8000/api/v1/query-tasks/qt_pending
```

### Result snapshot

```bash
curl http://127.0.0.1:8000/api/v1/result-snapshots/rs_01JVA1T4WM4B3PG5N8W1HEP7QA
```

---

## 10. 当前已知限制

当前测试机版本仍有以下限制：

- QueryTask / ResultSnapshot 接口以静态 / mock 风格返回为主
- 数据库 migration 在线验证依赖真实 PostgreSQL 实例
- Worker pipeline 仍是占位链路，不做真实数据处理
- API -> Worker 已有最小投递链路，但 Redis 不可达时会降级

---

## 11. 停止服务

### 停止依赖服务

```bash
./scripts/dev-down.sh
```

### 停止 API / Worker / Web

直接结束各自终端进程即可。

### 一键停止

```bash
./scripts/server-stop.sh
```

---

## 12. 一句话结论

> 当前测试机启动顺序是：`bootstrap -> dev-up -> migration -> run-api -> run-worker -> run-web -> smoke-test`。
