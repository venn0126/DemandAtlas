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

---

## 6. 当前结论

> 海外测试机最小可用闭环已跑通。

当前可确认：

- 仓库脚本可用于测试机初始化与启动
- API / Worker / Web 可按当前流程拉起
- 当前主链 smoke test 已通过

---

## 7. 当前遗留说明

本次通过的是“骨架与主链可用性验证”，不是最终生产验证。

仍待后续继续推进的方向包括：

- API 数据库真实读写链路替换静态返回
- Worker 真正写回 QueryTask / ResultSnapshot
- 更完整的错误处理、缓存、性能优化

