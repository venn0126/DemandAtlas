#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[dev-up] root: ${ROOT_DIR}"

if ! command -v docker >/dev/null 2>&1; then
  echo "[dev-up] error: docker is not installed"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "[dev-up] error: docker daemon is not running or not reachable"
  exit 1
fi

echo "[dev-up] starting local dependencies: postgres redis minio"
(
  cd "${ROOT_DIR}"
  docker compose -f docker-compose.yml up -d postgres redis minio
)

if [[ -d "${ROOT_DIR}/apps/api" ]]; then
  echo "[dev-up] syncing Python dependencies for apps/api"
  (
    cd "${ROOT_DIR}/apps/api"
    uv sync
  )
fi

echo "[dev-up] done"
echo "[dev-up] next suggested steps:"
echo "  1. cd apps/api && uv run alembic upgrade head"
echo "  2. cd apps/api && uv run uvicorn app.main:app --reload --port 8000"
echo "  3. cd apps/web && pnpm dev"

