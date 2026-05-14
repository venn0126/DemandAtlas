# Demand Atlas｜需见 Sprint 01 Backlog

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 Sprint 01 Backlog
- 文档版本：V1.0
- 更新时间：2026-05-12
- Sprint 目标阶段：M1 骨架完成
- 上游输入：
  - `doc/mvp_delivery_plan.md`
  - `doc/implementation_work_breakdown.md`
  - `doc/domain_model_and_schema.md`
  - `doc/query_task_and_pipeline_design.md`
  - `doc/api_contract_draft.md`
  - `openapi/openapi.yaml`
  - `frontend/mock/`

---

## 2. Sprint 01 目标

Sprint 01 的目标不是做出完整产品，而是完成：

> **Demand Atlas｜需见 的最小系统骨架，让 QueryTask -> ResultSnapshot 这条主链路在工程层面具备可实现基础。**

### Sprint 01 成功定义

本轮结束时，团队应具备以下能力：

1. 有可用的后端项目骨架
2. 有 QueryTask 主表、ResultSnapshot 主表等核心 schema
3. 有 TopicTemplate 基础读取能力
4. 有 `POST /query-tasks` 与 `GET /query-tasks/{id}` 骨架
5. 有 `GET /result-snapshots/{id}` 骨架
6. 前端可以基于 mock 跑通页面骨架
7. 前后端对主链路资源命名与字段口径一致

---

## 3. Sprint 01 范围

## 3.1 本轮包含

### 后端

- 项目骨架
- 核心表结构第一版
- QueryTask 基础状态流
- TopicTemplate 基础接口
- ResultSnapshot 基础读取接口

### 前端

- 路由骨架
- 首页 / 查询页 / 任务页 / 结果页 / 详情页骨架
- mock 驱动状态流

### 数据 / 分析

- Reddit Connector 抽象设计
- TopicTemplate 首批种子定义
- 候选社区池首批清单

### 设计

- 低保真线框确认
- UI 基础组件规范确认

## 3.2 本轮不包含

- 完整 fetch / normalize / cluster / score 实现
- 真正可用的热门榜结果
- 导出链路正式实现
- 登录体系完整实现
- 订阅 / 收藏 / 需求库

---

## 4. Sprint 01 进入条件

以下条件满足后，Sprint 01 可正式启动：

- [ ] 产品名已定稿：Demand Atlas｜需见
- [ ] PRD V1.1 已冻结
- [ ] 技术输入文档已完成
- [ ] OpenAPI 初稿已完成
- [ ] 前端 mock 数据已准备
- [ ] Sprint 01 范围无争议

---

## 5. Sprint 01 交付物

## 5.1 必交付物

1. 后端仓库基础结构
2. 前端仓库基础结构
3. 数据库核心表第一版 migration
4. OpenAPI 可用于本轮接口实现的最小版本
5. TopicTemplate 种子数据
6. QueryTask / ResultSnapshot 基础 API
7. 前端低保真可运行页面骨架

## 5.2 建议交付物

1. 开发环境 README
2. 本地 mock 启动方式说明
3. 接口字段对照表

---

## 6. 按角色拆分的 Sprint 01 工作项

## 6.1 后端工作项

### BE-01 项目骨架初始化

#### 目标

建立后端服务基本结构。

#### 内容

- 初始化服务目录
- 配置基础运行环境
- 配置日志基础能力
- 配置环境变量读取

#### 输出

- 可启动后端服务

#### Done 标准

- 本地能启动服务
- 有健康检查基础能力

---

### BE-02 数据库基础 migration

#### 目标

建立 Sprint 01 所需核心表。

#### 内容

优先落以下表：

- `topic_templates`
- `topic_template_versions`
- `topic_template_version_subreddits`
- `query_tasks`
- `query_task_run_logs`
- `result_snapshots`

#### 输出

- migration 脚本
- 本地数据库可初始化

#### Done 标准

- migration 可执行
- 表结构与 `doc/domain_model_and_schema.md` 一致

---

### BE-03 TopicTemplate 读取接口

#### 目标

支持前端加载模板。

#### 内容

- `GET /api/v1/topic-templates`
- `GET /api/v1/topic-templates/{template_id}`

#### 输出

- 基础模板 API

#### Done 标准

- 接口返回结构符合 `openapi/openapi.yaml`
- 可返回种子模板数据

---

### BE-04 QueryTask 创建接口骨架

#### 目标

让前端可以创建任务。

#### 内容

- `POST /api/v1/query-tasks`
- 参数基础校验
- `query_task_id` 生成
- cache hit 与 async accepted 的基础分支占位

#### 输出

- QueryTask 创建 API

#### Done 标准

- 支持 one_click 请求体
- 支持 directed 请求体
- 返回结构与 OpenAPI 一致

---

### BE-05 QueryTask 状态查询接口骨架

#### 目标

让前端可以轮询任务状态。

#### 内容

- `GET /api/v1/query-tasks/{query_task_id}`
- 支持基础状态读取
- 返回 progress 结构占位

#### 输出

- QueryTask 状态 API

#### Done 标准

- 可返回 pending / running / success / failed mock 状态

---

### BE-06 ResultSnapshot 基础读取接口骨架

#### 目标

让结果页可以读取快照摘要。

#### 内容

- `GET /api/v1/result-snapshots/{result_snapshot_id}`

#### 输出

- ResultSnapshot summary API

#### Done 标准

- 返回结构与 OpenAPI 一致
- 可返回 mock 或静态种子结果

---

## 6.2 前端工作项

### FE-01 前端项目骨架初始化

#### 目标

建立前端可运行框架。

#### 内容

- 路由基础结构
- 全局 layout
- 状态管理基础结构
- API client / mock adapter 基础结构

#### 输出

- 可运行前端项目

#### Done 标准

- 首页可访问
- 路由结构与页面规划一致

---

### FE-02 基础 UI 组件骨架

#### 目标

建立首批基础组件。

#### 内容

- Button
- Input
- Card
- Badge
- Banner
- LoadingState
- ErrorState
- EmptyState

#### 输出

- 基础 UI 组件库第一版

#### Done 标准

- 能支撑查询页和结果页骨架

---

### FE-03 首页 / 一键发现页 / 定向发现页骨架

#### 目标

搭建查询入口页。

#### 内容

- 首页
- 一键发现页
- 定向发现页
- 模板列表读取
- 表单输入与提交动作占位

#### 输出

- 可点击的查询入口页面

#### Done 标准

- 可以基于 mock 完成页面跳转

---

### FE-04 查询任务页骨架

#### 目标

搭建 QueryTask 状态页。

#### 内容

- pending / running / partial_success / failed 页面状态
- progress 区块
- action bar

#### 输出

- 可基于 mock 轮换状态展示

#### Done 标准

- 可以用 mock 数据演示状态变化

---

### FE-05 结果页与详情页骨架

#### 目标

搭建结果主链路页面。

#### 内容

- ResultSummaryHeader
- BoardTabs
- BoardList
- ClusterDetail 页面骨架

#### 输出

- 可用 mock 展示榜单与详情

#### Done 标准

- 可以从列表点击进入详情

---

## 6.3 数据 / 分析工作项

### DS-01 Reddit Connector 抽象定义

#### 目标

明确数据接入边界。

#### 内容

- 定义 Connector 能力接口
- 定义 fetch 输入与输出结构
- 明确 Raw / Normalized 分层边界

#### 输出

- Connector 接口设计说明

#### Done 标准

- 后端与数据侧对接方式无歧义

---

### DS-02 首批 TopicTemplate 种子数据

#### 目标

让一键发现有真实模板可选。

#### 内容

- 至少准备 3–5 个模板
- 每个模板包含：
  - 名称
  - 描述
  - 候选社区池
  - 默认语言

#### 输出

- 可导入数据库的模板种子

#### Done 标准

- 前端模板接口能读到首批模板

---

### DS-03 首批候选社区池清单

#### 目标

为后续 fetch / retrieve 阶段准备基础数据范围。

#### 内容

- 选定首批社区
- 标记是否 NSFW / private / banned 风险
- 标记大类归属

#### 输出

- 候选社区清单

#### Done 标准

- 至少可覆盖首批模板

---

## 6.4 设计工作项

### DE-01 页面线框确认

#### 目标

把线框说明转为可对齐的页面结构稿。

#### 内容

- 首页
- 一键发现页
- 定向发现页
- 查询任务页
- 结果页
- 详情页

#### 输出

- 低保真线框

#### Done 标准

- 前端可按线框直接搭页面骨架

---

### DE-02 基础组件视觉规范确认

#### 目标

固定 V1 的基础视觉组件。

#### 内容

- Button
- Card
- Badge
- Banner
- Tabs
- Form input

#### 输出

- 组件样式规范

#### Done 标准

- 前端可开始样式实现

---

## 6.5 QA / 联调工作项

### QA-01 Mock 对照检查

#### 目标

确认 mock 数据与文档一致。

#### 内容

- 检查 mock 结构
- 检查字段命名
- 检查状态覆盖

#### 输出

- mock 检查结果

#### Done 标准

- 关键页面可用 mock 完成演示

---

### QA-02 基础联调准备

#### 目标

为 Sprint 02 真正接口联调做好准备。

#### 内容

- 定义联调检查项
- 定义最小验收数据

#### 输出

- Sprint 02 联调入口清单

#### Done 标准

- 前后端都知道下轮联调从哪里开始

---

## 7. Sprint 01 依赖关系图

```text
WP-01 项目基线
  -> BE-02 数据库 migration
  -> BE-03 TopicTemplate API
  -> DS-02 模板种子

BE-02 + DS-02
  -> BE-03 TopicTemplate API

BE-04 QueryTask 创建
  -> BE-05 QueryTask 状态
  -> FE-04 查询任务页

BE-06 ResultSnapshot 摘要
  -> FE-05 结果页与详情页骨架

DE-01 线框确认
  -> FE-03 / FE-04 / FE-05
```

---

## 8. 可并行执行建议

## 8.1 后端与前端可并行

前端不必等待后端完成，可先使用：

- `frontend/mock/`

推进：

- 首页
- 查询页
- 任务页
- 结果页骨架

## 8.2 数据与后端可并行

- DS-02 模板种子
- DS-03 社区清单

可与数据库和接口骨架同步推进。

## 8.3 设计与前端可并行

- 线框确认
- 组件规范确认

可与前端基础组件搭建同步推进。

---

## 9. Sprint 01 风险点

## 9.1 风险 A：范围漂移

表现：

- 在骨架阶段就加入 clustering / scoring 细节实现

控制建议：

- Sprint 01 只做骨架，不追求完整结果质量

## 9.2 风险 B：接口过早追求完美

表现：

- 花太多时间在 OpenAPI 细枝末节上

控制建议：

- 以主链路可用为先

## 9.3 风险 C：前端等待后端

表现：

- 页面搭建被真实接口阻塞

控制建议：

- 强制使用 mock 数据并行推进

---

## 10. Sprint 01 验收标准

## 10.1 最小演示流

本轮至少应能演示：

1. 首页进入一键发现页
2. 选择模板并提交
3. 进入 QueryTask 页面
4. 模拟 running -> success
5. 进入结果页
6. 点击榜单项进入详情页

## 10.2 后端验收

- [ ] QueryTask 创建接口可用
- [ ] QueryTask 状态接口可用
- [ ] TopicTemplate 接口可用
- [ ] ResultSnapshot summary 接口可用

## 10.3 前端验收

- [ ] 页面路由完整
- [ ] QueryTask 状态流可展示
- [ ] 结果页骨架可展示
- [ ] 详情页骨架可展示

## 10.4 文档验收

- [ ] 实际接口与 OpenAPI 草案未明显偏离
- [ ] mock 数据与页面结构一致

---

## 11. Sprint 01 结束后应该具备的输入

Sprint 01 完成后，Sprint 02 应直接基于以下输入继续：

1. 后端骨架已可运行
2. 前端页面骨架已可运行
3. TopicTemplate / QueryTask / ResultSnapshot 资源已落地
4. mock 流程已经跑通

这将为 Sprint 02 进入：

- fetch
- normalize
- retrieve
- cluster
- score

做好准备。

---

## 12. 推荐下一步产出

基于本文档，建议继续输出：

1. `doc/sprint_02_backlog.md`
2. 真实项目任务看板导入格式

---

## 13. 一句话结论

Sprint 01 的核心，不是做出完整产品，而是：

> **把 Demand Atlas｜需见 的主链路骨架和跨角色协作接口先搭起来。**

