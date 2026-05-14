#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="${ROOT_DIR}/.runtime"
LOG_DIR="${RUNTIME_DIR}/logs"
PID_DIR="${RUNTIME_DIR}/pids"

mkdir -p "${LOG_DIR}" "${PID_DIR}"

if [[ ! -f "${ROOT_DIR}/.env" ]]; then
  cp "${ROOT_DIR}/.env.example" "${ROOT_DIR}/.env"
  echo "[server-deploy] .env created from .env.example"
fi

set -a
source "${ROOT_DIR}/.env"
set +a

echo "[server-deploy] bootstrapping project"
"${ROOT_DIR}/scripts/bootstrap.sh"

echo "[server-deploy] starting dependencies"
"${ROOT_DIR}/scripts/dev-up.sh"

echo "[server-deploy] applying database migrations"
(
  cd "${ROOT_DIR}/apps/api"
  uv run alembic upgrade head
)

stop_if_running() {
  local pid_file="$1"
  if [[ -f "${pid_file}" ]]; then
    local pid
    pid="$(cat "${pid_file}")"
    if kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" >/dev/null 2>&1 || true
    fi
    rm -f "${pid_file}"
  fi
}

stop_if_running "${PID_DIR}/api.pid"
stop_if_running "${PID_DIR}/worker.pid"
stop_if_running "${PID_DIR}/web.pid"

echo "[server-deploy] starting api"
nohup "${ROOT_DIR}/scripts/run-api.sh" > "${LOG_DIR}/api.log" 2>&1 &
echo $! > "${PID_DIR}/api.pid"

echo "[server-deploy] starting worker"
nohup "${ROOT_DIR}/scripts/run-worker.sh" > "${LOG_DIR}/worker.log" 2>&1 &
echo $! > "${PID_DIR}/worker.pid"

echo "[server-deploy] starting web"
nohup "${ROOT_DIR}/scripts/run-web.sh" > "${LOG_DIR}/web.log" 2>&1 &
echo $! > "${PID_DIR}/web.pid"

sleep 5

echo "[server-deploy] running smoke test"
"${ROOT_DIR}/scripts/smoke-test.sh"

echo "[server-deploy] done"
echo "[server-deploy] logs:"
echo "  api:    ${LOG_DIR}/api.log"
echo "  worker: ${LOG_DIR}/worker.log"
echo "  web:    ${LOG_DIR}/web.log"

