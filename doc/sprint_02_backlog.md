# Demand Atlas｜需见 Sprint 02 Backlog

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 Sprint 02 Backlog
- 文档版本：V1.0
- 更新时间：2026-05-12
- Sprint 目标阶段：M2 分析闭环可跑
- 上游输入：
  - `doc/sprint_01_backlog.md`
  - `doc/mvp_delivery_plan.md`
  - `doc/implementation_work_breakdown.md`
  - `doc/query_task_and_pipeline_design.md`
  - `doc/scoring_engine_design.md`
  - `frontend/mock/`

---

## 2. Sprint 02 目标

Sprint 02 的目标是：

> **让 Demand Atlas｜需见 从“页面和任务骨架可跑”，进入“真实分析结果可跑”。**

### Sprint 02 成功定义

本轮结束时，团队应具备以下能力：

1. QueryTask 可真实触发 fetch / normalize / retrieve / cluster / score / snapshot
2. 至少 1–2 个主题模板能产出真实结果
3. 热门榜可真实生成
4. 高增长榜可基础生成
5. 详情页可读取真实 supporting evidence
6. ResultSnapshot 不再只是静态占位，而是真实分析产物

---

## 3. Sprint 02 范围

## 3.1 本轮包含

### 后端 / 数据

- Reddit 数据接入最小闭环
- Normalize 最小闭环
- Retrieve 最小闭环
- Cluster 最小闭环
- Score 最小闭环
- Snapshot 落盘最小闭环

### 前端

- 查询任务页接入真实状态
- 结果页接入真实 snapshot
- 榜单列表接入真实 board
- 详情页接入真实 cluster detail

### 设计 / 产品

- 结果质量快速 review
- 榜单可解释性 review

## 3.2 本轮不包含

- 高机会榜精细优化
- 收藏 / 需求库
- 订阅提醒
- 飞书 / Notion 导出
- 多模板运营后台

---

## 4. Sprint 02 进入条件

以下条件满足后，Sprint 02 可启动：

- [ ] Sprint 01 骨架目标已完成
- [ ] QueryTask 主流程可创建与轮询
- [ ] TopicTemplate 种子已可读取
- [ ] 前端页面骨架已接上 mock
- [ ] 核心表结构已具备继续扩展条件

---

## 5. Sprint 02 交付物

## 5.1 必交付物

1. Reddit Connector 最小可用版本
2. SourcePost / SourceComment 标准化链路
3. Retrieve 最小逻辑
4. Cluster 最小逻辑
5. Discussion / Attention / Growth score 首版实现
6. ResultSnapshot 真实写入
7. 热门榜真实返回
8. 高增长榜真实返回
9. 详情页真实 evidence 返回

## 5.2 建议交付物

1. 机会分首版弱实现
2. 结果质量 review 记录
3. 若干失败与 partial_success 的真实可测样例

---

## 6. 按角色拆分的 Sprint 02 工作项

## 6.1 后端工作项

### BE-07 QueryTask Pipeline 实执行接入

#### 目标

让 QueryTask 不再只停留在状态骨架，而是真正进入 pipeline。

#### 内容

- 串起：
  - validate
  - plan
  - fetch
  - normalize
  - retrieve
  - cluster
  - score
  - snapshot
- 补充 `query_task_run_logs`

#### 输出

- QueryTask 真正跑完整流程

#### Done 标准

- 有真实任务从 pending 进入 success / partial_success / failed

---

### BE-08 ResultSnapshot 真实生成与读取

#### 目标

让 snapshot 成为真实分析结果容器。

#### 内容

- 写入 `result_snapshots`
- 写入 `result_snapshot_clusters`
- 结果摘要真实填充

#### 输出

- 可供结果页读取的真实 snapshot

#### Done 标准

- 热门榜和增长榜可通过真实 `result_snapshot_id` 获取

---

### BE-09 Cluster Detail 真实返回

#### 目标

让详情页接入真实 cluster detail 数据。

#### 内容

- `GET /result-snapshots/{id}/clusters/{clusterId}`
- scenes / pain_points / alternatives
- supporting evidence
- opposing evidence（可弱化）

#### 输出

- 详情接口真实数据

#### Done 标准

- 至少一个 cluster detail 可完整渲染

---

## 6.2 数据 / 分析工作项

### DS-04 Reddit Connector 最小实现

#### 目标

提供可用于 Sprint 02 的真实数据源接入。

#### 内容

- 按模板候选社区拉取帖子
- 按关键词补拉帖子
- 获取帖子评论

#### 输出

- 最小可用 fetch 能力

#### Done 标准

- 至少一个模板能拉到真实帖子和评论

---

### DS-05 Normalize 链路实现

#### 目标

把原始内容落成标准化对象。

#### 内容

- SourcePost 映射
- SourceComment 映射
- 时间统一
- 可访问性状态处理
- 基础语言识别

#### 输出

- 标准化 post/comment 数据

#### Done 标准

- fetch 结果可被 retrieve 阶段使用

---

### DS-06 Retrieve 最小逻辑

#### 目标

在标准化数据中召回有效候选内容。

#### 内容

- 模板关键词召回
- 定向关键词召回
- 基础语言过滤
- 简单噪声过滤

#### 输出

- 候选帖子 / 评论集合

#### Done 标准

- 至少一个模板查询能得到有效候选集合

---

### DS-07 Cluster 最小逻辑

#### 目标

将候选内容聚为可展示需求。

#### 内容

- 问题表达抽取
- 场景抽取
- 痛点抽取
- 同义表达合并
- 规范标题生成

#### 输出

- DemandCluster 首版
- Evidence 首版

#### Done 标准

- 至少产生 3–10 个可展示 cluster

---

### DS-08 Scoring 引擎首版实现

#### 目标

产出热门榜和增长榜的基础排序。

#### 内容

- discussion_score
- attention_score
- hot_score
- growth_score
- emerging signal
- 最低门槛与 weak signal

#### 输出

- ClusterMetricSnapshot
- hot / growth 排序结果

#### Done 标准

- 榜单排序结果基本可解释

---

### DS-09 结果质量快速校准

#### 目标

避免首版分析结果明显失真。

#### 内容

- 热门榜 Top 10 抽样 review
- 增长榜小样本污染检查
- 证据与摘要一致性检查

#### 输出

- 快速 review 记录
- 需要调整的参数清单

#### Done 标准

- 没有明显不可用结果直接进入主榜

---

## 6.3 前端工作项

### FE-06 QueryTask 页接真实接口

#### 目标

把任务页从 mock 驱动切到真实 QueryTask API。

#### 内容

- 轮询真实状态
- 处理 running / success / partial_success / failed
- 匿名 token 恢复

#### 输出

- 真实任务页

#### Done 标准

- 可以观察真实 QueryTask 生命周期

---

### FE-07 结果页接真实 snapshot

#### 目标

让结果页读取真实结果。

#### 内容

- summary header 接口接入
- board tabs 接口接入
- coverage / freshness 接口接入
- empty / weak signal / low confidence 状态接入

#### 输出

- 真实结果页

#### Done 标准

- 热门榜与增长榜可真实切换并展示

---

### FE-08 详情页接真实 cluster detail

#### 目标

让详情页从 mock 变成真实数据驱动。

#### 内容

- cluster detail 接口接入
- evidence 渲染
- availability 状态渲染
- supporting / opposing 分栏

#### 输出

- 真实详情页

#### Done 标准

- 点击榜单项可进入真实详情页

---

### FE-09 主链路错误态联调

#### 目标

确保首版主链路状态都可感知。

#### 内容

- no result
- partial_success
- failed
- access denied

#### 输出

- 前端状态流补齐

#### Done 标准

- 关键错误态都可正确渲染

---

## 6.4 设计 / 产品工作项

### DE-03 结果页与详情页细化

#### 目标

根据真实数据形态微调页面布局。

#### 内容

- 结果页榜单项结构微调
- 详情页 evidence 区密度微调
- 标签与 banner 优先级微调

#### 输出

- 结果页 / 详情页细化稿

#### Done 标准

- 不阻塞前端实现

---

### PO-01 结果质量评审

#### 目标

从产品视角确认真实结果是否可接受。

#### 内容

- 热门榜 review
- 增长榜 review
- 详情页 evidence review

#### 输出

- 结果质量问题清单

#### Done 标准

- 明确 Sprint 03 前必须修的问题

---

## 6.5 QA / 联调工作项

### QA-03 QueryTask 真链路联调

#### 目标

验证任务从创建到结果返回的主流程。

#### 内容

- one_click 主链路
- directed 主链路
- success / partial_success / failed

#### 输出

- 联调问题清单

#### Done 标准

- 主链路无阻断

---

### QA-04 结果与详情联调

#### 目标

验证 snapshot、board、detail 一致性。

#### 内容

- result summary 与 board 一致性
- board item 与 detail 一致性
- evidence 字段完整性

#### 输出

- 一致性检查清单

#### Done 标准

- 无明显字段错位与上下文错乱

---

## 7. Sprint 02 依赖关系

```text
DS-04 Reddit Connector
  -> DS-05 Normalize
  -> DS-06 Retrieve
  -> DS-07 Cluster
  -> DS-08 Scoring
  -> BE-08 ResultSnapshot

BE-07 QueryTask Pipeline
  -> BE-08 ResultSnapshot
  -> FE-06 QueryTask 页

BE-08 ResultSnapshot
  -> FE-07 结果页

BE-09 Cluster Detail
  -> FE-08 详情页

DS-09 质量校准
  -> PO-01 评审
```

---

## 8. 可并行执行建议

## 8.1 数据与前端可并行

前端可在 Sprint 初期仍暂时使用 mock，待真实接口可用后替换。

## 8.2 QueryTask 与分析逻辑可并行

- 后端先把 pipeline stage 串起来
- 数据侧逐步替换 stage 内真实逻辑

## 8.3 设计与质量 review 可并行

- 结果页、详情页的真实数据 review 可边做边调

---

## 9. Sprint 02 风险点

## 9.1 风险 A：真实数据质量过低

表现：

- 抓到的数据太少
- 聚类无意义

控制建议：

- 首批先只支持高质量模板
- 缩小候选社区池

## 9.2 风险 B：聚类结果不稳定

表现：

- cluster 标题奇怪
- evidence 与摘要不一致

控制建议：

- 先追求“可解释”而不是“覆盖更广”

## 9.3 风险 C：增长榜被极小样本污染

表现：

- 1–2 个帖子冲到榜首

控制建议：

- 样本门槛严格执行
- emerging signal 与正式榜分区

## 9.4 风险 D：真实接口返回不稳定导致前端反复改

控制建议：

- 严格以 OpenAPI 和 examples 为准
- 不轻易改字段语义

---

## 10. Sprint 02 验收标准

## 10.1 最小演示流

Sprint 02 至少应能演示：

1. 选择真实 TopicTemplate
2. 创建真实 QueryTask
3. QueryTask 进入 running
4. 成功生成真实 ResultSnapshot
5. 查看真实热门榜
6. 切换查看高增长榜
7. 点击进入真实详情页
8. 查看真实 supporting evidence

## 10.2 后端验收

- [ ] QueryTask 可跑完整 pipeline
- [ ] ResultSnapshot 真实落盘
- [ ] Board API 返回真实结果
- [ ] Cluster detail API 返回真实结果

## 10.3 数据 / 分析验收

- [ ] 至少 1–2 个模板可跑出真实结果
- [ ] 热门榜 Top 10 基本合理
- [ ] 增长榜无明显小样本失控

## 10.4 前端验收

- [ ] 主链路已从 mock 迁移到真实接口
- [ ] partial_success / no result / failed 均可渲染
- [ ] 详情页 evidence 可正常展示

---

## 11. Sprint 02 结束后应具备的输入

Sprint 02 完成后，Sprint 03 应直接基于以下内容继续：

1. 真实分析闭环已打通
2. 热门榜 / 增长榜已有基础质量
3. 页面可消费真实结果
4. 结果质量问题已形成清单

Sprint 03 可重点进入：

- 结果质量提升
- 导出真链路完善
- 上线前状态补齐
- 机会榜优化

---

## 12. 推荐下一步产出

基于本文档，建议继续输出：

1. `doc/sprint_03_backlog.md`
2. `doc/result_quality_review_template.md`

---

## 13. 一句话结论

Sprint 02 的核心，不是把所有细节做完，而是：

> **让 Demand Atlas｜需见 首次跑出真实、可读、可解释的需求结果。**

