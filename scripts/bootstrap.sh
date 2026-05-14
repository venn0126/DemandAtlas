#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[bootstrap] root: ${ROOT_DIR}"

if ! command -v uv >/dev/null 2>&1; then
  echo "[bootstrap] error: uv is not installed"
  exit 1
fi

if ! command -v pnpm >/dev/null 2>&1; then
  echo "[bootstrap] error: pnpm is not installed"
  exit 1
fi

if [[ -f "${ROOT_DIR}/apps/api/pyproject.toml" ]]; then
  echo "[bootstrap] syncing Python dependencies for apps/api"
  (
    cd "${ROOT_DIR}/apps/api"
    uv sync
  )
else
  echo "[bootstrap] skip: apps/api/pyproject.toml not found"
fi

if [[ -f "${ROOT_DIR}/apps/web/package.json" ]]; then
  echo "[bootstrap] installing Node dependencies for apps/web"
  (
    cd "${ROOT_DIR}/apps/web"
    pnpm install
  )
else
  echo "[bootstrap] skip: apps/web/package.json not found"
fi

if [[ -d "${ROOT_DIR}/apps/worker" ]]; then
  echo "[bootstrap] info: apps/worker exists"
else
  echo "[bootstrap] info: apps/worker is not initialized yet"
fi

echo "[bootstrap] done"
echo "[bootstrap] next suggested steps:"
echo "  1. cp .env.example .env"
echo "  2. ./scripts/dev-up.sh"
echo "  3. cd apps/api && uv run alembic upgrade head"
echo "  4. cd apps/api && uv run uvicorn app.main:app --reload --port 8000"
echo "  5. cd apps/web && pnpm dev"
