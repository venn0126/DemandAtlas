# Demand Atlas｜需见 项目文档总索引

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 项目文档总索引
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用对象：产品、设计、前端、后端、数据、QA、项目负责人

---

## 2. 文档目标

本文档用于作为 **Demand Atlas｜需见** 的统一文档入口。

目标：

1. 让团队快速找到当前阶段最该看的文档
2. 按角色与阶段组织已有文档
3. 降低后续交接、对齐、 onboarding 成本

---

## 3. 项目一句话

**Demand Atlas｜需见** 是一个面向需求发现的研究工作台，用于在指定时间窗口内，从 Reddit 中发现高讨论、高关注或快速增长的真实需求，并输出结构化需求卡片、榜单和证据。

---

## 4. 建议阅读顺序

如果你第一次进入这个项目，建议按以下顺序阅读：

### 第 0 步：看当前 handoff

0. `doc/current_status_and_next_steps.md`

### 第 1 步：理解产品是什么

1. `doc/prd_reddit_needs_discovery.md`
2. `doc/prd_review_and_edge_cases.md`

### 第 2 步：理解系统怎么设计

3. `doc/technical_architecture_input.md`
4. `doc/domain_model_and_schema.md`
5. `doc/query_task_and_pipeline_design.md`
6. `doc/scoring_engine_design.md`

### 第 3 步：理解接口和前端怎么承接

7. `doc/api_contract_draft.md`
8. `doc/openapi_v1_outline.md`
9. `doc/openapi_example_responses.md`
10. `doc/information_architecture_and_state_flow.md`
11. `doc/frontend_state_management_notes.md`
12. `doc/frontend_component_breakdown.md`
13. `doc/page_wireframe_notes.md`
14. `doc/ui_style_guide.md`

### 第 4 步：理解交付怎么推进

15. `doc/mvp_delivery_plan.md`
16. `doc/implementation_work_breakdown.md`
17. `doc/sprint_01_backlog.md`
18. `doc/sprint_02_backlog.md`
19. `doc/sprint_03_backlog.md`

### 第 5 步：理解上线与灰度怎么治理

20. `doc/release_readiness_checklist.md`
21. `doc/grey_release_observation_template.md`
22. `doc/result_quality_review_template.md`
23. `doc/post_launch_issue_triage.md`

---

## 5. 按文档类别分类

## 5.0 当前状态与 handoff

### 0. 当前进度与下一步执行说明

- `doc/current_status_and_next_steps.md`

用途：

- 下次继续时快速恢复上下文
- 明确当前已完成内容
- 明确下一步应直接开始的工程动作

## 5.1 产品定义类

### 1. PRD

- `doc/prd_reddit_needs_discovery.md`

用途：

- 定义产品范围、功能边界、核心流程、MVP 范围

### 2. PRD Review 与边界验证

- `doc/prd_review_and_edge_cases.md`

用途：

- 检查主 PRD 是否足以支撑技术与设计
- 记录边界 case 与必须补齐的定义

---

## 5.2 技术与系统设计类

### 2.5 技术选型最终拍板

- `doc/tech_stack_decision.md`

用途：

- 最终确认前后端、数据、部署与基础设施技术栈

### 3. 技术架构输入文档

- `doc/technical_architecture_input.md`

用途：

- 统一系统边界、核心对象、任务流、服务拆分思路

### 4. 领域模型与 Schema 文档

- `doc/domain_model_and_schema.md`

用途：

- 定义核心表结构、实体关系、索引建议

### 5. QueryTask 与 Pipeline 文档

- `doc/query_task_and_pipeline_design.md`

用途：

- 定义 QueryTask 状态机、阶段流、partial_success / failed 逻辑

### 6. 评分引擎设计文档

- `doc/scoring_engine_design.md`

用途：

- 定义 discussion / attention / growth / opportunity 分数与排序逻辑

---

## 5.3 API 与工程接口类

### 7. API Contract Draft

- `doc/api_contract_draft.md`

用途：

- 给前后端联调与接口实现提供可读契约草案

### 8. OpenAPI Outline

- `doc/openapi_v1_outline.md`

用途：

- 为正式 OpenAPI 文件编写提供结构蓝本

### 9. OpenAPI Example Responses

- `doc/openapi_example_responses.md`

用途：

- 提供关键接口的成功 / 失败 / 降级示例响应

### 10. 正式 OpenAPI 文件

- `openapi/openapi.yaml`

用途：

- 机器可读接口契约
- SDK / mock / 联调基础

---

## 5.4 前端状态、组件与页面设计类

### 11. 信息架构与状态流

- `doc/information_architecture_and_state_flow.md`

用途：

- 定义页面结构、页面状态、前后端状态映射

### 12. 前端状态管理说明

- `doc/frontend_state_management_notes.md`

用途：

- 定义前端 session / task / snapshot / UI 状态分层

### 13. 前端组件拆解文档

- `doc/frontend_component_breakdown.md`

用途：

- 按页面和组件层拆解前端实现

### 14. 页面线框说明

- `doc/page_wireframe_notes.md`

用途：

- 为低保真原型和页面骨架实现提供结构说明

### 15. UI 风格定稿文档

- `doc/ui_style_guide.md`

用途：

- 固定 Research Console 风格与基础视觉规范

---

## 5.5 工程启动与部署类

### 15.1 Monorepo 结构与启动方案

- `doc/monorepo_structure_and_bootstrap.md`

用途：

- 指导仓库初始化、目录结构和本地启动方式

### 15.2 开发与部署工作流

- `doc/development_and_deploy_workflow.md`

用途：

- 固定本地开发、CI/CD、服务器部署、验证与回滚流程

---

## 5.6 项目交付推进类

### 16. MVP 交付计划

- `doc/mvp_delivery_plan.md`

用途：

- 定义阶段目标、范围、里程碑、依赖和验收方式

### 17. 实施工作分解文档

- `doc/implementation_work_breakdown.md`

用途：

- 形成跨角色 WBS

### 18. Sprint 01 Backlog

- `doc/sprint_01_backlog.md`

用途：

- 骨架阶段执行清单

### 19. Sprint 02 Backlog

- `doc/sprint_02_backlog.md`

用途：

- 真实分析闭环阶段执行清单

### 20. Sprint 03 Backlog

- `doc/sprint_03_backlog.md`

用途：

- 结果质量提升与上线前收束阶段执行清单

---

## 5.7 上线、灰度与治理类

### 21. 上线准备检查清单

- `doc/release_readiness_checklist.md`

用途：

- 上线前统一核查 Must Have / Should Have / 风险接受项

### 22. 灰度发布观察模板

- `doc/grey_release_observation_template.md`

用途：

- 灰度期间日报与放量判断依据

### 23. 结果质量评审模板

- `doc/result_quality_review_template.md`

用途：

- 对榜单、聚类、evidence 做结构化抽检

### 24. 上线后问题分级与处置手册

- `doc/post_launch_issue_triage.md`

用途：

- 线上问题分级、止血、修复与回滚决策

---

## 5.8 前端 Mock 资产类

### 25. Mock 说明

- `frontend/mock/README.md`

### 26. Mock 目录清单

- `frontend/mock/manifest.json`

### 27. Mock 数据文件

- `frontend/mock/*.json`

用途：

- 前端不等后端即可搭主链路
- 联调前用于页面与状态实现

---

## 6. 按角色推荐阅读

## 6.1 产品经理

优先阅读：

1. `doc/current_status_and_next_steps.md`
1. `doc/prd_reddit_needs_discovery.md`
2. `doc/prd_review_and_edge_cases.md`
3. `doc/mvp_delivery_plan.md`
4. `doc/sprint_01_backlog.md`
5. `doc/sprint_02_backlog.md`
6. `doc/sprint_03_backlog.md`
7. `doc/release_readiness_checklist.md`

## 6.2 后端工程师

优先阅读：

1. `doc/current_status_and_next_steps.md`
1. `doc/technical_architecture_input.md`
2. `doc/domain_model_and_schema.md`
3. `doc/query_task_and_pipeline_design.md`
4. `doc/api_contract_draft.md`
5. `openapi/openapi.yaml`
 6. `doc/tech_stack_decision.md`
 7. `doc/monorepo_structure_and_bootstrap.md`
 8. `doc/development_and_deploy_workflow.md`
 9. `doc/implementation_work_breakdown.md`

## 6.3 数据 / 算法工程师

优先阅读：

1. `doc/current_status_and_next_steps.md`
1. `doc/technical_architecture_input.md`
2. `doc/domain_model_and_schema.md`
3. `doc/query_task_and_pipeline_design.md`
4. `doc/scoring_engine_design.md`
5. `doc/result_quality_review_template.md`

## 6.4 前端工程师

优先阅读：

1. `doc/current_status_and_next_steps.md`
1. `doc/api_contract_draft.md`
2. `openapi/openapi.yaml`
3. `doc/openapi_example_responses.md`
4. `doc/information_architecture_and_state_flow.md`
5. `doc/frontend_state_management_notes.md`
6. `doc/frontend_component_breakdown.md`
7. `doc/page_wireframe_notes.md`
 8. `doc/ui_style_guide.md`
 9. `frontend/mock/README.md`

## 6.5 设计师

优先阅读：

1. `doc/current_status_and_next_steps.md`
1. `doc/prd_reddit_needs_discovery.md`
2. `doc/information_architecture_and_state_flow.md`
3. `doc/frontend_component_breakdown.md`
4. `doc/page_wireframe_notes.md`
5. `doc/ui_style_guide.md`

## 6.6 QA / 联调负责人

优先阅读：

1. `doc/current_status_and_next_steps.md`
1. `doc/api_contract_draft.md`
2. `doc/openapi_example_responses.md`
3. `doc/release_readiness_checklist.md`
4. `doc/result_quality_review_template.md`
5. `doc/grey_release_observation_template.md`
6. `doc/post_launch_issue_triage.md`

---

## 7. 按阶段推荐阅读

## 7.1 立项 / 范围确认阶段

- `doc/current_status_and_next_steps.md`
- `doc/prd_reddit_needs_discovery.md`
- `doc/prd_review_and_edge_cases.md`

## 7.2 技术方案阶段

- `doc/current_status_and_next_steps.md`
- `doc/technical_architecture_input.md`
- `doc/domain_model_and_schema.md`
- `doc/query_task_and_pipeline_design.md`
- `doc/scoring_engine_design.md`
- `doc/tech_stack_decision.md`

## 7.3 接口与前端协作阶段

- `doc/current_status_and_next_steps.md`
- `doc/api_contract_draft.md`
- `doc/openapi_v1_outline.md`
- `openapi/openapi.yaml`
- `doc/frontend_state_management_notes.md`
- `frontend/mock/README.md`

## 7.4 页面设计与前端实现阶段

- `doc/current_status_and_next_steps.md`
- `doc/information_architecture_and_state_flow.md`
- `doc/frontend_component_breakdown.md`
- `doc/page_wireframe_notes.md`
- `doc/ui_style_guide.md`

## 7.5 项目执行与排期阶段

- `doc/current_status_and_next_steps.md`
- `doc/mvp_delivery_plan.md`
- `doc/implementation_work_breakdown.md`
- `doc/sprint_01_backlog.md`
- `doc/sprint_02_backlog.md`
- `doc/sprint_03_backlog.md`

## 7.6 灰度与上线阶段

- `doc/current_status_and_next_steps.md`
- `doc/release_readiness_checklist.md`
- `doc/grey_release_observation_template.md`
- `doc/result_quality_review_template.md`
- `doc/post_launch_issue_triage.md`

---

## 8. 当前项目状态建议

基于现有文档体系，项目当前最适合进入：

### 工程执行阶段

优先动作：

1. 按 `doc/sprint_01_backlog.md` 启动开发
2. 前端基于 `frontend/mock/` 与线框先搭主链路
3. 后端按 `openapi/openapi.yaml` 与 schema 文档落骨架
4. 按 `doc/monorepo_structure_and_bootstrap.md` 初始化仓库与本地环境
5. 按 `doc/development_and_deploy_workflow.md` 采用 Git + 镜像化部署流程

### 后续推进节奏

- Sprint 01：骨架
- Sprint 02：真实分析闭环
- Sprint 03：质量与上线前收束
- 灰度：观察与问题治理

---

## 9. 推荐下一步维护方式

为避免文档失控，建议后续采用以下维护策略：

## 9.1 冻结类文档

以下文档原则上低频修改：

- `doc/prd_reddit_needs_discovery.md`
- `doc/technical_architecture_input.md`
- `doc/ui_style_guide.md`

## 9.2 迭代类文档

以下文档会随实现持续更新：

- `doc/api_contract_draft.md`
- `openapi/openapi.yaml`
- `doc/sprint_01_backlog.md`
- `doc/sprint_02_backlog.md`
- `doc/sprint_03_backlog.md`
- `frontend/mock/`

## 9.3 运营类文档

以下文档在灰度和上线期高频使用：

- `doc/release_readiness_checklist.md`
- `doc/grey_release_observation_template.md`
- `doc/result_quality_review_template.md`
- `doc/post_launch_issue_triage.md`

---

## 10. 一句话结论

这份总索引的作用，不是把文档“列一遍”，而是：

> **让不同角色在不同阶段，都能快速找到自己当前最该使用的那组文档。**
