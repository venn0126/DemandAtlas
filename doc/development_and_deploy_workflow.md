# Demand Atlas｜需见 开发与部署工作流

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 开发与部署工作流
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：本地开发 / 联调 / 测试环境部署 / 灰度验证 / 正式发布
- 上游输入：
  - `doc/tech_stack_decision.md`
  - `doc/monorepo_structure_and_bootstrap.md`
  - `doc/mvp_delivery_plan.md`
  - `doc/release_readiness_checklist.md`

---

## 2. 文档目标

本文档用于回答以下问题：

1. 本地开发后，应该如何把代码部署到测试或线上环境
2. 是不是应该用“把文件推送到服务器目录”的脚本
3. 如何做到部署简单、可回滚、可验证
4. 如何设计开发、测试、灰度、生产的最小流程

---

## 3. 最终结论

先给明确结论：

> **不推荐使用“把本地代码文件直接同步到服务器目录，再手工重启”的方式作为主流程。**

推荐的最佳方案是：

> **Git 作为唯一代码源头 + CI/CD 自动构建 Docker 镜像 + 服务器拉取指定镜像版本并用 Docker Compose 重启服务 + 部署后自动 / 半自动验证。**

也就是说：

- **不是推文件**
- **而是推 Git 提交 / 镜像版本**

---

## 4. 为什么不推荐“文件推送脚本”

你提到的方式通常是：

1. 本地改代码
2. 用 `rsync/scp` 或自定义脚本把代码推到服务器某个目录
3. SSH 上去重启服务

这类方式的问题是：

## 4.1 服务器状态会漂移

你很难保证服务器上的代码：

- 一定来自哪个 commit
- 是否有手工改动
- 是否混入临时文件

## 4.2 回滚困难

如果线上出问题，很难快速回答：

- 回滚到哪个版本
- 回滚后依赖是否一致

## 4.3 前后端 / worker 版本不一致风险高

如果是多服务：

- API
- Worker
- Web

文件推送很容易出现：

- 某个目录更新了
- 某个目录没更新
- 某个服务忘记重启

## 4.4 多人协作不可控

一旦不是一个人开发，文件推送方式会很快失控。

## 4.5 验证链路不完整

你只能知道“代码传上去了”，但很难保证：

- 镜像是否一致
- 依赖是否一致
- 服务是否用新版本真正跑起来了

---

## 5. 最佳方案：Git 驱动的镜像化部署

## 5.1 核心原则

### 原则 A：Git 是唯一真实源

- 服务器不手工改代码
- 服务器不作为开发机
- 所有变更都来自 Git commit

### 原则 B：镜像是部署单位

- 不是把源代码传到服务器运行
- 而是把构建好的镜像版本部署到服务器

### 原则 C：Compose 负责启动服务

- 用 `docker compose pull`
- 用 `docker compose up -d`
- 不手写大量 restart 命令

### 原则 D：部署后一定要验证

最少验证：

- Web 可访问
- API health 正常
- QueryTask 可创建
- ResultSnapshot 链路不报错

---

## 6. 推荐环境划分

建议最少区分 4 个环境：

## 6.1 Local

本地开发环境。

用途：

- 开发
- 单元测试
- mock 联调

## 6.2 Dev

共享开发验证环境。

用途：

- 合并后快速验证
- 前后端联调

## 6.3 Staging / Grey

灰度或预发布环境。

用途：

- 接近生产配置
- 小流量验证
- release readiness 检查

## 6.4 Production

正式生产环境。

用途：

- 正式外部用户使用

---

## 7. 推荐分支策略

V1 建议使用简单可控的分支策略：

## 7.1 分支定义

- `main`：生产稳定分支
- `develop`：开发集成分支
- `feature/*`：功能分支
- `hotfix/*`：线上热修复分支

## 7.2 流程建议

### 日常开发

```text
feature/* -> PR -> develop
```

### 测试 / 集成部署

```text
develop -> auto deploy to dev/staging
```

### 生产发布

```text
develop -> main -> manual approval -> production deploy
```

### 线上热修复

```text
hotfix/* -> main
hotfix/* -> back merge to develop
```

---

## 8. 推荐部署方式

## 8.1 最优 V1 方案

### 代码源

- GitHub 仓库

### 镜像仓库

- GitHub Container Registry（GHCR）

### 运行方式

- 服务器上用 Docker Compose 运行：
  - web
  - api
  - worker
  - postgres
  - redis
  - minio（如需要）

### 部署触发

- GitHub Actions

### 部署行为

1. 代码 push / merge
2. CI 构建镜像
3. 推送镜像到 GHCR
4. SSH 到目标服务器
5. 更新镜像 tag
6. `docker compose pull`
7. `docker compose up -d`
8. 执行 health check 与 smoke test

---

## 9. 服务器目录结构建议

如果使用自管服务器 + Docker Compose，建议在服务器上采用固定目录：

```text
/srv/demand-atlas/
  docker-compose.yml
  .env
  deploy/
    compose/
    scripts/
  logs/
```

### 说明

- 服务器只放：
  - compose 文件
  - env 文件
  - 少量部署脚本
- **不要把完整源代码长期放在服务器作为运行基线**

---

## 10. 本地开发工作流

## 10.1 本地启动流程

### Step 1：启动依赖服务

```bash
docker compose up -d postgres redis minio
```

### Step 2：启动 API

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

### Step 3：启动 Worker

```bash
cd apps/worker
python -m worker.main
```

### Step 4：启动 Web

```bash
cd apps/web
pnpm dev
```

## 10.2 本地验证顺序

每次完成一个功能后建议验证：

1. 页面能打开
2. API 健康检查通过
3. QueryTask 创建成功
4. 任务状态能变化
5. 对应页面状态渲染正常

## 10.3 本地提交前检查

提交前建议最少执行：

- lint
- format
- 基础单元测试
- 必要的 mock 页面自检

---

## 11. 标准开发流程

## 11.1 日常流程

```text
拉 develop 最新代码
  -> 新建 feature 分支
  -> 本地开发
  -> 本地验证
  -> 提交 commit
  -> push 到远程
  -> 提 PR 到 develop
  -> 通过 review / CI
  -> merge 到 develop
```

## 11.2 develop 分支合并后

建议自动触发：

- dev 环境部署
- 或 staging 环境部署（视资源情况）

---

## 12. 推荐 CI/CD 流程

## 12.1 CI 阶段

触发条件：

- PR
- push 到 develop
- push 到 main

CI 内容建议：

### 通用检查

- 格式检查
- lint
- 基础测试

### 构建检查

- 构建 web
- 构建 api 镜像
- 构建 worker 镜像

### OpenAPI / mock 一致性检查（可后加）

- 接口契约变更提醒

## 12.2 CD 阶段

### develop -> dev/staging

自动部署

### main -> production

建议：

- 手工 approval 后部署

---

## 13. GitHub Actions 推荐流程

## 13.1 Build Workflow

建议职责：

1. checkout
2. 安装依赖
3. 跑 lint / test
4. 构建 Docker 镜像
5. push 到 GHCR

## 13.2 Deploy Workflow

建议职责：

1. 通过 SSH 登录服务器
2. 切换到 `/srv/demand-atlas`
3. 更新镜像 tag 或 `.env`
4. 执行：

```bash
docker compose pull
docker compose up -d --remove-orphans
```

5. 跑 health check
6. 输出部署结果

---

## 14. 镜像版本策略

## 14.1 推荐 tag 策略

建议每次构建至少打两个 tag：

- `git-sha`
- `branch-latest`

例如：

- `ghcr.io/org/demand-atlas-api:sha-abc123`
- `ghcr.io/org/demand-atlas-api:develop-latest`

## 14.2 生产建议

生产部署优先使用：

- 明确的 `git-sha tag`

不要只用：

- `latest`

### 原因

- 回滚更容易
- 可追踪性更好

---

## 15. Docker Compose 部署策略

## 15.1 服务划分

建议 Compose 中包含：

- `web`
- `api`
- `worker`
- `postgres`
- `redis`
- `minio`（可选）

## 15.2 重启方式

推荐标准方式：

```bash
docker compose pull
docker compose up -d --remove-orphans
```

不推荐：

- 逐个手工 stop / start
- 直接 `docker restart` 某个容器作为主策略

## 15.3 数据持久化

以下必须做 volume 持久化：

- PostgreSQL data
- MinIO data

Redis 是否持久化按需求决定，但建议至少保留基础持久配置。

---

## 16. 服务器验证流程

每次部署后，建议按以下顺序验证：

## 16.1 基础服务验证

- `docker compose ps`
- 核心容器都为 healthy / running

## 16.2 API 验证

- health endpoint 正常
- OpenAPI endpoint 正常（如开放）

## 16.3 Web 验证

- 首页可访问
- 核心静态资源加载正常

## 16.4 主链路 smoke test

建议最少验证：

1. 一键发现提交 QueryTask
2. QueryTask 状态可变化
3. ResultSnapshot 可读取
4. 热门榜可展示

## 16.5 导出链路验证（上线前或变更相关时）

- 触发导出
- 导出任务成功
- 文件可下载

---

## 17. 回滚策略

## 17.1 推荐回滚方式

回滚应以“镜像版本”为单位，不以“文件目录”为单位。

### 标准回滚步骤

1. 确定上一个稳定 `git-sha`
2. 修改部署使用的镜像 tag
3. 执行：

```bash
docker compose pull
docker compose up -d
```

4. 重跑 health check
5. 重跑主链路 smoke test

## 17.2 什么时候要回滚

以下情况建议评估立即回滚：

- QueryTask 大面积失败
- ResultSnapshot 无法读取
- 权限问题
- 热门榜大面积失真

---

## 18. 是否需要“推送脚本”

## 18.1 结论

### 不建议做：

- “把代码文件推到服务器目录”的主部署脚本

### 可以做：

- **部署辅助脚本**

例如：

- `scripts/dev-up.sh`
- `scripts/deploy-staging.sh`
- `scripts/smoke-test.sh`

这些脚本的职责应是：

- 调用标准流程
- 不是替代标准流程

## 18.2 允许的脚本类型

### 本地辅助脚本

- 启动本地依赖
- 初始化种子数据
- 跑 smoke test

### 服务器部署脚本

- 拉取镜像
- 重启 compose
- 跑 health check

### CI 调用脚本

- 封装固定部署命令

---

## 19. 最终推荐工作流

## 19.1 开发到测试环境

```text
本地开发
  -> 本地验证
  -> push feature 分支
  -> PR -> merge develop
  -> GitHub Actions build 镜像
  -> push GHCR
  -> 自动部署到 dev/staging
  -> 自动 / 手工 smoke test
```

## 19.2 测试到生产环境

```text
develop 稳定
  -> merge main
  -> GitHub Actions build 生产镜像
  -> 手工 approval
  -> 部署到 production
  -> health check
  -> smoke test
  -> 灰度观察
```

---

## 20. V1 最优方案总结

如果你当前明确是：

- 一台或少量服务器
- 希望流程稳
- 希望后续能扩

那么最优方案就是：

> **本地开发 + Git 提交 + CI 构建镜像 + 服务器拉镜像并用 Docker Compose 重启验证**

而不是：

> **本地改完代码后直接把文件推到服务器目录并手工重启**

---

## 21. 推荐下一步动作

基于本方案，建议立即落地以下工程文件：

1. `docker-compose.yml`
2. `.env.example`
3. 根目录 `README.md`
4. `scripts/dev-up.sh`
5. `scripts/dev-down.sh`
6. `scripts/smoke-test.sh`
7. GitHub Actions workflow 草稿

---

## 22. 一句话结论

对于 **需见** 当前阶段，最佳开发与部署方式不是“传代码到服务器”，而是：

> **让服务器永远只运行已构建、可回滚、可验证的镜像版本。**

