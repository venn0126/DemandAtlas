# Demand Atlas｜需见 实施工作分解文档

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 实施工作分解文档
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：任务拆分 / 排期 / 人力分工 / 项目执行管理
- 上游输入：
  - `doc/mvp_delivery_plan.md`
  - `doc/technical_architecture_input.md`
  - `doc/domain_model_and_schema.md`
  - `doc/query_task_and_pipeline_design.md`
  - `doc/api_contract_draft.md`
  - `doc/frontend_component_breakdown.md`

---

## 2. 文档目标

本文档用于把 MVP 交付计划进一步拆解为可执行工作项（WBS）。

本文档重点回答：

1. 要做哪些具体工作包
2. 这些工作包由谁承担更合适
3. 哪些工作包之间存在依赖关系
4. 哪些工作可以并行
5. 每项工作完成后如何判定 Done

---

## 3. 工作分解原则

## 3.1 主链路优先

所有拆分都围绕 V1 主链路：

```text
Query -> QueryTask -> Pipeline -> ResultSnapshot -> Board -> Cluster Detail -> Export
```

## 3.2 可单独验收

每个工作包都应尽量满足：

- 有明确输入
- 有明确输出
- 可独立验收

## 3.3 降低跨角色等待

优先按可并行的能力块拆分，减少：

- 前端等后端
- 后端等分析
- 设计等实现

## 3.4 V1 克制

所有工作包仅围绕 MVP，不把 V1.5+ 的扩展项混入本轮排期。

---

## 4. 角色建议

建议最少按以下角色组织任务：

1. 产品 / 项目 owner
2. 后端
3. 数据 / 算法 / 分析
4. 前端
5. 设计
6. QA / 联调

### 说明

若团队较小，可由一人承担多个角色，但工作包边界仍建议保留。

---

## 5. WBS 总览

建议将 MVP 拆为 8 个一级工作包：

1. 项目基线与配置
2. 数据接入与标准化
3. QueryTask 与 Pipeline
4. 需求聚类与评分
5. 结果快照与导出
6. 前端页面与状态
7. 联调、测试与校准
8. 上线准备与发布

---

## 6. 工作包详解

## 6.1 WP-01 项目基线与配置

### 目标

建立项目基础运行环境与 MVP 基础配置。

### 主要任务

#### WP-01-01 文档冻结与范围确认

- 确认 MVP 边界
- 确认不交付项
- 确认 V1 默认策略

#### WP-01-02 环境与仓库基线

- 仓库结构初始化
- 环境配置
- 基础 CI/CD 骨架（可轻量）

#### WP-01-03 模板与社区池初始化

- 首批 TopicTemplate 清单
- 首批候选 Subreddit 池

#### WP-01-04 配置中心初始化

- 评分参数基础配置
- feature flag 基础配置
- 环境变量与 secrets 约定

### 输入

- PRD
- 技术架构输入

### 输出

- 项目基础结构
- 首批模板与社区池配置
- MVP 范围冻结结论

### 依赖

- 无

### Done 标准

- 所有人对 MVP 范围一致
- 模板池和社区池可供开发使用

---

## 6.2 WP-02 数据接入与标准化

### 目标

建立 Reddit 数据进入系统的可运行链路。

### 主要任务

#### WP-02-01 Reddit Connector 抽象层

- 定义数据接入接口
- 支持社区帖子拉取
- 支持关键词帖子拉取
- 支持评论拉取

#### WP-02-02 Raw 数据落盘

- 原始 payload 保存
- 原始对象追踪

#### WP-02-03 SourcePost / SourceComment 标准化

- 字段映射
- UTC 时间统一
- 可访问性状态映射

#### WP-02-04 内容状态处理

- removed / deleted 降级
- private / banned / nsfw_excluded 处理

#### WP-02-05 检索层写入

- posts index
- comments index
- 基础全文字段

### 输入

- 数据接入策略
- domain model

### 输出

- 可被后续 pipeline 使用的标准化数据

### 依赖

- WP-01

### Done 标准

- 可成功抓取并标准化至少一个模板的候选社区数据
- SourcePost / SourceComment 可用于后续召回

---

## 6.3 WP-03 QueryTask 与 Pipeline

### 目标

建立任务驱动的执行主链路。

### 主要任务

#### WP-03-01 QueryTask 模型与状态流

- `query_tasks`
- `query_task_run_logs`
- 状态机实现

#### WP-03-02 查询标准化与 Query Key

- 输入标准化
- `normalized_query_key`
- 缓存判断逻辑

#### WP-03-03 创建任务接口

- `POST /query-tasks`
- cache hit / async accepted 双路径

#### WP-03-04 任务状态接口

- `GET /query-tasks/{id}`
- 轮询字段输出

#### WP-03-05 Pipeline Orchestrator

- validate
- plan
- fetch
- normalize
- retrieve
- cluster
- score
- snapshot

#### WP-03-06 partial_success / failed 规则实现

- coverage note
- warning code
- failure reason

### 输入

- query task design
- api draft

### 输出

- QueryTask 全链路
- 可轮询、可追踪任务系统

### 依赖

- WP-01
- WP-02（fetch / normalize 依赖）

### Done 标准

- 前端可创建 QueryTask
- 任务状态可轮询
- 成功 / 部分成功 / 失败可区分

---

## 6.4 WP-04 需求聚类与评分

### 目标

把候选内容转成可排序的需求结果。

### 主要任务

#### WP-04-01 retrieve 逻辑实现

- 关键词召回
- 模板召回
- 过滤逻辑

#### WP-04-02 cluster 逻辑实现

- 问题抽取
- 场景抽取
- 痛点抽取
- 同义归并
- 规范标题生成

#### WP-04-03 evidence 抽取

- supporting evidence
- opposing evidence
- 引用规范输出

#### WP-04-04 discussion / attention / growth score 实现

- 平滑
- 归一化
- 样本门槛
- emerging signal

#### WP-04-05 opportunity score 实现

- V1 辅助实现
- 低置信度降级

#### WP-04-06 排序后处理

- tie-break
- 弱信号区分
- 近重复结果处理（可先轻做）

### 输入

- normalized source data
- scoring design

### 输出

- DemandCluster
- ClusterMetricSnapshot
- Board 排序结果

### 依赖

- WP-02
- WP-03

### Done 标准

- 至少一个模板能稳定产出热门榜与增长榜
- 详情页有 supporting evidence

---

## 6.5 WP-05 结果快照与导出

### 目标

让结果变成稳定可读取、可复现、可导出的对象。

### 主要任务

#### WP-05-01 ResultSnapshot 主表与写入逻辑

- `result_snapshots`
- `result_snapshot_clusters`

#### WP-05-02 榜单读取接口

- `GET /result-snapshots/{id}`
- `GET /result-snapshots/{id}/boards/{boardType}`

#### WP-05-03 详情读取接口

- `GET /result-snapshots/{id}/clusters/{clusterId}`

#### WP-05-04 ExportJob 机制

- `POST /export-jobs`
- `GET /export-jobs/{id}`

#### WP-05-05 Markdown / CSV 导出实现

- 快照字段映射
- 导出文件落对象存储

### 输入

- pipeline 输出
- api draft

### 输出

- 稳定结果读取接口
- 导出能力

### 依赖

- WP-03
- WP-04

### Done 标准

- ResultSnapshot 可稳定读取
- 榜单与详情可基于 snapshot 返回
- Markdown / CSV 可成功下载

---

## 6.6 WP-06 前端页面与状态

### 目标

把主链路做成真实可用的前端体验。

### 主要任务

#### WP-06-01 基础布局与路由

- AppShell
- 页面路由结构

#### WP-06-02 一键发现页

- 模板选择
- 时间范围
- view type
- 提交逻辑

#### WP-06-03 定向发现页

- keyword input
- subreddit selector
- language / region hints
- form warnings / errors

#### WP-06-04 查询任务页

- 状态轮询
- 进度展示
- partial_success / failed 展示

#### WP-06-05 结果页

- summary header
- board tabs
- board list
- no result / weak signal / low confidence

#### WP-06-06 详情页

- score panel
- metric panel
- scene / pain point / alternatives
- evidence rendering

#### WP-06-07 导出交互

- export button
- export job polling

#### WP-06-08 匿名 token 管理

- sessionStorage
- 任务恢复

### 输入

- component breakdown
- frontend state notes
- API examples

### 输出

- 完整 V1 前端主链路

### 依赖

- WP-03
- WP-05

### Done 标准

- 用户可走通：首页 -> 查询 -> 任务 -> 结果 -> 详情 -> 导出

---

## 6.7 WP-07 联调、测试与校准

### 目标

把“能跑”提升为“可信可用”。

### 主要任务

#### WP-07-01 API 联调

- QueryTask
- Snapshot
- Boards
- Cluster detail
- Export

#### WP-07-02 状态流联调

- cache hit
- running
- partial_success
- failed
- no result

#### WP-07-03 结果质量校准

- 热门榜人工抽样 review
- 增长榜极端 case 检查
- 机会榜低置信度检查

#### WP-07-04 前端体验校验

- 页面刷新恢复
- 匿名 token 恢复
- error / empty / warning 展示

#### WP-07-05 回归测试

- 主链路回归
- 导出回归

### 输入

- 前后端实现

### 输出

- 联调稳定版本
- 初步校准结果

### 依赖

- WP-04
- WP-05
- WP-06

### Done 标准

- 核心状态流无阻断
- 结果页与详情页字段稳定
- 已覆盖关键边界 case

---

## 6.8 WP-08 上线准备与发布

### 目标

把系统从开发态推进到可灰度上线状态。

### 主要任务

#### WP-08-01 监控与日志接入

- QueryTask 状态监控
- 失败率
- 超时率
- 导出成功率

#### WP-08-02 限流与保护策略

- 查询频控
- 匿名查询频控
- 导出频控

#### WP-08-03 运行手册

- 常见问题
- 故障排查
- 回退策略

#### WP-08-04 上线检查

- 配置检查
- 数据源检查
- 导出链路检查

#### WP-08-05 灰度发布

- 小流量放量
- 异常观察

### 输入

- 联调稳定版本

### 输出

- 可上线版本

### 依赖

- WP-07

### Done 标准

- 基础监控到位
- 可回退
- 可灰度

---

## 7. 按角色拆分的工作包视图

## 7.1 后端

主要承担：

- WP-03
- WP-05
- WP-08 部分

### 关键交付

- QueryTask API
- ResultSnapshot API
- Export API
- 状态机与快照落盘

## 7.2 数据 / 算法 / 分析

主要承担：

- WP-02
- WP-04
- WP-07 部分校准

### 关键交付

- 数据接入
- 聚类与 evidence
- scoring 引擎

## 7.3 前端

主要承担：

- WP-06
- WP-07 前端联调

### 关键交付

- 查询页
- 任务页
- 结果页
- 详情页
- 导出交互

## 7.4 设计

主要承担：

- 首页 / 查询页 / 结果页 / 详情页视觉稿
- 状态组件规范
- badge / banner / card 规范

## 7.5 QA / 联调

主要承担：

- WP-07
- WP-08 发布前检查

---

## 8. 并行关系建议

## 8.1 可并行组 A

- WP-02 数据接入
- WP-06 前端基础页面骨架
- UI 基础组件实现

## 8.2 可并行组 B

- WP-03 QueryTask 骨架
- WP-05 ResultSnapshot 接口骨架

## 8.3 可并行组 C

- WP-04 评分实现
- 榜单 UI 组件实现（可先 mock）

## 8.4 必须串行的关键点

以下顺序不建议打乱：

1. QueryTask 可创建
2. Pipeline 能产出 snapshot
3. Snapshot API 稳定
4. 前端结果页接真实数据

---

## 9. 工作项优先级

## 9.1 P0 级

阻断主链路，不完成不能继续：

- QueryTask 创建与状态轮询
- 数据接入最小闭环
- 热门榜生成
- ResultSnapshot 落盘
- 结果页读取

## 9.2 P1 级

强影响 MVP 质量：

- 增长榜
- 详情页 evidence
- 导出
- partial_success 完整支持

## 9.3 P2 级

可弱化或后移：

- 机会分优化
- 更多模板
- 更精细的反对证据分类

---

## 10. 每阶段的最小演示物

## 10.1 P1 结束演示物

- 创建 QueryTask
- 查看任务状态

## 10.2 P2 结束演示物

- 后端生成至少一个真实榜单结果

## 10.3 P3 结束演示物

- 前端可完整走通主链路

## 10.4 P4 结束演示物

- 展示 partial_success / no result / low confidence

## 10.5 P5 结束演示物

- 灰度可上线版本

---

## 11. Done 定义建议

每个工作项完成时，至少应满足：

1. 代码已提交
2. 核心自测通过
3. 文档与接口一致
4. 关键日志 / 错误码存在
5. 可被下游继续消费

### 说明

“功能写完但没人能接着联调”不算 Done。

---

## 12. 推荐下一步产出

基于本文档，建议继续输出：

1. `doc/release_readiness_checklist.md`
2. 实际排期表 / sprint backlog

---

## 13. 一句话结论

实施工作分解的核心，不是把任务拆得越碎越好，而是：

> **围绕主链路，把后端、数据、前端、联调各自必须完成的工作包拆清楚，并明确谁依赖谁。**
