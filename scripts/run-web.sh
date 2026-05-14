#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_HOST="${WEB_HOST:-127.0.0.1}"
WEB_PORT="${WEB_PORT:-4173}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

WEB_HOST="${WEB_HOST:-127.0.0.1}"
WEB_PORT="${WEB_PORT:-4173}"

echo "[run-web] root: ${ROOT_DIR}"
echo "[run-web] host: ${WEB_HOST}"
echo "[run-web] port: ${WEB_PORT}"

cd "${ROOT_DIR}/apps/web"
pnpm dev --host "${WEB_HOST}" --port "${WEB_PORT}"
