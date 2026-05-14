#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_PORT="${API_PORT:-8000}"
API_HOST="${API_HOST:-127.0.0.1}"
API_RELOAD="${API_RELOAD:-0}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

API_PORT="${API_PORT:-8000}"
API_HOST="${API_HOST:-127.0.0.1}"
API_RELOAD="${API_RELOAD:-0}"

echo "[run-api] root: ${ROOT_DIR}"
echo "[run-api] host: ${API_HOST}"
echo "[run-api] port: ${API_PORT}"
echo "[run-api] reload: ${API_RELOAD}"

cd "${ROOT_DIR}/apps/api"
if [[ "${API_RELOAD}" == "1" ]]; then
  uv run uvicorn app.main:app --host "${API_HOST}" --port "${API_PORT}" --reload
else
  uv run uvicorn app.main:app --host "${API_HOST}" --port "${API_PORT}"
fi
