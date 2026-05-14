# Demand Atlas｜需见 测试机准备清单

## 1. 说明

本文档用于在海外测试机上启动 **Demand Atlas｜需见** 前，逐项确认环境、依赖、目录、网络与运行条件。

适用范围：

- 单台海外测试机
- 用于开发验证 / 联调 / 预发布测试
- 当前阶段以 Docker + 本地进程启动为主

---

## 2. 目标

完成本清单后，测试机应具备以下能力：

- 拉取仓库代码
- 初始化前后端与 worker 依赖
- 启动 PostgreSQL / Redis / MinIO
- 启动 API / Worker / Web
- 执行基础 smoke test

---

## 3. 基础环境检查

### 3.1 操作系统

- [ ] Linux 发行版可用
- [ ] 系统时间正确
- [ ] 时区已确认

### 3.2 用户与权限

- [ ] 有可登录用户
- [ ] 该用户可执行 `sudo`
- [ ] 该用户可读写应用目录

### 3.3 常用工具

- [ ] `git`
- [ ] `curl`
- [ ] `bash`
- [ ] `lsof`

---

## 4. 运行时依赖检查

### 4.1 Docker

- [ ] `docker` 已安装
- [ ] Docker daemon 正常运行
- [ ] 当前用户可直接执行 `docker`

建议验证：

```bash
docker --version
docker info
```

### 4.2 Python / uv

- [ ] Python 3.12+ 已安装
- [ ] `uv` 已安装

建议验证：

```bash
python3 --version
uv --version
```

### 4.3 Node / pnpm

- [ ] Node.js 已安装
- [ ] `pnpm` 已安装

建议验证：

```bash
node -v
pnpm -v
```

### 4.4 宝塔面板占用检查

若机器已安装宝塔，请优先确认端口占用：

- [ ] `8000`
- [ ] `4173`
- [ ] `5432`
- [ ] `6379`
- [ ] `9000`
- [ ] `9001`

建议验证：

```bash
sudo lsof -nP -iTCP -sTCP:LISTEN
```

若端口冲突，请优先修改：

- `.env` 中的 `API_PORT`
- `.env` 中的 `WEB_PORT`
- `.env` 中的 `POSTGRES_BIND_PORT`
- `.env` 中的 `REDIS_BIND_PORT`
- `.env` 中的 `MINIO_BIND_PORT`
- `.env` 中的 `MINIO_CONSOLE_BIND_PORT`

---

## 5. 仓库目录准备

建议目录：

```text
/srv/demand-atlas
```

检查项：

- [ ] 目录已创建
- [ ] 当前用户对目录有写权限
- [ ] 仓库已 clone 到该目录

建议验证：

```bash
mkdir -p /srv/demand-atlas
cd /srv/demand-atlas
git clone <repo-url> .
```

---

## 6. 环境变量准备

检查项：

- [ ] 根目录 `.env.example` 存在
- [ ] 已复制为 `.env`
- [ ] 已按测试机实际情况修改

重点字段：

- [ ] `APP_ENV`
- [ ] `LOG_LEVEL`
- [ ] `API_PORT`
- [ ] `API_BASE_URL`
- [ ] `WEB_PORT`
- [ ] `VITE_API_BASE_URL`
- [ ] `POSTGRES_*`
- [ ] `DATABASE_URL`
- [ ] `REDIS_*`
- [ ] `MINIO_*`

建议验证：

```bash
cp .env.example .env
```

---

## 7. 端口与网络检查

当前最小链路建议开放 / 可访问：

- [ ] `5432` PostgreSQL
- [ ] `6379` Redis
- [ ] `9000` MinIO API
- [ ] `9001` MinIO Console
- [ ] `8000` API
- [ ] `4173` Web

说明：

- 若测试机仅自用，可先只开放 `8000` / `4173`
- 数据库与缓存端口可限制为本机访问

---

## 8. 仓库脚本检查

检查项：

- [ ] `scripts/bootstrap.sh`
- [ ] `scripts/dev-up.sh`
- [ ] `scripts/dev-down.sh`
- [ ] `scripts/run-api.sh`
- [ ] `scripts/run-worker.sh`
- [ ] `scripts/run-web.sh`
- [ ] `scripts/smoke-test.sh`
- [ ] `scripts/server-bootstrap-ubuntu.sh`
- [ ] `scripts/server-deploy.sh`
- [ ] `scripts/server-stop.sh`

建议验证：

```bash
bash -n scripts/bootstrap.sh scripts/dev-up.sh scripts/dev-down.sh scripts/run-api.sh scripts/run-worker.sh scripts/run-web.sh scripts/smoke-test.sh
```

---

## 9. 当前应用状态预期

当前测试机阶段不要求：

- 完整生产部署
- CI/CD 自动发布
- 完整数据库真实写入验证

当前测试机阶段应能验证：

- [ ] API health
- [ ] TopicTemplate 列表
- [ ] QueryTask 创建
- [ ] QueryTask 状态查询
- [ ] ResultSnapshot 摘要读取
- [ ] Web 前端可访问
- [ ] Worker actor 可导入

---

## 10. 最终准备完成标准

满足以下条件即可认为测试机准备完成：

- [ ] Docker 可用
- [ ] `uv` / `pnpm` 可用
- [ ] 仓库代码已拉取
- [ ] `.env` 已配置
- [ ] 脚本存在且语法通过
- [ ] 端口策略已确认

---

## 11. 一句话结论

> 当测试机具备 Docker、uv、pnpm、正确的 `.env` 与可执行脚本时，就可以进入启动与联调阶段。
