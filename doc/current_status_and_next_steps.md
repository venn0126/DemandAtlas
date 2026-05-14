# Demand Atlas｜需见 当前进度与下一步执行说明

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 当前进度与下一步执行说明
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用场景：中断后恢复 / 下次开工前快速对齐 / 项目 handoff

---

## 2. 当前项目结论

截至当前阶段，**Demand Atlas｜需见** 已完成从“需求定义”到“工程启动方案”的核心文档设计。

当前结论可以概括为：

> 项目已完成产品、技术、前端、交付、灰度与问题治理的文档体系搭建，**下一步应进入工程初始化与 Sprint 01 实施阶段**。

---

## 3. 已完成事项

## 3.1 产品与品牌

已完成：

- 产品正式命名定稿：
  - 英文：**Demand Atlas**
  - 中文：**需见**
  - 标准写法：**Demand Atlas｜需见**
- PRD 主文档已完成并增强
- 边界 case review 已完成
- UI 风格已定稿为：
  - **Research Console / 冷静型研究工作台**

## 3.2 技术架构

已完成：

- 总体技术架构输入文档
- 领域模型与 schema 设计
- QueryTask 与 Pipeline 设计
- 评分引擎设计
- 技术选型最终拍板

## 3.3 前端与设计

已完成：

- 信息架构与状态流
- 前端状态管理方案
- 前端组件拆解
- 页面线框说明
- mock 数据资产
- `apps/web` 前端工程骨架与 mock 主链路已落地
- 前端已完成结构化重构：
  - i18n 基础设施
  - layout / common / business 组件分层
  - types / adapters / hooks 分层
  - query / task / result / detail 页面容器化

## 3.4 API 与工程契约

已完成：

- API Contract Draft
- OpenAPI Outline
- OpenAPI Example Responses
- 正式 `openapi/openapi.yaml` 首版草稿
- TopicTemplate 已支持数据库优先读取（空库 / 异常时回落静态数据）
- QueryTask / ResultSnapshot 已开始接入数据库优先链路（当前保留静态回退）
- QueryTask 最小真实数据库链路已验证通过
- ResultSnapshot 最小真实数据库链路已验证通过

## 3.5 项目交付推进

已完成：

- MVP 交付计划
- 实施工作分解（WBS）
- Sprint 01 / 02 / 03 Backlog
- 上线准备检查清单
- 灰度观察模板
- 结果质量评审模板
- 上线后问题分级与处置手册
- 测试机准备清单与启动说明文档

## 3.6 工程启动方案

已完成：

- Monorepo 结构与启动方案
- 开发与部署工作流（已明确不采用“推文件到服务器目录”的主流程）
- `apps/api` FastAPI 基础骨架已落地
- 后端健康检查已可本地启动验证
- `apps/worker` Dramatiq + Redis 基础骨架已落地
- Worker 最小 QueryTask pipeline 占位链路已落地
- API -> Worker 最小投递链路已落地（Redis 不可用时可降级）
- Worker -> 数据库最小状态写回链路已验证通过
- Ubuntu 海外测试机最小闭环验证已通过
  - 验证记录：`doc/test_server_validation_record_2026-05-14.md`

---

## 4. 已拍板的关键决策

以下内容已定，不建议下次随意变动：

## 4.1 产品名

- **Demand Atlas｜需见**

## 4.2 技术栈

### 前端

- React 18 + TypeScript + Vite
- TanStack Query
- Zustand
- Tailwind CSS
- shadcn/ui + Radix UI

### 后端

- Python 3.12 + FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic

### 异步任务

- Dramatiq + Redis

### 数据层

- PostgreSQL 16
- PostgreSQL Full Text Search + GIN / trigram
- pgvector 预埋
- Redis 7
- S3-compatible object storage

### 部署

- Monorepo
- Docker Compose（本地依赖服务）
- Git + CI/CD + Docker 镜像 + 服务器拉镜像部署
- Render 首选 / Railway 备选

## 4.3 V1 关键架构决策

- V1 不上 OpenSearch
- V1 不上微服务
- V1 不上 K8s
- V1 不自建 Auth
- V1 不采用“代码文件推送到服务器目录再手工重启”作为主流程

---

## 5. 当前文档体系状态

当前文档体系已经覆盖：

1. 产品定义
2. 技术设计
3. 数据模型
4. QueryTask / Pipeline
5. API 契约
6. 前端状态与组件
7. 页面线框与 UI 风格
8. Sprint 计划
9. 上线检查
10. 灰度观察
11. 线上问题治理

### 结论

当前阶段**不再需要继续扩展抽象设计文档**，下一步应转入：

- 工程文件初始化
- Sprint 01 实施

### 当前补充结论

当前仓库已从“本地可运行”推进到“测试机可运行”阶段，并已完成最小真实异步链路验证。

---

## 6. 当前未完成但应该优先执行的内容

以下内容还没有正式落成工程文件：

## 6.1 工程文件

优先级最高：

1. `docker-compose.yml`
2. `.env.example`
3. 根目录 `README.md`

### 当前补充说明

- 根目录 `README.md` 已创建
- 当前最高优先级已切换为：
  1. `docker-compose.yml`
  2. `.env.example`
  3. `apps/api` 静态回退向真实数据库链路继续替换
  4. `apps/worker` 占位 pipeline 向真实业务处理继续替换

## 6.2 辅助脚本

建议随后补：

4. `scripts/dev-up.sh`
5. `scripts/dev-down.sh`
6. `scripts/smoke-test.sh`

### 当前补充说明

- 已创建：
  - `scripts/bootstrap.sh`
  - `scripts/dev-up.sh`
  - `scripts/dev-down.sh`
  - `scripts/run-api.sh`
  - `scripts/run-worker.sh`
  - `scripts/restart-worker.sh`
  - `scripts/run-web.sh`
  - `scripts/smoke-test.sh`
  - `scripts/seed_topic_templates.py`
  - `scripts/server-bootstrap-ubuntu.sh`
  - `scripts/server-deploy.sh`
  - `scripts/server-stop.sh`
- 当前脚本已完成静态校验：
  - `bash -n` 通过
- `scripts/bootstrap.sh` 已完成实际执行验证
- `scripts/bootstrap.sh` 已接入 `apps/worker` 依赖初始化
- 当前脚本运行依赖：
  - Docker daemon 可用
  - 本地 API / Web 已启动（针对 `smoke-test.sh`）

## 6.3 仓库骨架

建议随后初始化：

7. `apps/web`
8. `apps/api`
9. `apps/worker`
10. `packages/shared-types`
11. `infra/`

## 6.4 CI/CD 草稿

后续补：

12. `.github/workflows/build.yml`
13. `.github/workflows/deploy-dev.yml`
14. `.github/workflows/deploy-prod.yml`

---

## 7. 下一次开工时的最佳起手顺序

下次继续开发时，建议严格按以下顺序推进：

## Step 1：看这两份文档

先快速阅读：

1. `doc/current_status_and_next_steps.md`
2. `doc/project_index.md`

目的：

- 重新进入上下文
- 明确当前已拍板内容

## Step 2：看工程启动相关文档

再看：

3. `doc/tech_stack_decision.md`
4. `doc/monorepo_structure_and_bootstrap.md`
5. `doc/development_and_deploy_workflow.md`

目的：

- 直接进入工程初始化

## Step 3：落工程基础文件

先真正创建：

1. `docker-compose.yml`
2. `.env.example`
3. `README.md`

## Step 4：初始化 Monorepo 目录

创建：

- `apps/web`
- `apps/api`
- `apps/worker`
- `packages/shared-types`
- `infra/`

## Step 5：按 Sprint 01 开工

执行：

- `doc/sprint_01_backlog.md`

### 当前实际推进建议

前端 mock 主链路已完成并已提交，下一步建议直接进入：

- `doc/backend_sprint_01_execution_checklist.md`
- 从 **BE-02 数据库基础 migration** 开始

---

## 8. 推荐的下一步执行目标

下次继续时，推荐目标不是“继续补文档”，而是：

> **完成工程启动三件套**

即：

1. `docker-compose.yml`
2. `.env.example`
3. `README.md`

### 原因

这三件完成后：

- 项目真正进入工程启动
- 后端可开始建表与 API 骨架
- 前端可开始接 mock 和页面骨架

---

## 9. 对应的 Sprint 阶段建议

### 当前所在阶段

项目目前位于：

> **Sprint 01 启动前**

### 下一阶段

下一阶段应进入：

> **Sprint 01：骨架打通**

不建议现在直接跳到：

- Sprint 02 真实分析闭环
- Sprint 03 质量收束

---

## 10. 风险提醒

下次继续时，最容易出现的偏差有：

## 10.1 继续写更多抽象文档

当前收益已经很低，不建议优先。

## 10.2 直接开始写业务逻辑，但没有工程骨架

这样很容易导致：

- 目录混乱
- 环境混乱
- 后续迁移成本变高

## 10.3 重新讨论已拍板技术选型

除非出现新的强约束，否则不建议重新打开：

- 前端框架
- 后端框架
- 检索方案
- 部署方式

---

## 11. 下次你可以直接对我说什么

为了快速进入开发阶段，下次你可以直接给我以下任一指令：

### 工程启动

- “开始生成 docker-compose.yml”
- “开始生成 .env.example”
- “开始生成根 README”
- “初始化 monorepo 目录骨架”

### 后端启动

- “开始搭 FastAPI 骨架”
- “开始写 Alembic migration 草稿”
- “开始实现 QueryTask API 骨架”

### 前端启动

- “开始搭 Vite + React 骨架”
- “开始接 frontend/mock”
- “开始搭查询页和任务页骨架”

### CI/CD 启动

- “开始生成 GitHub Actions build workflow”
- “开始生成 deploy workflow 草稿”

---

## 12. 一句话 handoff

如果下次只看一句话，请看这句：

> **项目的方案设计已经足够完整，下一步不要再扩抽象文档，而应直接从 `docker-compose.yml`、`.env.example`、`README.md` 开始进入工程启动。**
