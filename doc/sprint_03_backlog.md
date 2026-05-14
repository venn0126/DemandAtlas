# Demand Atlas｜需见 Sprint 03 Backlog

## 1. 文档信息

- 文档名称：Demand Atlas｜需见 Sprint 03 Backlog
- 文档版本：V1.0
- 更新时间：2026-05-12
- Sprint 目标阶段：M3/M4 质量提升与上线前收束
- 上游输入：
  - `doc/sprint_02_backlog.md`
  - `doc/result_quality_review_template.md`
  - `doc/release_readiness_checklist.md`
  - `doc/mvp_delivery_plan.md`

---

## 2. Sprint 03 目标

Sprint 03 的目标是：

> **把 Demand Atlas｜需见 从“真实分析结果可跑”，推进到“结果更可信、状态更稳定、可进入灰度上线”的阶段。**

### Sprint 03 成功定义

本轮结束时，团队应具备以下能力：

1. 热门榜与增长榜质量达到基础可灰度标准
2. QueryTask 的边界状态更稳定
3. ResultSnapshot / board / detail 一致性稳定
4. 导出链路真实可用
5. 主要错误态和降级态都可被正确处理
6. 上线前 checklist 中 Must Have 项大部分完成

---

## 3. Sprint 03 范围

## 3.1 本轮包含

### 结果质量

- 热门榜校准
- 增长榜校准
- 机会榜弱化或校准
- 聚类与摘要质量提升

### 状态稳定性

- partial_success 完整处理
- no result 完整处理
- low confidence 展示收束
- evidence 可访问性降级处理完善

### 导出与交付

- Markdown 导出完善
- CSV 导出完善
- 导出状态链路稳定

### 联调与上线前收束

- API / 前端联调问题清空
- release readiness 检查推进
- 灰度前问题清单收束

## 3.2 本轮不包含

- 订阅系统
- 收藏 / 需求库正式上线
- 多平台
- 高级主题模板管理后台

---

## 4. Sprint 03 进入条件

以下条件满足后，Sprint 03 可启动：

- [ ] Sprint 02 已跑出真实 ResultSnapshot
- [ ] 热门榜与增长榜已有真实返回
- [ ] 详情页已可展示真实 evidence
- [ ] 已完成至少一轮结果质量评审
- [ ] 已形成首轮问题清单

---

## 5. Sprint 03 交付物

## 5.1 必交付物

1. 热门榜 / 高增长榜首轮校准版
2. 详情页摘要与 evidence 一致性修正版
3. partial_success / no result / low confidence 完整状态处理
4. Markdown / CSV 导出真实可用版
5. 联调问题修复清单
6. release readiness Must Have 项推进结果

## 5.2 建议交付物

1. 机会榜展示策略收束方案
2. 灰度期观察指标草案
3. 可灰度模板白名单

---

## 6. 按角色拆分的 Sprint 03 工作项

## 6.1 后端工作项

### BE-10 QueryTask 边界稳定性修复

#### 目标

让 QueryTask 状态流在真实环境中更稳定。

#### 内容

- 处理 running 卡住场景
- 处理 timeout -> partial_success / failed
- 处理 snapshot 写入失败
- 补齐 failure_reason code

#### 输出

- 更稳定的任务状态流

#### Done 标准

- QueryTask 不会长期无响应
- 关键失败有明确 failure code

---

### BE-11 ResultSnapshot / Board / Detail 一致性修复

#### 目标

减少榜单与详情之间的错位。

#### 内容

- board item 与 detail 字段对齐
- snapshot summary 与 board summary 对齐
- coverage_note 透传一致

#### 输出

- 更一致的结果读取链路

#### Done 标准

- QA 抽样下无明显上下文错乱

---

### BE-12 ExportJob 真链路完善

#### 目标

让导出从“可跑”进入“可用”。

#### 内容

- Markdown 导出字段核对
- CSV 导出字段核对
- 下载地址时效策略
- 导出失败处理

#### 输出

- 稳定导出能力

#### Done 标准

- Markdown / CSV 可稳定下载
- 导出失败能正确返回错误

---

## 6.2 数据 / 分析工作项

### DS-10 热门榜排序校准

#### 目标

让热门榜 Top 结果更符合“真实需求”预期。

#### 内容

- 根据评审记录调整 discussion / attention 权重
- 修正噪声过滤
- 优化高热非需求内容的降权

#### 输出

- 热门榜校准版

#### Done 标准

- 热门榜 Top 10 抽样质量明显提升

---

### DS-11 增长榜排序校准

#### 目标

降低增长榜的小样本幻觉。

#### 内容

- 调整 growth score 参数
- 调整 emerging signal 门槛
- 强化最低样本门槛

#### 输出

- 增长榜校准版

#### Done 标准

- 极小样本污染明显减少

---

### DS-12 聚类与摘要质量修复

#### 目标

提升 cluster 标题、摘要与 evidence 的一致性。

#### 内容

- 修复错误归并
- 缓解一个需求拆成多个 cluster
- 修复摘要过度概括问题

#### 输出

- 更稳定 cluster 结果

#### Done 标准

- 详情页与 evidence 的一致性显著提升

---

### DS-13 机会榜展示策略收束

#### 目标

决定机会榜在 V1 的上线形态。

#### 内容

- 根据质量评审决定：
  - 保持辅助榜
  - 弱化展示
  - 或仅在内部灰度可见

#### 输出

- 机会榜上线策略结论

#### Done 标准

- 产品、数据、前端对展示策略一致

---

## 6.3 前端工作项

### FE-10 结果页状态收束

#### 目标

把结果页各种边界态真正做完整。

#### 内容

- no result
- weak signal
- low confidence
- partial_success
- board empty

#### 输出

- 结果页完整状态版本

#### Done 标准

- 所有关键状态都有稳定 UI 表现

---

### FE-11 详情页状态收束

#### 目标

让详情页能够稳定承载真实数据质量波动。

#### 内容

- evidence unavailable 状态
- opposing evidence 稀缺或为空时的处理
- 低置信度提示
- coverage note 展示

#### 输出

- 详情页稳定版本

#### Done 标准

- 详情页不会因真实数据缺口崩坏

---

### FE-12 导出交互完善

#### 目标

让导出体验可真实交付。

#### 内容

- export button loading
- export job polling
- success / failed 反馈
- download entry

#### 输出

- 稳定导出前端体验

#### Done 标准

- 用户可从结果页或详情页完成导出

---

### FE-13 错误处理与恢复优化

#### 目标

减少用户在失败状态下的迷失。

#### 内容

- failed 页面引导文案
- retry / back to edit 路径优化
- 页面刷新恢复强化

#### 输出

- 更稳定的错误恢复体验

#### Done 标准

- 失败后用户知道下一步怎么做

---

## 6.4 产品 / 设计工作项

### PO-02 结果质量评审与问题归档

#### 目标

对 Sprint 02 真实结果做系统评审。

#### 内容

- 使用 `result_quality_review_template`
- 对重点模板做抽检
- 汇总问题优先级

#### 输出

- 质量问题清单
- 是否可灰度建议

#### Done 标准

- 至少完成一轮正式评审

---

### DE-04 边界状态视觉收束

#### 目标

让边界态表达统一、专业。

#### 内容

- no result
- weak signal
- low confidence
- partial_success
- export failed

#### 输出

- 边界状态视觉补充稿

#### Done 标准

- 状态表达与 UI 风格统一

---

## 6.5 QA / 联调工作项

### QA-05 主链路回归测试

#### 目标

验证核心主链路在修复后仍稳定。

#### 内容

- one_click
- directed
- QueryTask 生命周期
- result snapshot
- cluster detail
- export

#### 输出

- 回归结果记录

#### Done 标准

- 主链路无回归阻断

---

### QA-06 边界态回归测试

#### 目标

验证 Sprint 03 重点修复的边界态。

#### 内容

- no result
- partial_success
- failed
- low confidence
- evidence unavailable

#### 输出

- 边界态测试结果

#### Done 标准

- 关键边界态都可通过

---

### QA-07 发布前检查推进

#### 目标

对照 `release_readiness_checklist` 推进 Must Have 项。

#### 内容

- checklist 检查
- blocker 归档
- release 风险记录

#### 输出

- 发布 readiness 状态

#### Done 标准

- Must Have 项大部分完成或已有风险接受说明

---

## 7. Sprint 03 依赖关系

```text
PO-02 质量评审
  -> DS-10 热门榜校准
  -> DS-11 增长榜校准
  -> DS-12 聚类与摘要修复
  -> DS-13 机会榜策略收束

BE-10 QueryTask 稳定性修复
  -> FE-13 错误恢复优化

BE-11 Snapshot / Board / Detail 一致性修复
  -> FE-10 结果页状态收束
  -> FE-11 详情页状态收束

BE-12 Export 真链路
  -> FE-12 导出交互

QA-05 / QA-06
  -> QA-07 发布前检查推进
```

---

## 8. 可并行执行建议

## 8.1 排序校准与前端状态收束可并行

- 数据侧调榜单质量
- 前端补边界状态

可以并行推进。

## 8.2 导出链路可单独并行

- 后端导出
- 前端导出交互

可单独拆分处理，不阻塞榜单质量校准。

## 8.3 发布检查可后半程并行

- 在主链路趋稳后，QA 可提前推进 readiness checklist

---

## 9. Sprint 03 风险点

## 9.1 风险 A：结果质量问题超预期

表现：

- 热门榜核心结果仍不可信
- 聚类与 evidence 对不上

控制建议：

- 优先保住热门榜
- 机会榜可继续弱化

## 9.2 风险 B：导出链路不稳定

表现：

- 导出成功率低
- 下载地址失效

控制建议：

- 导出不阻断主查询链路
- 必要时上线初期先限制为 Markdown / CSV 基础导出

## 9.3 风险 C：边界态太多导致前端返工

控制建议：

- 严格按已定义状态做，不继续扩展新状态

---

## 10. Sprint 03 验收标准

## 10.1 最小演示流

Sprint 03 至少应能演示：

1. 跑一个真实 one_click 查询
2. 结果页显示热门榜
3. 切换增长榜
4. 打开详情页
5. 显示 supporting / opposing evidence
6. 在 partial_success 或 low confidence 条件下正确展示状态
7. 触发 Markdown 导出并下载

## 10.2 结果质量验收

- [ ] 热门榜 Top 10 质量达到内部可接受标准
- [ ] 增长榜不会被极小样本主导
- [ ] 详情摘要与 evidence 基本一致

## 10.3 前端体验验收

- [ ] 关键状态都有稳定 UI
- [ ] 错误恢复路径明确
- [ ] 导出体验完整

## 10.4 发布准备验收

- [ ] release readiness Must Have 基本完成
- [ ] 风险接受项已明确记录

---

## 11. Sprint 03 结束后应具备的输入

Sprint 03 完成后，项目应具备：

1. 可灰度主链路
2. 可解释榜单
3. 可用详情页
4. 可用导出
5. 可执行上线检查

此时可进入：

- 灰度观察期
- 正式发布准备

---

## 12. 推荐下一步产出

基于本文档，建议继续输出：

1. `doc/grey_release_observation_template.md`
2. `doc/post_launch_issue_triage.md`

---

## 13. 一句话结论

Sprint 03 的核心，不是继续扩功能，而是：

> **把需见最关键的结果质量、边界状态和发布稳定性收束到可灰度上线。**

