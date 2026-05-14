#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
API_RELOAD="${API_RELOAD:-0}"
API_LOG_FILE="${ROOT_DIR}/.runtime-api.log"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
API_RELOAD="${API_RELOAD:-0}"

echo "[restart-api] root: ${ROOT_DIR}"
echo "[restart-api] host: ${API_HOST}"
echo "[restart-api] port: ${API_PORT}"
echo "[restart-api] reload: ${API_RELOAD}"

echo "[restart-api] syncing api dependencies"
(
  cd "${ROOT_DIR}/apps/api"
  uv sync
)

if [[ -f "${ROOT_DIR}/.env" ]]; then
  cp "${ROOT_DIR}/.env" "${ROOT_DIR}/apps/api/.env"
fi

echo "[restart-api] stopping existing uvicorn processes"
pkill -9 -f "uvicorn app.main:app" >/dev/null 2>&1 || true
sleep 2

LISTEN_PID="$(lsof -t -iTCP:${API_PORT} -sTCP:LISTEN 2>/dev/null || true)"
if [[ -n "${LISTEN_PID}" ]]; then
  echo "[restart-api] killing stale listener pid=${LISTEN_PID}"
  kill -9 "${LISTEN_PID}" >/dev/null 2>&1 || true
  sleep 2
fi

if lsof -nP -iTCP:${API_PORT} -sTCP:LISTEN >/dev/null 2>&1; then
  echo "[restart-api] error: port ${API_PORT} is still occupied"
  lsof -nP -iTCP:${API_PORT} -sTCP:LISTEN || true
  exit 1
fi

: > "${API_LOG_FILE}"

echo "[restart-api] starting api"
(
  cd "${ROOT_DIR}"
  nohup ./scripts/run-api.sh > "${API_LOG_FILE}" 2>&1 &
)

sleep 5

echo "[restart-api] recent api log:"
tail -n 50 "${API_LOG_FILE}" || true

echo "[restart-api] checking api health"
curl --fail --silent --show-error "http://${API_HOST}:${API_PORT}/api/v1/healthz" >/dev/null

echo "[restart-api] done"
