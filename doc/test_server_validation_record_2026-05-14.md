# Demand Atlas｜需见 测试机验证记录

## 1. 基本信息

- 验证日期：2026-05-14
- 机器环境：Ubuntu
- 仓库路径：`/home/ubuntu/DemandAtlas`
- 验证方式：手工登录 + 仓库脚本启动

---

## 2. 本次使用配置

已确认的关键端口：

- API：`127.0.0.1:18000`
- Web：`127.0.0.1:14173`
- PostgreSQL 宿主机映射端口：`15432`

本次补充修正项：

- `.env` 中增加：

```text
WEB_BASE_URL=http://127.0.0.1:14173
```

说明：

- Web 实际运行在 `14173`
- `smoke-test.sh` 初次失败原因是未显式设置 `WEB_BASE_URL`

---

## 3. 启动链路验证结果

本次已完成：

1. 依赖初始化
   - `./scripts/bootstrap.sh`
2. 依赖服务启动
   - `./scripts/dev-up.sh`
3. 数据库 migration
   - `cd apps/api && uv run alembic upgrade head`
4. API 启动
5. Worker 启动
6. Web 启动
7. Smoke test

---

## 4. Smoke Test 结果

执行命令：

```bash
./scripts/smoke-test.sh
```

结果：

```text
[smoke-test] smoke test passed
```

---

## 5. 本次已验证通过的项目

- API health
- TopicTemplate 列表
- QueryTask 创建
- QueryTask 状态读取
- ResultSnapshot 摘要读取
- Web 根页面可访问
- PostgreSQL migration 在线执行通过
- QueryTask 真实数据库写入通过
- Worker 消费 QueryTask 并写回阶段日志通过
- ResultSnapshot 真实数据库写入通过

---

## 6. 真实异步链路验证结果

本次已验证真实链路：

```text
POST /api/v1/query-tasks
  -> 写入 query_tasks
  -> Worker 消费 run_query_task_pipeline
  -> 写入 query_task_run_logs
  -> 写入 result_snapshots
  -> GET /api/v1/query-tasks/{id} 返回 success
```

已确认：

- `query_task_id` 返回真实 UUID
- `query_tasks.status` 从 `pending` 更新为 `success`
- `query_task_run_logs` 成功写入 9 条阶段日志
- `result_snapshots` 成功生成真实记录
- `GET /api/v1/result-snapshots/{id}` 可读取真实快照

---

## 7. 本次排查与修复记录

已修复的测试机问题包括：

1. API 使用旧进程导致仍返回静态占位 `qt_*`
2. 数据库连接端口与 `.env` 中 `DATABASE_URL` 不一致
3. Worker 使用错误启动方式，未加载自定义 broker
4. Worker 默认连接 `6379`，未使用测试机 Redis 映射端口
5. Worker 写回数据库时 UUID / string 比较类型不匹配

当前已确认修复：

- 使用 `restart-api.sh` 可稳定重启 API
- `run-worker.sh` 已改为 `uv run dramatiq worker.main`
- `restart-worker.sh` 已加入脚本集
- `REDIS_URL` 已通过 `.env` 显式配置
- Worker 数据库写回链路已可用

---

## 8. 当前结论

> 海外测试机最小可用闭环与最小真实异步链路都已跑通。

当前可确认：

- 仓库脚本可用于测试机初始化与启动
- API / Worker / Web 可按当前流程拉起
- 当前主链 smoke test 已通过
- 最小真实 QueryTask -> Worker -> DB -> ResultSnapshot 链路已通过

补充说明：

- 2026-05-15 已在本地仓库继续推进：
  - `QueryTask` enqueue 失败即时写回 `failed`
  - Worker 占位快照改为基于请求内容生成动态 `summary_stats`
  - `scripts/smoke-test.sh` 默认切到真实异步链路模式
- 2026-05-18 已在本地仓库继续推进：
  - OneClick / Directed 都已支持成功缓存命中与进行中任务复用
  - 成功缓存已加入 freshness 策略，并支持按 query_type 配置
  - `partial_success` 复用策略已支持配置化
  - `force_refresh=true` 已显式绕过成功缓存与进行中任务复用
  - `scripts/smoke-test.sh` 已增加：
    - OneClick 二次 `cache_hit`
    - Directed 二次 `cache_hit`
    - OneClick / Directed `force_refresh=true` 绕过缓存验证
- 上述更新当前仅完成本地静态校验，尚未写入本记录的测试机复验结论

---

## 9. 当前遗留说明

本次通过的是“测试机可用性 + 最小真实链路验证”，不是最终生产验证。

仍待后续继续推进的方向包括：

- TopicTemplate / QueryTask / ResultSnapshot 全面替换静态回退
- Worker pipeline 从占位执行升级为真实业务处理
- 更完整的错误处理、缓存、性能优化
