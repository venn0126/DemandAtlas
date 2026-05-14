# Demand Atlas｜需见

## 简体中文

### 项目简介

Demand Atlas｜需见 是一个面向 Reddit 内容发现与需求研究的服务，帮助用户在指定时间范围内，通过一键搜索或定向查询，快速识别平台上：

- 高讨论度内容
- 高关注度内容
- 显著增长中的内容

它的目标是将分散的 Reddit 讨论信号进行结构化整理，帮助用户更高效地发现值得关注的话题、帖子、趋势与真实需求。

### 核心能力

- **时间范围筛选**：限定分析窗口，聚焦某一时间段内的内容表现
- **一键发现**：快速浏览当前值得关注的热门或增长内容
- **定向查询**：基于关键词、主题或条件进行针对性检索
- **趋势识别**：发现讨论热度、关注度或增长速度异常突出的内容

### 适用场景

- 跟踪 Reddit 上的新兴话题与趋势
- 发现高热度社区讨论
- 挖掘潜在用户需求与兴趣方向
- 为内容选题、产品研究或市场洞察提供参考

### 仓库结构

- `doc/`：项目文档
- `frontend/`：前端相关代码与 mock 资产
- `openapi/`：接口定义与相关规范
- `apps/web/`：前端应用
- `apps/api/`：后端 API 应用
- `scripts/`：本地开发辅助脚本

### 本地开发

1. 初始化依赖

```bash
./scripts/bootstrap.sh
```

2. 复制环境变量模板

```bash
cp .env.example .env
```

3. 启动本地依赖服务

```bash
./scripts/dev-up.sh
```

4. 执行数据库 migration

```bash
cd apps/api
uv run alembic upgrade head
```

5. 启动后端 API

```bash
./scripts/run-api.sh
```

如需重启 API：

```bash
./scripts/restart-api.sh
```

6. 启动前端

```bash
./scripts/run-web.sh
```

7. 启动 Worker

```bash
./scripts/run-worker.sh
```

8. 执行 smoke test

```bash
./scripts/smoke-test.sh
```

### 测试机准备说明

后续若使用海外测试机，建议至少提前准备：

- Docker / Docker daemon
- Git
- `uv`
- `pnpm`
- 可访问的 `5432 / 6379 / 9000 / 9001 / 8000 / 4173` 端口策略
- 独立 `.env`

建议测试机路径约定：

```text
/srv/demand-atlas
```

建议测试机目标：

- 能拉起本地依赖服务
- 能执行后端 migration
- 能启动 API / Web
- 能跑 `scripts/smoke-test.sh`

如需 Ubuntu 测试机一键安装基础依赖，可执行：

```bash
./scripts/server-bootstrap-ubuntu.sh
```

如需在测试机上一键拉起当前仓库版本，可执行：

```bash
./scripts/server-deploy.sh
```

停止可执行：

```bash
./scripts/server-stop.sh
```

---

## English

### Overview

Demand Atlas is a service for Reddit content discovery and demand research. Within a specified timeframe, it helps users identify content that is:

- highly discussed
- highly followed
- showing significant growth

Users can explore these signals through one-click discovery or targeted queries. The goal is to turn fragmented Reddit discussions into structured insights, making it easier to spot valuable topics, posts, trends, and real user needs.

### Core Capabilities

- **Time-window filtering**: focus analysis on a specific period
- **One-click discovery**: quickly surface notable hot or fast-growing content
- **Targeted queries**: search by keywords, topics, or custom conditions
- **Trend detection**: identify content with unusually strong discussion, attention, or growth signals

### Use Cases

- Track emerging topics and trends on Reddit
- Discover highly active community discussions
- Uncover potential user needs and interest directions
- Support content planning, product research, and market insight work

### Repository Structure

- `doc/`: project documentation
- `frontend/`: frontend-related code and mock assets
- `openapi/`: API definitions and related specifications
- `apps/web/`: web application
- `apps/api/`: backend API service
- `scripts/`: local development helper scripts

### Local Development

1. Bootstrap dependencies

```bash
./scripts/bootstrap.sh
```

2. Copy the environment template

```bash
cp .env.example .env
```

3. Start local dependency services

```bash
./scripts/dev-up.sh
```

4. Run database migrations

```bash
cd apps/api
uv run alembic upgrade head
```

5. Start the API

```bash
./scripts/run-api.sh
```

To restart the API cleanly:

```bash
./scripts/restart-api.sh
```

6. Start the web app

```bash
./scripts/run-web.sh
```

7. Start the worker

```bash
./scripts/run-worker.sh
```

8. Run the smoke test

```bash
./scripts/smoke-test.sh
```

### Test Server Preparation

If you plan to use an overseas machine for testing later, prepare at least:

- Docker / running Docker daemon
- Git
- `uv`
- `pnpm`
- reachable port policy for `5432 / 6379 / 9000 / 9001 / 8000 / 4173`
- a dedicated `.env`

Suggested application path:

```text
/srv/demand-atlas
```

Suggested test server goals:

- bring up local dependency services
- run backend migrations
- start API / Web
- run `scripts/smoke-test.sh`

For Ubuntu test servers, install baseline dependencies with:

```bash
./scripts/server-bootstrap-ubuntu.sh
```

For one-command startup on the test server:

```bash
./scripts/server-deploy.sh
```

To stop services:

```bash
./scripts/server-stop.sh
```
