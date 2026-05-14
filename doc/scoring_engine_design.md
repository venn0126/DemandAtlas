# Demand Atlas｜需见 评分引擎设计文档

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 评分引擎设计文档
- 文档版本：V1.0
- 更新时间：2026-05-12
- 适用阶段：排序系统设计 / 算法实现设计 / 后端实现评审 / 产品解释口径对齐
- 上游输入：
  - `doc/prd_reddit_needs_discovery.md`
  - `doc/technical_architecture_input.md`
  - `doc/domain_model_and_schema.md`
  - `doc/query_task_and_pipeline_design.md`

---

## 2. 文档目标

本文档用于定义 V1 阶段评分引擎的设计原则、输入指标、计算逻辑、边界规则和排序口径。

本文档重点回答：

1. 什么是讨论度分、关注度分、增长分、机会分
2. 这些分数分别用哪些指标计算
3. 如何避免大社区天然碾压小社区
4. 如何处理样本过少、分母为 0、低置信度等边界 case
5. 三个榜单的最终排序逻辑是什么

### 2.1 本文档不直接覆盖

- 最终模型代码实现
- 最终特征仓库设计
- 最终 A/B 实验方案
- LLM prompt 细节

---

## 3. 评分引擎定位

## 3.1 评分引擎的职责

评分引擎负责：

- 把离散统计指标转成统一分数
- 给榜单排序提供稳定依据
- 为产品层提供可解释的“为什么排前面”

## 3.2 评分引擎不负责

评分引擎不负责：

- 从原始文本中发现需求
- 生成完整需求摘要
- 判断商业可行性是否为真

这些由：

- 聚类系统
- 证据抽取系统
- AI 摘要系统

共同完成。

## 3.3 评分系统在产品中的角色

V1 建议将评分系统理解为：

- **排序系统**
- **解释系统**
- **风控系统**

而不是“绝对真相系统”。

---

## 4. 设计原则

## 4.1 相对排序优先

V1 所有分数优先作为“同一次查询结果集内部”的相对比较依据。

不建议在 V1 把不同查询任务之间的分数直接横向比较。

## 4.2 可解释优先

每一个榜单条目，都应能解释：

- 为什么它分高
- 它高在哪个维度
- 是否存在样本不足 / 低置信度

## 4.3 统计分与推断分分离

建议区分：

- **统计分**：讨论度、关注度、增长分
- **推断分**：机会分

其中：

- 统计分更稳定
- 机会分更主观

因此 V1 中：

- 热门榜与增长榜应优先依赖统计分
- 机会榜只作为辅助榜单

## 4.4 样本量优先于华丽分数

若样本过少，即使某项指标很高，也不应直接推到榜首。

## 4.5 大社区平滑

需要避免以下问题：

> 仅因为某个需求出现在超大社区，就天然获得压倒性优势。

因此必须对：

- 帖子量
- 评论量
- 互动量

做一定程度的平滑或截断。

## 4.6 配置化

V1 的公式、阈值、权重应可配置，不应硬编码到不可调整。

---

## 5. 评分引擎整体框架

V1 建议采用四层结构：

1. 原始统计层
2. 特征处理层
3. 单项分数层
4. 榜单排序层

### 5.1 逻辑图

```text
Raw Metrics
  -> Normalize / Smooth / Clamp
  -> Feature Scores
  -> Discussion / Attention / Growth / Opportunity
  -> Board Ranking
```

---

## 6. 原始输入指标定义

以下指标来自 `ClusterMetricSnapshot`。

## 6.1 规模类指标

- `post_count`
- `comment_count`
- `unique_user_count`
- `community_spread_count`

## 6.2 互动质量类指标

- `avg_comment_depth`
- `avg_post_score`
- `avg_comment_score`
- `high_engagement_post_ratio`

## 6.3 趋势类指标

- `prev_post_count`
- `prev_comment_count`
- `prev_unique_user_count`
- `prev_community_spread_count`

## 6.4 风险与可靠性指标

- `confidence_score`
- `is_weak_signal`
- `is_low_confidence`
- `is_emerging_signal`

## 6.5 可选 AI 特征

主要用于机会分：

- `pain_point_clarity_score`
- `scene_concentration_score`
- `solution_intent_score`
- `alternative_dissatisfaction_score`

---

## 7. 特征预处理设计

在进入评分前，所有原始指标建议经过统一预处理。

## 7.1 缺失值处理

建议规则：

- 缺失的统计字段先按 0 处理
- 缺失的 AI 推断字段按 `null` 处理，不强行补零

### 原因

- 统计字段缺失通常意味着未观察到
- AI 字段缺失通常意味着“未生成”，不应直接当作负面

## 7.2 极值截断

建议对以下指标做上界截断或对数处理：

- `post_count`
- `comment_count`
- `avg_post_score`
- `avg_comment_score`

### 目的

避免某一两个异常高热帖子导致整个 cluster 极端放大。

## 7.3 对数平滑

对规模类指标，建议使用：

`log(1 + x)`

### 适用字段

- 帖子数
- 评论数
- 独立用户数
- 社区扩散数

## 7.4 比例类指标约束

比例类指标建议限制在 `[0, 1]` 后再映射到 0–100。

例如：

- `high_engagement_post_ratio`

## 7.5 标准化

V1 建议采用“单次查询结果集内部标准化”：

- Min-Max
- 或分位数归一化
- 或 Robust Scaling

### 推荐

V1 采用：

- 对数平滑后再 Min-Max

若极值问题明显，再切换为 Robust Scaling。

---

## 8. 大社区平滑设计

## 8.1 问题定义

如果某个需求仅出现在超大社区，即使真实“讨论质量”一般，也可能因为量大而压制其他更垂直、更真实的需求。

## 8.2 处理原则

不直接按社区成员数做强归一，而是采用：

- 对数平滑
- 高互动比率
- 社区扩散数
- 独立用户数

联合平衡。

## 8.3 建议方案

### A. 规模类指标统一对数平滑

例如：

`scaled_post_count = log(1 + post_count)`

### B. 社区扩散作为奖励项

若某需求跨多个社区都有出现，则说明其不仅仅依赖单社区规模。

### C. 高互动帖占比作为质量补偿

避免只依靠大量普通帖堆高分数。

## 8.4 不建议的方案

V1 不建议直接除以 subreddit member_count。

原因：

- 社区成员数不稳定
- 实际活跃基数不可准确代表
- 解释成本高

---

## 9. 讨论度分设计

## 9.1 目标

衡量：

> 这个需求在当前时间窗口内，被多少人、以多深的方式讨论。

## 9.2 输入特征

- `post_count`
- `comment_count`
- `unique_user_count`
- `avg_comment_depth`

## 9.3 推荐处理逻辑

### Step 1：预处理

- 对 `post_count` / `comment_count` / `unique_user_count` 做 `log(1+x)`
- `avg_comment_depth` 直接截断后标准化

### Step 2：标准化

得到：

- `post_count_norm`
- `comment_count_norm`
- `unique_user_count_norm`
- `comment_depth_norm`

### Step 3：加权求和

建议公式：

```text
discussion_score =
  0.30 * post_count_norm +
  0.30 * comment_count_norm +
  0.20 * unique_user_count_norm +
  0.20 * comment_depth_norm
```

### Step 4：映射到 0–100

最终输出 0–100 分。

## 9.4 解释口径

讨论度分高，代表：

- 讨论多
- 参与人多
- 讨论链条更深

不代表：

- 用户一定想付费
- 产品机会一定更大

---

## 10. 关注度分设计

## 10.1 目标

衡量：

> 这个需求相关讨论是否被看见、被响应、被认可。

## 10.2 输入特征

- `avg_post_score`
- `avg_comment_score`
- `high_engagement_post_ratio`

## 10.3 推荐处理逻辑

### Step 1：预处理

- 对 `avg_post_score` / `avg_comment_score` 做截断与平滑
- `high_engagement_post_ratio` 保持比例结构

### Step 2：标准化

得到：

- `avg_post_score_norm`
- `avg_comment_score_norm`
- `high_engagement_ratio_norm`

### Step 3：加权求和

建议公式：

```text
attention_score =
  0.50 * avg_post_score_norm +
  0.30 * avg_comment_score_norm +
  0.20 * high_engagement_ratio_norm
```

## 10.4 解释口径

关注度分高，代表：

- 相关讨论更容易获得响应
- 更可能出现在高热帖子中

不代表：

- 讨论深度一定高
- 需求表达一定明确

---

## 11. 增长分设计

## 11.1 目标

衡量：

> 这个需求相对于上一等长窗口，是否明显升温。

## 11.2 输入特征

- 当前窗口：
  - `post_count`
  - `comment_count`
  - `unique_user_count`
  - `community_spread_count`
- 对比窗口：
  - `prev_post_count`
  - `prev_comment_count`
  - `prev_unique_user_count`
  - `prev_community_spread_count`

## 11.3 增长计算原则

V1 不建议简单用：

`(current - prev) / prev`

直接做最终增长分。

因为：

- `prev = 0` 时失真
- 小样本极易虚高

## 11.4 推荐中间特征

建议至少计算：

### A. 提及增长率

```text
mention_growth_ratio =
  (current_mentions - prev_mentions) / max(prev_mentions, floor_base)
```

其中：

- `current_mentions = post_count + comment_count`
- `prev_mentions = prev_post_count + prev_comment_count`
- `floor_base` 建议为 5 或 10

### B. 用户增长率

```text
user_growth_ratio =
  (unique_user_count - prev_unique_user_count) / max(prev_unique_user_count, floor_base_user)
```

### C. 社区扩散增长率

```text
community_growth_ratio =
  (community_spread_count - prev_community_spread_count) / max(prev_community_spread_count, 1)
```

## 11.5 推荐公式

先对增长率做截断，例如：

- 下限：-1
- 上限：3 或 5

然后归一化后加权：

```text
growth_score =
  0.60 * mention_growth_norm +
  0.20 * user_growth_norm +
  0.20 * community_growth_norm
```

## 11.6 新兴信号规则

当上一周期样本极低或为 0 时：

- 不直接给超高增长分
- 标记为 `is_emerging_signal = true`

建议规则：

### 条件

- `prev_mentions = 0`
- 且当前样本达到最低门槛

### 行为

- 增长分进入受限上限
- 展示“新兴信号”标签

## 11.7 解释口径

增长分高，代表：

- 当前比上一周期明显升温

不代表：

- 绝对讨论量一定大

因此增长榜必须同时展示样本量。

---

## 12. 机会分设计

## 12.1 目标

衡量：

> 这个需求是否更像一个值得切入的产品 / 内容机会。

## 12.2 特征性质

机会分比前三项更主观，建议明确为：

- 规则 + AI 的联合推断分
- 不作为唯一主排序依据

## 12.3 输入特征

建议至少包括：

- `pain_point_clarity_score`
- `scene_concentration_score`
- `solution_intent_score`
- `alternative_dissatisfaction_score`

### 可附加输入

- `discussion_score`
- `attention_score`
- `confidence_score`

## 12.4 子分定义建议

### A. 痛点明确度

衡量：

- 用户是否明确表达问题
- 是否是“真实抱怨”而非泛讨论

### B. 场景集中度

衡量：

- 需求是否集中在清晰场景中
- 是否存在可识别用户使用场景

### C. 解决意愿强度

衡量：

- 用户是否在寻找替代方案
- 是否有购买 / 尝试 / 切换的倾向

### D. 替代方案不满意度

衡量：

- 当前主流替代方案是否被抱怨
- 是否出现反复的“不满意”

## 12.5 推荐公式

```text
opportunity_score =
  0.30 * pain_point_clarity_norm +
  0.20 * scene_concentration_norm +
  0.25 * solution_intent_norm +
  0.25 * alternative_dissatisfaction_norm
```

## 12.6 机会分降级规则

当以下任一条件满足时，应降级机会分：

1. `confidence_score` 低于阈值
2. 样本不足
3. 证据高度冲突

### 降级方式建议

- 不展示机会分
- 或展示但标记“辅助判断”
- 或仅在详情页展示，不在主榜单强调

## 12.7 解释口径

机会分高，代表：

- 痛点更明确
- 场景更集中
- 用户更像在寻求解决方案

不代表：

- 一定能做成商业产品
- 市场规模一定足够大

---

## 13. 置信度与风控规则

## 13.1 confidence_score 的角色

`confidence_score` 不是榜单主分数，但应作为：

- 风险校正项
- 降级判断项
- tie-break 项

## 13.2 低置信度阈值

V1 建议配置：

- `confidence_score < 40`：低置信度
- `40 <= confidence_score < 60`：中等置信度
- `>= 60`：相对可用

### 说明

阈值应配置化，不写死在产品层。

## 13.3 低置信度影响规则

### 对热门榜

- 可展示
- 但需打标签

### 对增长榜

- 可展示
- 但增长解释应谨慎

### 对机会榜

- 默认降级或隐藏

---

## 14. 样本门槛与弱信号规则

## 14.1 正式榜单最低门槛

V1 默认至少满足以下一项：

- `post_count >= 2`
- `comment_count >= 10`
- `unique_user_count >= 5`

## 14.2 弱信号规则

若不满足正式门槛，但有一定可观察性，可标记：

- `is_weak_signal = true`

建议条件：

- 至少有 1 个帖子
- 且至少 3 条相关评论
- 且 `confidence_score` 不为极低

## 14.3 弱信号展示策略

- 不进入正式榜单 Top 区域
- 可进入“弱信号 / 新兴信号”区域

---

## 15. 三类榜单最终排序逻辑

## 15.1 热门需求榜

### 目标

优先展示当前最值得优先关注的“高讨论 + 高响应”需求。

### 推荐公式

```text
hot_score =
  0.55 * discussion_score +
  0.45 * attention_score
```

### 过滤条件

- 满足正式榜单最低门槛

### 排序 tie-break

1. `confidence_score`
2. 样本量
3. 最近活跃时间
4. `cluster_id`

## 15.2 高增长需求榜

### 目标

优先展示正在升温的需求。

### 推荐公式

```text
growth_rank_score = growth_score
```

### 显示要求

必须同时显示：

- 样本量
- 是否新兴信号
- `confidence_score`

### 过滤条件

- 满足正式门槛，或被判定为新兴信号

## 15.3 高机会需求榜

### 目标

优先展示更像“产品 / 内容切入点”的需求。

### 推荐公式

```text
opportunity_rank_score = opportunity_score
```

### 附加约束

- 样本不足时降级
- 低置信度时降级
- 不建议作为默认首页首榜

---

## 16. 排序后处理规则

## 16.1 去重复

排序结果需要避免语义高度重复的多个 cluster 同时排在前列。

建议后处理：

- 前 N 名中相似 cluster 做近邻去重或轻微降排

## 16.2 类别平衡（V1 可选）

若模板中同时覆盖多个子方向，可考虑轻量平衡，避免榜首全被单一细分占满。

V1 可先不做强平衡，但要在评估中观察。

## 16.3 榜单数量限制

V1 默认：

- 每个榜单首屏展示 Top 20

### 建议

- 排序引擎实际可以产出更长列表
- 前端按分页消费

---

## 17. 配置化设计建议

## 17.1 可配置项

以下参数建议进入配置中心：

- 分数权重
- 最低证据门槛
- 低置信度阈值
- 新兴信号阈值
- 截断上限
- 对数平滑开关
- 机会分降级阈值

## 17.2 版本化

建议每次评分引擎参数集有独立版本：

- `scoring_config_version`

该版本应记录在：

- `query_tasks.pipeline_version`
- `result_snapshots`

### 原因

- 便于回放
- 便于实验
- 便于结果解释

---

## 18. 评估与校准建议

## 18.1 离线评估

建议建立一批标注样本，评估：

- 热门榜 Top N 合理性
- 增长榜 Top N 合理性
- 机会榜 Top N 可解释性

## 18.2 人工评审维度

可让产品 / 研究 / 运营共同评审：

1. 是否真是需求而不是噪声
2. 是否值得被排前
3. 是否存在误聚类
4. 是否存在“大社区碾压”问题

## 18.3 线上指标建议

评分系统可间接观察：

- 榜单详情点击率
- 导出率
- 用户停留时长
- 高频查询重复率

### 注意

这些指标只能辅助，不应直接代替排序质量判断。

---

## 19. 边界 Case 处理清单

## 19.1 上一周期为 0

处理：

- 不直接计算无限增长
- 标记新兴信号
- 增长分受上限约束

## 19.2 1 篇帖子极高热度

处理：

- 可高 attention
- 但 discussion 不应过高
- 若样本不足则进入样本不足或弱信号标签

## 19.3 大量普通帖子，无高互动

处理：

- discussion 可高
- attention 不应高

## 19.4 评论极多但都来自少数用户

处理：

- unique_user_count 拉低 discussion_score

## 19.5 多社区小范围重复提及

处理：

- community_spread_count 作为正向加分

## 19.6 低置信度但增长很快

处理：

- 可进入增长榜
- 必须带低置信度标签
- 不应直接进入机会榜高位

---

## 20. 推荐实现顺序

V1 建议按以下顺序实现：

### 第一阶段

- discussion_score
- attention_score
- hot_score

### 第二阶段

- growth_score
- emerging signal

### 第三阶段

- opportunity_score
- confidence 降级规则

### 原因

这样可以先保证：

- 热门榜可信
- 增长榜可用

再逐步增强机会判断。

---

## 21. 一句话结论

本评分引擎的核心目标，不是计算一个“绝对真值”，而是：

> **在同一查询上下文中，用可解释、可平滑、可降级的方式，把最值得优先关注的需求排到前面。**
