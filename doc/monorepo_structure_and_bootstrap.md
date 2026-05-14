# Demand Atlas｜需见 Monorepo 结构与启动方案

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 Monorepo 结构与启动方案
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：仓库初始化 / 工程脚手架搭建 / 本地开发环境准备 / Sprint 01 开工
- 上游输入：
  - `doc/tech_stack_decision.md`
  - `doc/mvp_delivery_plan.md`
  - `doc/sprint_01_backlog.md`
  - `openapi/openapi.yaml`

---

## 2. 文档目标

本文档用于把已拍板的技术选型，进一步落成可执行的工程目录与启动方案。

本文档重点回答：

1. Monorepo 应该如何组织
2. 前端、后端、worker、共享类型分别放哪里
3. 本地开发环境如何启动
4. Docker Compose 首版应该承载哪些服务
5. Sprint 01 应优先初始化哪些目录与脚手架

---

## 3. 总体原则

## 3.1 一个仓库承载全部 V1 资产

V1 采用 Monorepo，原因是：

- 前后端、OpenAPI、mock、文档高度耦合
- 当前迭代速度比组织边界更重要
- 小团队协作下，单仓维护成本更低

## 3.2 代码、契约、文档、mock 同仓

同一个仓库内应同时包含：

- 应用代码
- OpenAPI 契约
- mock 数据
- 项目文档
- 基础脚本

## 3.3 先搭最小骨架，不做过度工程化

V1 仓库目标是：

- 快速起步
- 容易本地跑通
- 目录边界清晰

而不是：

- 一开始就做超复杂 workspace 编排
- 一开始就做多环境多集群复杂脚本

---

## 4. 最终推荐目录结构

## 4.1 顶层结构

建议仓库顶层采用：

```text
DemandAtlas/
  apps/
  packages/
  openapi/
  frontend/
    mock/
  infra/
  scripts/
  doc/
  .github/
  .env.example
  docker-compose.yml
  README.md
```

## 4.2 目录职责

### `apps/`

存放可运行应用：

- Web 前端
- API 后端
- Worker

### `packages/`

存放共享代码：

- API types
- 常量
- 共享 schema

### `openapi/`

存放正式 OpenAPI 契约文件。

### `frontend/mock/`

存放前端 mock 资产。

### `infra/`

存放基础设施相关配置：

- DB init
- object storage init
- deployment notes

### `scripts/`

存放辅助脚本：

- bootstrap
- seed
- lint
- format

### `doc/`

存放全部项目文档。

---

## 5. apps 目录建议

## 5.1 apps/web

前端 Web 应用。

### 技术栈

- React
- TypeScript
- Vite
- TanStack Query
- Zustand
- Tailwind CSS

### 建议结构

```text
apps/web/
  src/
    app/
    pages/
    containers/
    components/
    hooks/
    stores/
    services/
    styles/
    utils/
    types/
  public/
  index.html
  package.json
  vite.config.ts
  tsconfig.json
```

### 职责

- 页面实现
- 状态管理
- API 调用
- mock 切换

---

## 5.2 apps/api

后端 API 应用。

### 技术栈

- Python 3.12
- FastAPI
- Pydantic v2
- SQLAlchemy
- Alembic

### 建议结构

```text
apps/api/
  app/
    api/
      v1/
        routes/
        schemas/
    core/
    db/
    models/
    services/
    repositories/
    integrations/
    common/
    main.py
  alembic/
  tests/
  pyproject.toml
```

### 职责

- REST API
- QueryTask 创建与读取
- ResultSnapshot 读取
- ExportJob 接口

---

## 5.3 apps/worker

异步任务 Worker 应用。

### 技术栈

- Python 3.12
- Dramatiq
- Redis

### 建议结构

```text
apps/worker/
  worker/
    jobs/
    pipeline/
    fetch/
    normalize/
    retrieve/
    cluster/
    score/
    snapshot/
    main.py
  tests/
  pyproject.toml
```

### 职责

- QueryTask pipeline 执行
- export job 执行

### 说明

若首版希望更简单，也可以把 worker 和 api 放在同一 Python package 中，只通过不同启动命令区分角色。

---

## 6. packages 目录建议

## 6.1 packages/shared-types

### 用途

存放前后端共享的类型约定与常量。

### 建议内容

```text
packages/shared-types/
  src/
    enums/
    constants/
    ui/
    api/
  package.json
  tsconfig.json
```

### 说明

前端可直接使用。
后端 Python 不直接 import，但可以对照同一份 OpenAPI 契约生成类型。

## 6.2 packages/config（可选）

若需要统一前端工具链配置，可加：

```text
packages/config/
  eslint/
  prettier/
  tsconfig/
```

V1 可选，不强制。

---

## 7. openapi 目录建议

## 7.1 当前结构

当前已有：

```text
openapi/
  openapi.yaml
```

## 7.2 后续推荐结构

若后续需要拆分，可逐步演进为：

```text
openapi/
  openapi.yaml
  paths/
  schemas/
  examples/
```

### V1 建议

首版先保留单文件：

- `openapi/openapi.yaml`

这样更简单，后续再拆。

---

## 8. frontend/mock 目录建议

当前已经有：

```text
frontend/mock/
  README.md
  manifest.json
  *.json
```

## 8.1 建议补充结构（后续）

```text
frontend/mock/
  README.md
  manifest.json
  scenarios/
  loaders/
```

### 说明

V1 先不强制拆目录。

---

## 9. infra 目录建议

## 9.1 首版用途

存放与基础设施初始化相关的轻量文件。

### 建议结构

```text
infra/
  postgres/
    init/
  minio/
    buckets/
  redis/
  deployment/
```

## 9.2 示例用途

- PostgreSQL 初始化 SQL
- MinIO bucket 初始化脚本
- 部署说明

---

## 10. scripts 目录建议

## 10.1 建议脚本

```text
scripts/
  bootstrap.sh
  seed_topic_templates.py
  seed_subreddit_catalog.py
  lint.sh
  format.sh
  dev-up.sh
  dev-down.sh
```

## 10.2 首批必须脚本

Sprint 01 建议优先准备：

- `bootstrap.sh`
- `dev-up.sh`
- `dev-down.sh`
- `seed_topic_templates.py`

---

## 11. README 顶层建议

仓库根 README 建议最少包含：

1. 项目简介
2. 技术栈
3. 目录结构
4. 本地启动步骤
5. 常用命令
6. 文档入口（指向 `doc/project_index.md`）

---

## 12. 环境变量方案

## 12.1 顶层 `.env.example`

建议在根目录维护：

```text
.env.example
```

包含所有关键环境变量模板。

## 12.2 变量分组建议

### 应用基础

- `APP_ENV`
- `LOG_LEVEL`

### API

- `API_PORT`
- `API_BASE_URL`

### Web

- `WEB_PORT`
- `VITE_API_BASE_URL`

### PostgreSQL

- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

### Redis

- `REDIS_HOST`
- `REDIS_PORT`

### Object Storage

- `S3_ENDPOINT`
- `S3_BUCKET_RAW`
- `S3_BUCKET_EXPORTS`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`

### Auth

- `CLERK_SECRET_KEY`
- `VITE_CLERK_PUBLISHABLE_KEY`

### Monitoring

- `SENTRY_DSN_API`
- `SENTRY_DSN_WEB`

---

## 13. Docker Compose 首版设计

## 13.1 V1 本地依赖服务

首版 `docker-compose.yml` 建议只承载基础依赖服务：

- PostgreSQL
- Redis
- MinIO

### 可选

- pgAdmin / Adminer（仅开发）

## 13.2 为什么不把 web / api / worker 全部强绑进 Compose

建议首版：

- 基础依赖走 Compose
- 应用服务本地进程启动

原因：

- 调试体验更好
- 热更新更简单
- 降低初期开发复杂度

### 也就是说

本地模式建议：

```text
docker compose up postgres redis minio
```

然后：

- `apps/api` 本地启动
- `apps/worker` 本地启动
- `apps/web` 本地启动

## 13.3 后续可演进模式

若后续需要统一开发环境，可再扩展 Compose 运行：

- web
- api
- worker

但 V1 不强制。

---

## 14. 本地启动顺序建议

## 14.1 Step 1：启动依赖服务

```text
docker compose up -d postgres redis minio
```

## 14.2 Step 2：初始化数据库

```text
cd apps/api
alembic upgrade head
```

## 14.3 Step 3：初始化模板与基础种子

```text
python ../../scripts/seed_topic_templates.py
python ../../scripts/seed_subreddit_catalog.py
```

## 14.4 Step 4：启动 API

```text
cd apps/api
uvicorn app.main:app --reload --port 8000
```

## 14.5 Step 5：启动 Worker

```text
cd apps/worker
python -m worker.main
```

## 14.6 Step 6：启动 Web

```text
cd apps/web
pnpm dev
```

---

## 15. Monorepo 包管理建议

## 15.1 前端包管理

建议使用：

> **pnpm**

原因：

- workspace 支持好
- 安装快
- Monorepo 体验好

## 15.2 Python 依赖管理

建议使用：

> **uv**

原因：

- 快
- 简洁
- 对 Python 3.12 开发体验好

### 结论

前端和 Python 可采用双工具链：

- JS/TS：`pnpm`
- Python：`uv`

这是可接受且高效的组合。

---

## 16. API 与类型同步建议

## 16.1 契约源头

以：

> `openapi/openapi.yaml`

作为 API 契约源头。

## 16.2 前端类型生成建议

可后续增加：

- 从 OpenAPI 生成 TypeScript client/types

V1 可先手写轻 client，不阻塞开发。

## 16.3 为什么不首版强制 codegen

因为：

- 接口仍可能变化
- 首版手写更快
- 等字段稳定后再上 codegen 更合理

---

## 17. Sprint 01 对应的初始化清单

## 17.1 必须先建的目录

- `apps/web`
- `apps/api`
- `apps/worker`
- `packages/shared-types`
- `openapi`
- `frontend/mock`
- `infra`
- `scripts`
- `doc`

## 17.2 必须先建的文件

- `docker-compose.yml`
- `.env.example`
- 根 `README.md`
- `apps/api/pyproject.toml`
- `apps/web/package.json`
- `apps/worker/pyproject.toml`

## 17.3 必须先跑通的最小链路

- Compose 启动依赖
- API 健康检查
- Web 首页启动
- mock 驱动前端页面

---

## 18. 生产部署结构建议

## 18.1 推荐服务拆分

生产建议拆为 3 类服务：

### Web

- 静态前端

### API

- FastAPI 服务

### Worker

- Dramatiq worker

### Managed Dependencies

- PostgreSQL
- Redis
- Object Storage

## 18.2 这样拆的原因

- 部署简单
- 职责清晰
- 后续扩容方便

---

## 19. 最终推荐目录树

```text
DemandAtlas/
├── apps/
│   ├── api/
│   ├── web/
│   └── worker/
├── packages/
│   └── shared-types/
├── openapi/
│   └── openapi.yaml
├── frontend/
│   └── mock/
├── infra/
├── scripts/
├── doc/
├── .github/
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 20. 最终结论

对于 **Demand Atlas｜需见** 当前阶段，最合适的工程落地方式是：

> **Monorepo + 应用分目录 + 依赖服务 Compose 化 + 应用进程本地启动 + OpenAPI 为契约源头 + mock 驱动前端并行开发。**

这套方案同时满足：

- **部署简单**
- **方便扩展**
- **性能佳**

