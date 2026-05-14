#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_PORT="${API_PORT:-8000}"
API_HOST="${API_HOST:-127.0.0.1}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

API_PORT="${API_PORT:-8000}"
API_HOST="${API_HOST:-127.0.0.1}"

echo "[run-api] root: ${ROOT_DIR}"
echo "[run-api] host: ${API_HOST}"
echo "[run-api] port: ${API_PORT}"

cd "${ROOT_DIR}/apps/api"
uv run uvicorn app.main:app --host "${API_HOST}" --port "${API_PORT}" --reload
