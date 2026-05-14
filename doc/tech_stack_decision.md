# Demand Atlas｜需见 技术选型决策文档

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 技术选型决策文档
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：技术拍板 / 架构评审 / 工程启动 / 基础设施初始化
- 上游输入：
  - `doc/technical_architecture_input.md`
  - `doc/domain_model_and_schema.md`
  - `doc/query_task_and_pipeline_design.md`
  - `doc/frontend_state_management_notes.md`
  - `openapi/openapi.yaml`

---

## 2. 文档目标

本文档用于对 **需见** 的技术栈做最终拍板。

本文档重点回答：

1. 前端、后端、数据、任务、存储、部署分别采用什么技术
2. 每个候选方案为什么不选
3. 最终方案为什么最符合以下目标

本次选型目标：

- **部署简单**
- **方便扩展**
- **性能佳**

---

## 3. 决策原则

## 3.1 V1 优先级排序

本项目 V1 的选型优先级按以下顺序排序：

1. **交付速度**
2. **系统简单度**
3. **可扩展性**
4. **性能**
5. **极致技术先进性**

### 解释

对于 **需见** 这种“异步分析 + 结果快照 + 研究工作台”型产品：

- 过早引入复杂微服务、复杂搜索栈、复杂工作流编排，会显著拖慢交付
- 但完全只按“最快能跑”选择，又会影响后续扩展

因此本次策略是：

> **选择 V1 足够简单、但能自然演进到 V1.5 / V2 的技术栈。**

## 3.2 本文档优先级

本文件中的最终选型结论，优先级高于前面文档中偏“推荐性”的技术选项描述。

即：

- 前面文档可作为背景
- **本文件作为最终拍板依据**

---

## 4. 最终拍板结果总览

## 4.1 最终推荐技术栈

### 前端

- **React 18 + TypeScript + Vite**
- **TanStack Query**
- **Zustand**
- **Tailwind CSS**
- **shadcn/ui + Radix UI**

### 后端 API

- **Python 3.12 + FastAPI**
- **Pydantic v2**
- **SQLAlchemy 2.x**
- **Alembic**

### 异步任务 / Worker

- **Dramatiq + Redis**

### 主数据库

- **PostgreSQL 16**

### 检索方案

- **PostgreSQL Full Text Search + GIN / trigram**
- **pgvector 作为预埋扩展**

### 缓存

- **Redis 7**

### 对象存储

- **S3 Compatible Object Storage**
  - 本地：**MinIO**
  - 生产：**AWS S3 / Cloudflare R2 / 阿里云 OSS** 任选其一

### API 契约

- **OpenAPI 3.1**

### 本地开发与部署

- **Docker Compose**

### 生产部署

- **容器化部署 + Managed PaaS**
  - 首选模式：**Render / Railway 类托管容器平台**

### 可观测性

- **Sentry**（前后端错误追踪）
- **结构化日志**
- **基础 Metrics / Health Check**

---

## 5. 前端技术选型决策

## 5.1 候选方案

### 方案 A：Next.js

优点：

- 全栈能力强
- SSR / SEO 能力好
- 路由和服务端能力完整

缺点：

- 本项目已有独立后端 API，不需要再引入一套 server framework
- 会造成前后端职责边界重复
- 部署与调试复杂度高于纯前端方案

### 方案 B：React + Vite

优点：

- 启动快，开发体验好
- 前后端边界清晰
- 静态资源部署简单
- 与现有 API-first 方案天然匹配

缺点：

- 不强调 SSR
- 需要自己组织前端工程结构

## 5.2 最终结论

### 选择：

> **React + TypeScript + Vite**

## 5.3 选择理由

为什么它是最优解：

### 对“部署简单”

- 可以直接构建静态资源
- 部署到 CDN / 静态托管最简单

### 对“方便扩展”

- 前后端职责清晰
- 后续即使换 API 或增加 BFF，也不会推翻前端工程

### 对“性能佳”

- Vite 构建与开发体验优秀
- React SPA 对当前产品场景足够

## 5.4 补充前端基础库选择

### 状态管理

- 服务端状态：**TanStack Query**
- 本地 UI / session 状态：**Zustand**

### UI 层

- 样式：**Tailwind CSS**
- 组件基础：**shadcn/ui + Radix UI**

### 原因

- 这套组合实现快
- 对状态复杂但页面数量有限的 B2B 工具很合适
- 组件与样式扩展性强

---

## 6. 后端 API 技术选型决策

## 6.1 候选方案

### 方案 A：NestJS（Node.js）

优点：

- 工程结构清晰
- 生态成熟
- 对 REST / OpenAPI / 模块化友好

缺点：

- 本项目有较强的数据处理、文本分析、AI / NLP 属性
- 若分析逻辑在 Python，Node 和 Python 双栈会增加复杂度

### 方案 B：Go（Gin / Fiber / Echo 等）

优点：

- 性能强
- 部署轻
- 并发能力好

缺点：

- 对数据分析 / 文本处理 / AI 生态不如 Python 顺手
- 对团队后续快速试验不一定最友好

### 方案 C：FastAPI（Python）

优点：

- 对文本分析、AI、数据处理最友好
- OpenAPI 原生能力强
- 异步支持好
- API 层与分析层更容易统一语言栈

缺点：

- 极致高并发性能不如 Go
- 若工程约束不严，容易写成脚本式代码

## 6.2 最终结论

### 选择：

> **Python 3.12 + FastAPI**

## 6.3 选择理由

为什么它是最优解：

### 对“部署简单”

- FastAPI 配置简单
- OpenAPI 自动生成
- Python 生态部署成本低

### 对“方便扩展”

- API 层和分析层共用 Python 生态
- 后续接 AI / embedding / clustering / summarization 更顺滑

### 对“性能佳”

- 对当前 V1 来说，性能瓶颈不在 API Web 框架，而在异步分析链路
- FastAPI 对“任务编排型 API”完全足够

## 6.4 后端工程基础设施

配套选择：

- 数据校验：**Pydantic v2**
- ORM：**SQLAlchemy 2.x**
- Migration：**Alembic**

理由：

- 成熟
- 与 FastAPI 组合稳定
- 文档生态完整

---

## 7. 异步任务与 Worker 选型决策

## 7.1 候选方案

### 方案 A：Celery + Redis/RabbitMQ

优点：

- 成熟
- 功能多
- 社区大

缺点：

- 学习与运维复杂度偏高
- 对 V1 来说有些重

### 方案 B：Temporal

优点：

- 工作流能力极强
- 长任务控制能力强

缺点：

- 对 V1 明显过重
- 部署和认知成本高

### 方案 C：RQ / ARQ / Dramatiq 类 Redis 队列

优点：

- 轻量
- 简单
- 部署成本低

缺点：

- 功能不如 Celery / Temporal 全
- 需要自己约束任务结构

## 7.2 最终结论

### 选择：

> **Dramatiq + Redis**

## 7.3 选择理由

为什么它是最优解：

### 对“部署简单”

- 只依赖 Redis
- 比 Celery 更轻
- 比 Temporal 简单很多

### 对“方便扩展”

- 支持后续把 fetch / normalize / cluster / score 拆成更清晰 worker
- 未来若任务复杂度暴增，再升级更重型编排方案也可接受

### 对“性能佳”

- 对当前异步任务量足够
- Worker 模式适合 QueryTask pipeline

## 7.4 结论备注

V1 不需要上 Temporal。  
V1 也不建议一开始就上 Celery + RabbitMQ 这种较重组合。

---

## 8. 主数据库选型决策

## 8.1 候选方案

### 方案 A：PostgreSQL

优点：

- 稳定
- JSON / Full Text / GIN 丰富
- 和事务型模型非常匹配

缺点：

- 如果完全拿它替代专业搜索引擎，在超大规模下会吃力

### 方案 B：MySQL

优点：

- 普及度高

缺点：

- 对 JSON / FTS / 扩展性不如 PostgreSQL
- 不适合本项目这种“结构化 + 检索 + 半分析”场景

## 8.2 最终结论

### 选择：

> **PostgreSQL 16**

## 8.3 选择理由

为什么它是最优解：

### 对“部署简单”

- 一个主数据库就能承载事务数据与部分检索需求

### 对“方便扩展”

- 后续可接 pgvector
- 后续若规模变大，再单独拆搜索引擎也不晚

### 对“性能佳”

- 对 V1 的数据规模和查询模式完全足够
- 对 QueryTask / ResultSnapshot / Cluster 这类事务对象很稳

---

## 9. 检索与搜索选型决策

这部分是本次最关键的“最终拍板”，因为它和前面泛化推荐文档略有区别。

## 9.1 候选方案

### 方案 A：OpenSearch / Elasticsearch

优点：

- 全文检索强
- 聚合能力强
- 适合大规模搜索

缺点：

- 增加一个独立重型基础设施
- 运维和部署复杂度明显上升
- 对 V1 会过早增加系统复杂度

### 方案 B：PostgreSQL Full Text Search

优点：

- 部署最简单
- 不需要单独搜索集群
- 与现有数据模型一致

缺点：

- 在超大规模、多复杂排序下不如专用搜索引擎

### 方案 C：PostgreSQL FTS + pgvector

优点：

- 保持单数据库方案
- 既支持关键词检索，也为后续语义检索预留空间

缺点：

- 比纯 FTS 稍复杂
- 向量部分若首版就重用，可能拖慢交付

## 9.2 最终结论

### 选择：

> **V1 使用 PostgreSQL Full Text Search + GIN / trigram**
>
> **同时预埋 pgvector 扩展，但首版不把向量检索作为主依赖**

## 9.3 选择理由

为什么这是最优解：

### 对“部署简单”

- 去掉 OpenSearch，少一套基础设施
- 本地开发和线上部署都更轻

### 对“方便扩展”

- 先用 FTS 跑通关键词召回
- 后续需要语义召回时再启用 pgvector
- 若数据规模再上一个量级，再考虑单独引入 OpenSearch

### 对“性能佳”

- 对 V1 候选社区池 + 查询补拉模式完全够用
- GIN / trigram 对关键词检索和模糊匹配足够实用

## 9.4 明确结论

### 本次最终拍板：

- **V1 不上 OpenSearch**
- **V1 用 PostgreSQL 统一承担事务存储 + 基础检索**

这能显著降低部署复杂度。

---

## 10. 缓存选型决策

## 10.1 候选方案

### 方案 A：Redis

优点：

- 成熟
- 既可做 cache，也可做 queue broker

### 方案 B：应用内缓存

优点：

- 简单

缺点：

- 无法支撑多实例
- 不适合 QueryTask / 结果缓存

## 10.2 最终结论

### 选择：

> **Redis 7**

## 10.3 用途

- QueryTask 状态辅助缓存
- 热结果缓存
- 队列 broker

---

## 11. 对象存储选型决策

## 11.1 候选方案

### 方案 A：本地文件系统

优点：

- 最简单

缺点：

- 不适合多实例
- 不适合持久化导出与 raw payload

### 方案 B：S3 Compatible Object Storage

优点：

- 标准化
- 易迁移
- 本地可用 MinIO，线上可用托管对象存储

## 11.2 最终结论

### 选择：

> **S3 Compatible Object Storage**

### 本地

- **MinIO**

### 生产

- **AWS S3 / Cloudflare R2 / 阿里云 OSS** 三选一

## 11.3 选择理由

- 本地开发与生产形态统一
- 迁移成本低
- raw payload、导出文件、中间产物都适配

---

## 12. API 契约选型决策

## 12.1 候选方案

### 方案 A：REST + OpenAPI

优点：

- 前后端契约清晰
- 文档、SDK、mock 生态完整

### 方案 B：GraphQL

优点：

- 字段灵活

缺点：

- 对当前 QueryTask / Snapshot 资源型系统收益不大
- 增加复杂度

## 12.2 最终结论

### 选择：

> **REST + OpenAPI 3.1**

## 12.3 选择理由

- 当前资源边界清晰
- 异步任务协议更容易表达
- 和现有文档体系完全对齐

---

## 13. 身份认证选型决策

## 13.1 候选方案

### 方案 A：完全自建 Auth

优点：

- 完全自主

缺点：

- 实现与维护成本高
- 对 V1 非核心

### 方案 B：托管 Auth 服务（Clerk / Auth0 / Supabase Auth）

优点：

- 部署简单
- 集成快

缺点：

- 引入外部依赖

## 13.2 最终结论

### 选择：

> **V1 优先采用托管 Auth 服务**
>
> 在具体供应商上，优先选择 **Clerk**

## 13.3 选择理由

### 对“部署简单”

- 登录、session、前端集成速度最快

### 对“方便扩展”

- 可快速支持登录用户与匿名查询并存

### 对“性能佳”

- 认证不是本系统性能瓶颈

## 13.4 备注

若后续出于合规或成本原因，可替换为自建 Auth，但 V1 不建议自建。

---

## 14. 可观测性选型决策

## 14.1 候选方案

### 方案 A：只打日志

优点：

- 最简单

缺点：

- 排障效率低

### 方案 B：Sentry + 结构化日志 + 基础 metrics

优点：

- 部署成本适中
- 问题定位效率高

### 方案 C：完整 Prometheus + Grafana + Loki + Trace

优点：

- 能力强

缺点：

- 对 V1 偏重

## 14.2 最终结论

### 选择：

> **Sentry + 结构化日志 + 基础 Metrics / Health Check**

## 14.3 选择理由

- 已足够覆盖 V1 QueryTask / Export / API 问题
- 明显比“只打日志”更可用
- 明显比完整自建监控栈更简单

---

## 15. 部署方案选型决策

## 15.1 本地开发

### 方案对比

#### A. 全员手配环境

缺点：

- 易不一致
- 成本高

#### B. Docker Compose

优点：

- 环境统一
- 起步快

### 最终结论

> **本地统一使用 Docker Compose**

---

## 15.2 生产部署

### 候选方案

#### 方案 A：自建 K8s

优点：

- 灵活

缺点：

- 对 V1 明显过重

#### 方案 B：云主机自管 Docker

优点：

- 可控

缺点：

- 运维负担较高

#### 方案 C：Managed PaaS（Render / Railway）

优点：

- 部署简单
- 适合 Web + Worker + Postgres + Redis 组合
- 对 MVP 速度最友好

## 15.3 最终结论

> **生产采用：容器化部署 + Managed PaaS**
>
> **首选 Render，备选 Railway**

## 15.4 选择理由

### 对“部署简单”

- 不需要自己维护 K8s
- Web / Worker / Cron 型服务支持较友好

### 对“方便扩展”

- 后续可分服务扩展
- 若未来规模更大，再迁移到更重平台也不难

### 对“性能佳”

- 对 V1 完全足够
- 瓶颈更多在分析流程和数据质量，不在容器编排本身

---

## 16. 仓库组织方式决策

## 16.1 候选方案

### 方案 A：多仓库

优点：

- 边界清晰

缺点：

- 初期协作成本高

### 方案 B：Monorepo

优点：

- 文档、openapi、mock、前后端更容易协同
- 适合当前产品快速迭代

## 16.2 最终结论

> **Monorepo**

建议结构：

```text
apps/
  web/
  api/
  worker/
packages/
  shared-types/
openapi/
frontend/mock/
doc/
```

---

## 17. 最终技术栈汇总表

| 层 | 最终方案 |
|---|---|
| 前端框架 | React 18 + TypeScript + Vite |
| 前端状态 | TanStack Query + Zustand |
| 前端样式 | Tailwind CSS + shadcn/ui + Radix UI |
| API 后端 | Python 3.12 + FastAPI |
| ORM / Migration | SQLAlchemy 2.x + Alembic |
| Worker / Queue | Dramatiq + Redis |
| 主数据库 | PostgreSQL 16 |
| 检索 | PostgreSQL FTS + GIN / trigram |
| 向量扩展 | pgvector（预埋，不作为 V1 主依赖） |
| 缓存 | Redis 7 |
| 对象存储 | S3 Compatible（本地 MinIO，生产托管对象存储） |
| API 契约 | OpenAPI 3.1 |
| 本地开发 | Docker Compose |
| 生产部署 | Render（首选）/ Railway（备选） |
| 可观测性 | Sentry + 结构化日志 + 基础 Metrics |
| 仓库形态 | Monorepo |

---

## 18. 不采用的方案总结

本次明确不采用：

- **微服务优先**
- **K8s 优先**
- **OpenSearch 作为 V1 必需组件**
- **Temporal**
- **自建 Auth**
- **Next.js 全栈化**

### 原因总结

它们不是不好，而是：

> **对当前 V1 来说，要么部署更复杂，要么增加不必要的系统负担。**

---

## 19. 推荐下一步动作

基于本次拍板，下一步建议立即执行：

1. 按本文件更新后端工程骨架方案
2. 按本文件更新前端工程骨架方案
3. 把 PostgreSQL-only search 策略同步到后续实现计划
4. 初始化 Monorepo 目录结构
5. 准备 Docker Compose 开发环境

---

## 20. 一句话结论

如果目标是：

- **部署简单**
- **方便扩展**
- **性能佳**

那么 **需见** 的 V1 最优技术栈不是“最重型的技术组合”，而是：

> **React + Vite 前端，FastAPI 后端，Dramatiq + Redis 异步任务，PostgreSQL 统一承载事务与基础检索，S3-compatible 对象存储，容器化 + Managed PaaS 部署。**

