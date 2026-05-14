# Demand Atlas｜需见 前端组件拆解文档

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 前端组件拆解文档
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：前端页面拆解 / 组件设计 / 开发分工 / UI 实现评审
- 上游输入：
  - `doc/information_architecture_and_state_flow.md`
  - `doc/frontend_state_management_notes.md`
  - `doc/api_contract_draft.md`
  - `doc/openapi_example_responses.md`

---

## 2. 文档目标

本文档用于把页面级信息架构继续拆解到“前端可开发”的组件层。

本文档重点回答：

1. 每个页面由哪些组件构成
2. 哪些组件是容器组件，哪些是展示组件
3. 每个组件依赖什么数据
4. 每个组件触发什么交互事件
5. 哪些组件需要复用
6. V1 与 V1.5 在组件层的边界如何控制

### 2.1 本文档不直接覆盖

- 最终 UI 样式细节
- CSS / Tailwind / CSS-in-JS 方案
- 最终文件目录命名
- 最终 design token 规范

---

## 3. 组件设计原则

## 3.1 页面容器与业务组件分离

建议将组件分成三层：

1. **Page Container**
2. **Business Component**
3. **Pure Presentational Component**

### 含义

- Page Container：负责路由、数据请求、状态协调
- Business Component：负责某块业务区域的展示与交互
- Pure Presentational Component：只接收 props 渲染，不发请求

## 3.2 服务端数据读取集中在容器层

不建议让深层展示组件直接发核心业务请求。

推荐做法：

- 页面容器负责拿数据
- 向下传递结构化 props

例外：

- 可局部容忍独立 pagination 组件做受控拉取，但仍应通过统一 hooks

## 3.3 QueryTask / ResultSnapshot 上下文显式透传

与任务或结果强绑定的组件，应显式接收：

- `queryTaskId`
- `resultSnapshotId`
- `clusterId`

不要依赖隐式全局状态猜测上下文。

## 3.4 展示状态不自行推断业务真值

如：

- `is_low_confidence`
- `is_weak_signal`
- `coverage_note`

这些应直接来自服务端数据，而不是组件自己推导。

## 3.5 可替换优先

高复用模块应设计成可替换组件，例如：

- 结果状态条
- 榜单列表
- 证据列表
- 分数标签区

---

## 4. 组件分层建议

## 4.1 顶层目录建议

建议按职责分：

```text
frontend/
  pages/
  containers/
  components/
    common/
    query/
    result/
    cluster/
    export/
  hooks/
  stores/
  services/
```

## 4.2 组件类别建议

### A. Layout 类

- `AppShell`
- `PageHeader`
- `PageSection`
- `ContentContainer`

### B. Query 类

- `TopicTemplateSelector`
- `TimeWindowPicker`
- `ViewTypeToggle`
- `KeywordInput`
- `SubredditSelector`
- `RegionHintInput`
- `MinEngagementEditor`
- `QuerySubmitBar`

### C. Task 类

- `QueryTaskStatusCard`
- `QueryTaskProgress`
- `QueryTaskStageTimeline`
- `QueryTaskErrorPanel`

### D. Result 类

- `ResultSummaryHeader`
- `BoardTabs`
- `CoverageNoticeBanner`
- `SyncFreshnessBanner`
- `BoardList`
- `BoardListItem`
- `BoardFilterBar`
- `EmptyResultState`
- `WeakSignalNotice`

### E. Cluster Detail 类

- `ClusterDetailHeader`
- `ClusterScorePanel`
- `ClusterMetricPanel`
- `ClusterTagList`
- `ClusterSceneList`
- `ClusterPainPointList`
- `ClusterAlternativeList`
- `EvidenceSection`
- `EvidenceList`
- `EvidenceCard`

### F. Export 类

- `ExportButton`
- `ExportJobStatusBadge`
- `ExportJobPanel`

### G. Common 类

- `LoadingState`
- `ErrorState`
- `EmptyState`
- `StatusBadge`
- `ConfidenceBadge`
- `SignalBadge`
- `PaginationFooter`
- `ToastHost`

---

## 5. 页面级组件树

## 5.1 首页

### 组件树

```text
HomePageContainer
  ├── AppShell
  ├── HomeHeroSection
  ├── DiscoverModeEntrySection
  ├── TopicTemplateRecommendationSection
  ├── ProductIntroSection
  └── ExampleResultPreviewSection
```

### 组件职责

#### HomePageContainer

- 拉取模板推荐数据
- 处理首页整体 loading / error

#### DiscoverModeEntrySection

- 提供“一键发现 / 定向发现”两个入口 CTA

#### TopicTemplateRecommendationSection

- 展示推荐模板卡片列表
- 点击进入一键发现页并带模板参数

---

## 5.2 一键发现页

### 组件树

```text
OneClickDiscoverPageContainer
  ├── AppShell
  ├── PageHeader
  ├── OneClickQueryForm
  │     ├── TopicTemplateSelector
  │     ├── TimeWindowPicker
  │     ├── ViewTypeToggle
  │     ├── QueryDescriptionHint
  │     └── QuerySubmitBar
  └── QueryFormHelpPanel
```

### 组件职责

#### OneClickDiscoverPageContainer

- 拉取可用模板列表
- 管理表单初始值
- 提交 `POST /query-tasks`
- 根据返回结果路由到任务页或结果页

#### OneClickQueryForm

- 受控表单容器
- 汇总子组件输入
- 输出 submit payload

#### TopicTemplateSelector

- 展示模板列表
- 支持选择、切换、查看基础说明

#### QuerySubmitBar

- 提交按钮
- 提交 loading
- 可能的 warning 展示

### 数据依赖

- `GET /topic-templates`
- `POST /query-tasks`

---

## 5.3 定向发现页

### 组件树

```text
DirectedDiscoverPageContainer
  ├── AppShell
  ├── PageHeader
  ├── DirectedQueryForm
  │     ├── KeywordInput
  │     ├── SubredditSelector
  │     ├── LanguageSelector
  │     ├── RegionHintInput
  │     ├── TimeWindowPicker
  │     ├── MinEngagementEditor
  │     ├── ViewTypeToggle
  │     ├── QueryValidationNotice
  │     └── QuerySubmitBar
  └── DirectedQueryExamplesPanel
```

### 组件职责

#### DirectedDiscoverPageContainer

- 管理 form 状态
- 进行提交前校验结果映射
- 提交查询任务

#### KeywordInput

- 支持多关键词 / 关键词组输入
- 支持删除、去重、长度限制

#### SubredditSelector

- 支持受控输入 subreddit 列表
- 首版可用 tag-input 形式

#### QueryValidationNotice

- 展示：
  - 过泛警告
  - 歧义警告
  - 超限错误

### 数据依赖

- `POST /query-tasks`

---

## 5.4 查询任务页

### 组件树

```text
QueryTaskPageContainer
  ├── AppShell
  ├── QueryTaskStatusCard
  │     ├── QueryTaskStatusBadge
  │     ├── QueryTaskProgress
  │     └── QueryTaskStageTimeline
  ├── QueryConditionSummaryCard
  ├── CoverageNoticeBanner
  ├── QueryTaskWarningList
  ├── QueryTaskActionBar
  └── QueryTaskErrorPanel
```

### 组件职责

#### QueryTaskPageContainer

- 读取 `queryTaskId`
- 轮询任务状态
- 状态到页面路由控制
- 在 `success` / `partial_success` 时跳转结果页或展示进入按钮

#### QueryTaskStatusCard

- 展示状态总览

#### QueryTaskProgress

- 展示阶段式进度

#### QueryTaskStageTimeline

- 展示当前 stage
- 可拓展显示阶段说明

#### QueryTaskActionBar

- 刷新
- 返回修改查询
- 查看结果（若可用）

### 数据依赖

- `GET /query-tasks/{queryTaskId}`

---

## 5.5 结果页

### 组件树

```text
ResultPageContainer
  ├── AppShell
  ├── ResultSummaryHeader
  ├── CoverageNoticeBanner
  ├── SyncFreshnessBanner
  ├── ResultControlBar
  │     ├── ViewTypeReadonlyIndicator
  │     ├── BoardTabs
  │     ├── ResultActionMenu
  │     └── ExportButton
  ├── ResultStateBlock
  ├── BoardList
  │     └── BoardListItem
  └── PaginationFooter
```

### 组件职责

#### ResultPageContainer

- 读取 `resultSnapshotId`
- 拉取 summary
- 拉取当前榜单列表
- 处理 board 切换
- 管理结果页级 loading / error

#### ResultSummaryHeader

- 展示：
  - 查询模式
  - 时间窗口
  - 生成时间
  - 当前视角

#### ResultControlBar

- 榜单切换
- 导出操作
- 未来扩展收藏 / 保存 / 订阅入口位

#### ResultStateBlock

统一承接以下状态：

- 无结果
- 样本不足
- 低置信度
- 部分成功

#### BoardList

- 渲染当前榜单条目列表
- 与分页联动

#### BoardListItem

- 展示轻详情
- 提供点击进入详情页

### 数据依赖

- `GET /result-snapshots/{id}`
- `GET /result-snapshots/{id}/boards/{boardType}`

---

## 5.6 需求详情页

### 组件树

```text
ClusterDetailPageContainer
  ├── AppShell
  ├── ClusterDetailHeader
  ├── CoverageNoticeBanner
  ├── ClusterInsightLayout
  │     ├── ClusterScorePanel
  │     ├── ClusterMetricPanel
  │     └── ClusterTagList
  ├── ClusterProblemSection
  │     ├── ClusterSceneList
  │     ├── ClusterPainPointList
  │     └── ClusterAlternativeList
  ├── ClusterEvidenceSection
  │     ├── SupportingEvidencePanel
  │     ├── OpposingEvidencePanel
  │     └── EvidenceCard
  ├── ClusterCommunitySection
  ├── ClusterActionBar
  │     └── ExportButton
  └── ClusterDetailErrorBlock
```

### 组件职责

#### ClusterDetailPageContainer

- 读取 `resultSnapshotId + clusterId`
- 拉取详情数据
- 管理详情页 loading / error

#### ClusterDetailHeader

- 标题、摘要、时间窗口、返回按钮

#### ClusterScorePanel

- 展示各类分数与解释标签

#### ClusterMetricPanel

- 展示：
  - post_count
  - comment_count
  - unique_user_count
  - community_spread_count

#### ClusterTagList

- 展示：
  - 低置信度
  - 弱信号
  - 新兴信号

#### ClusterEvidenceSection

- 支持 / 反对观点分栏
- 证据可访问性降级

### 数据依赖

- `GET /result-snapshots/{id}/clusters/{clusterId}`

---

## 5.7 设置 / 偏好页

### 组件树

```text
SettingsPageContainer
  ├── AppShell
  ├── AuthSection
  ├── PreferenceSection
  └── SessionInfoSection
```

### 组件职责

#### AuthSection

- 登录 / 登出入口

#### PreferenceSection

- 默认语言偏好
- 默认时间范围偏好（可选）

#### SessionInfoSection

- 当前匿名任务提示（可选）

---

## 6. 容器组件与展示组件划分

## 6.1 推荐划分标准

### 容器组件

具备以下一项即可视为容器组件：

- 发请求
- 读全局状态
- 处理路由参数
- 管理复杂交互流程

### 展示组件

满足以下特征：

- 不直接发核心请求
- 主要通过 props 渲染
- 只派发事件，不决定业务流程

## 6.2 建议容器组件列表

- `HomePageContainer`
- `OneClickDiscoverPageContainer`
- `DirectedDiscoverPageContainer`
- `QueryTaskPageContainer`
- `ResultPageContainer`
- `ClusterDetailPageContainer`
- `SettingsPageContainer`

## 6.3 建议纯展示组件列表

- `StatusBadge`
- `ConfidenceBadge`
- `SignalBadge`
- `LoadingState`
- `ErrorState`
- `EmptyState`
- `BoardListItem`
- `EvidenceCard`

---

## 7. 可复用组件清单

## 7.1 Banner 类

- `CoverageNoticeBanner`
- `SyncFreshnessBanner`
- `WarningBanner`

### 复用场景

- 结果页
- 详情页
- 查询任务页

## 7.2 Badge 类

- `StatusBadge`
- `ConfidenceBadge`
- `SignalBadge`
- `BoardTypeBadge`

### 复用场景

- 榜单列表
- 详情页
- 任务页

## 7.3 State 类

- `LoadingState`
- `ErrorState`
- `EmptyState`
- `NoResultState`
- `WeakSignalState`

### 复用场景

- 各页面与区块

## 7.4 Form 控件类

- `TimeWindowPicker`
- `ViewTypeToggle`
- `KeywordInput`
- `SubredditSelector`
- `QuerySubmitBar`

## 7.5 List / Card 类

- `BoardList`
- `BoardListItem`
- `EvidenceList`
- `EvidenceCard`

---

## 8. 每类组件的数据契约建议

## 8.1 Query 表单类组件

### 典型 props

- `value`
- `onChange`
- `disabled`
- `error`
- `warning`

### 典型 events

- `change`
- `submit`
- `reset`

## 8.2 Task 状态类组件

### 典型 props

- `status`
- `currentStage`
- `progress`
- `coverageNote`
- `warnings`

### 典型 events

- `refresh`
- `viewResult`
- `editQuery`

## 8.3 榜单类组件

### BoardList props

- `items`
- `boardType`
- `loading`
- `error`
- `nextPageToken`
- `onLoadMore`
- `onOpenCluster`

### BoardListItem props

- `rank`
- `title`
- `summary`
- `scores`
- `flags`
- `metrics`
- `topSubreddits`
- `highlightEvidence`

## 8.4 详情类组件

### ClusterScorePanel props

- `scores`
- `flags`

### EvidenceCard props

- `excerpt`
- `subreddit`
- `createdAt`
- `availabilityStatus`
- `sourceUrl`

---

## 9. 页面到接口的组件映射

| 页面组件 | 依赖接口 |
|---|---|
| `TopicTemplateSelector` | `GET /topic-templates` |
| `OneClickDiscoverPageContainer` | `POST /query-tasks` |
| `DirectedDiscoverPageContainer` | `POST /query-tasks` |
| `QueryTaskPageContainer` | `GET /query-tasks/{id}` |
| `ResultSummaryHeader` | `GET /result-snapshots/{id}` |
| `BoardList` | `GET /result-snapshots/{id}/boards/{boardType}` |
| `ClusterDetailPageContainer` | `GET /result-snapshots/{id}/clusters/{clusterId}` |
| `ExportButton` / `ExportJobPanel` | `POST /export-jobs`, `GET /export-jobs/{id}` |

---

## 10. 组件状态设计建议

## 10.1 所有异步组件统一具备的状态

建议统一支持：

- `idle`
- `loading`
- `ready`
- `empty`
- `error`

### 说明

不是所有业务都需要全部五种，但命名保持统一有利于实现。

## 10.2 榜单组件额外状态

除了通用异步状态，还应支持：

- `partial_success_notice`
- `weak_signal_notice`
- `low_confidence_notice`

### 注意

这些通常不是替代 `ready`，而是附加在 `ready` 上。

## 10.3 详情组件额外状态

- `evidence_partially_unavailable`
- `has_opposing_evidence`

---

## 11. 关键交互事件清单

## 11.1 查询发起类事件

- `onSubmitOneClickQuery`
- `onSubmitDirectedQuery`
- `onSwitchViewType`

## 11.2 任务类事件

- `onPollTaskStatus`
- `onRetryTask`
- `onGoToResult`
- `onBackToEdit`

## 11.3 结果页事件

- `onChangeBoardType`
- `onOpenClusterDetail`
- `onLoadMoreBoardItems`
- `onTriggerExport`
- `onRefreshResult`

## 11.4 详情页事件

- `onBackToResult`
- `onLoadMoreEvidence`
- `onTriggerExportCluster`

---

## 12. V1 / V1.5 组件边界

## 12.1 V1 必做组件

### 首页相关

- `HomeHeroSection`
- `DiscoverModeEntrySection`
- `TopicTemplateRecommendationSection`

### 查询相关

- `OneClickQueryForm`
- `DirectedQueryForm`
- `TimeWindowPicker`
- `ViewTypeToggle`
- `KeywordInput`
- `SubredditSelector`
- `QuerySubmitBar`

### 任务相关

- `QueryTaskStatusCard`
- `QueryTaskProgress`
- `QueryTaskErrorPanel`

### 结果相关

- `ResultSummaryHeader`
- `BoardTabs`
- `BoardList`
- `BoardListItem`
- `CoverageNoticeBanner`
- `SyncFreshnessBanner`

### 详情相关

- `ClusterDetailHeader`
- `ClusterScorePanel`
- `ClusterMetricPanel`
- `ClusterSceneList`
- `ClusterPainPointList`
- `ClusterAlternativeList`
- `EvidenceCard`

### 导出相关

- `ExportButton`
- `ExportJobPanel`

## 12.2 V1.5 预留组件

- `SavedQueryButton`
- `FavoriteClusterButton`
- `SubscriptionEntryButton`
- `DemandLibraryDrawer`
- `AlertRuleEditor`

### 要求

V1 不强行实现这些组件，但在布局层要预留位置。

---

## 13. 开发分工建议

## 13.1 按页面分工

适合小团队：

- 开发 A：查询页 + 任务页
- 开发 B：结果页 + 详情页
- 开发 C：通用组件 + 导出流 + 设置页

## 13.2 按模块分工

适合组件化开发：

- 模块 A：Query Form 组件组
- 模块 B：Task 状态组件组
- 模块 C：Result / Board 组件组
- 模块 D：Cluster Detail / Evidence 组件组
- 模块 E：Export / Common UI 组件组

## 13.3 联调优先顺序

建议按以下顺序联调：

1. 一键发现 -> QueryTask -> Result summary
2. Board list
3. Cluster detail
4. Export flow
5. 定向发现复杂输入校验

---

## 14. 推荐下一步产出

基于本文档，建议继续输出：

1. 前端线框图或原型稿
2. 正式组件目录结构说明
3. 设计 token / 组件规范文档

---

## 15. 一句话结论

前端组件拆解的关键，不是把页面切得更碎，而是：

> **围绕 QueryTask、ResultSnapshot 和 Cluster Detail，把数据获取、业务状态和纯展示组件清晰分层。**
