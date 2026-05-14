#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKER_LOG_FILE="${ROOT_DIR}/.runtime-worker.log"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

echo "[restart-worker] root: ${ROOT_DIR}"

echo "[restart-worker] syncing worker dependencies"
(
  cd "${ROOT_DIR}/apps/worker"
  uv sync
)

if [[ -f "${ROOT_DIR}/.env" ]]; then
  cp "${ROOT_DIR}/.env" "${ROOT_DIR}/apps/worker/.env"
fi

echo "[restart-worker] stopping existing worker processes"
pkill -9 -f "dramatiq worker.main" >/dev/null 2>&1 || true
pkill -9 -f "dramatiq worker.jobs.health worker.jobs.query_task_pipeline" >/dev/null 2>&1 || true
sleep 2

: > "${WORKER_LOG_FILE}"

echo "[restart-worker] starting worker"
(
  cd "${ROOT_DIR}"
  nohup ./scripts/run-worker.sh > "${WORKER_LOG_FILE}" 2>&1 &
)

sleep 5

echo "[restart-worker] recent worker log:"
tail -n 50 "${WORKER_LOG_FILE}" || true

if ! pgrep -f "dramatiq worker.main" >/dev/null 2>&1; then
  echo "[restart-worker] error: worker process is not running"
  exit 1
fi

echo "[restart-worker] done"
