# Demand Atlas｜需见 前端 Mock 搭建执行清单

## 1. 说明

本清单用于按 `doc/sprint_01_backlog.md` 的前端与 mock 相关工作项，逐阶段执行、验证与勾选。

当前范围仅包含：

- FE-01 前端项目骨架初始化
- FE-02 基础 UI 组件骨架
- FE-03 首页 / 一键发现页 / 定向发现页骨架
- FE-04 查询任务页骨架
- FE-05 结果页与详情页骨架
- QA-01 Mock 对照检查

当前阶段：`已完成`

---

## 2. 执行清单

- [x] FE-01 前端项目骨架初始化
- [x] FE-02 基础 UI 组件骨架
- [x] FE-03 首页 / 一键发现页 / 定向发现页骨架
- [x] FE-04 查询任务页骨架
- [x] FE-05 结果页与详情页骨架
- [x] QA-01 Mock 对照检查

---

## 3. 阶段验证记录

### FE-01

- 状态：已完成
- 验证项：
  - [x] 前端项目可启动
  - [x] 首页可访问
  - [x] 路由结构与页面规划一致
- 验证结果：
  - `apps/web` 已基于 Vite + React + TypeScript 初始化
  - 已接入 `react-router-dom`、`@tanstack/react-query`、`zustand`
  - 已建立 `AppShell`、页面路由骨架、mock adapter、基础 store
  - `pnpm build` 通过
  - `pnpm lint` 通过
  - 本地开发服务已在 `http://127.0.0.1:4173/` 启动验证
  - `curl -I` 验证首页及以下路由均返回 `HTTP/1.1 200 OK`
    - `/`
    - `/discover/one-click`
    - `/discover/directed`
    - `/tasks/:queryTaskId`
    - `/results/:resultSnapshotId`
    - `/results/:resultSnapshotId/clusters/:clusterId`
    - `/settings`

### FE-02

- 状态：已完成
- 验证项：
  - [x] 基础 UI 组件可复用
  - [x] 能支撑查询页和结果页骨架
- 验证结果：
  - 已实现 `Button`、`Input`、`Card`、`Badge`、`Banner`、`Tabs`
  - 已实现 `LoadingState`、`ErrorState`、`EmptyState`
  - 查询页、任务页、结果页、详情页、设置页均已接入这些通用组件
  - `pnpm build` 通过
  - `pnpm lint` 通过

### FE-03

- 状态：已完成
- 验证项：
  - [x] 首页、一键发现页、定向发现页骨架完成
  - [x] 可基于 mock 完成页面跳转
- 验证结果：
  - 首页已接入模板推荐读取
  - 一键发现页已接入模板列表、模板说明、async/cache-hit 提交模式
  - 定向发现页已接入关键词 / subreddit / region hint / 提交模式
  - 已接入 `query-task.create.async.json`
  - 已接入 `query-task.create.cache-hit.json`
  - 已接入过宽输入错误分支
  - 已实现匿名 token 的 `sessionStorage` 持久化
  - 页面提交后已具备跳往 `/tasks/:queryTaskId` 或 `/results/:resultSnapshotId` 的代码路径
  - `pnpm build` 通过
  - `pnpm lint` 通过
  - 查询页与目标路由本地访问返回 `HTTP/1.1 200 OK`

### FE-04

- 状态：已完成
- 验证项：
  - [x] pending / running / partial_success / failed 页面状态完整
  - [x] 可以用 mock 数据演示状态变化
- 验证结果：
  - 查询任务页已接入状态场景选择器
  - 已接入 `pending` / `running` / `partial_success` / `success` / `failed`
  - 已实现状态卡、阶段、进度条、Query Summary、Coverage Banner、Warnings、Action Bar、Failed Error Panel
  - `partial_success` / `success` 已提供 `View Result` 入口
  - `pnpm build` 通过
  - `pnpm lint` 通过
  - 查询任务页本地访问返回 `HTTP/1.1 200 OK`

### FE-05

- 状态：已完成
- 验证项：
  - [x] 结果页与详情页骨架完成
  - [x] 可以从列表点击进入详情
- 验证结果：
  - 结果页已接入 summary、coverage、freshness、board tabs、board list、empty state
  - 详情页已接入 flags、scores、metrics、scenes、pain points、alternatives、supporting / opposing evidence
  - 已实现从结果列表进入详情页的链接
  - `pnpm build` 通过
  - `pnpm lint` 通过
  - 结果页与详情页本地访问返回 `HTTP/1.1 200 OK`

### QA-01

- 状态：已完成
- 验证项：
  - [x] mock 结构与文档一致
  - [x] 字段命名覆盖到当前前端主链路
  - [x] 状态覆盖完整
- 验证结果：
  - 已对照 `frontend/mock/manifest.json`
  - 当前前端主链路已覆盖：
    - `topic_templates`
    - `query_task_create`
    - `query_task_status`
    - `result_snapshot`
    - `cluster_detail`
  - 当前未接入但不属于本轮必做主链路：
    - `export_jobs`
    - `errors` 中的 401 / 403 / 404 专项页面
  - 已接入的关键状态：
    - 查询创建：`cache-hit` / `async` / `too-broad`
    - 任务状态：`pending` / `running` / `partial_success` / `success` / `failed`
    - 结果状态：`normal` / `empty` / `partial`
    - 榜单状态：`hot` / `growth` / `opportunity` / `empty`
    - 详情状态：`normal` / `partial-evidence`
  - 代码层已通过：
    - `pnpm build`
    - `pnpm lint`

---

## 4. 当前阶段总结

本轮已按清单完成基于现有 mock 数据的前端主链路搭建：

- 首页
- 一键发现页
- 定向发现页
- 查询任务页
- 结果页
- 详情页

当前实现特点：

- 全程不依赖后端接口
- 严格以 `frontend/mock/` 现有数据为驱动
- 已具备从查询入口到结果详情的完整前端演示链路
