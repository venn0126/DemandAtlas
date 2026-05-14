#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

echo "[dev-down] root: ${ROOT_DIR}"

if ! command -v docker >/dev/null 2>&1; then
  echo "[dev-down] error: docker is not installed"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "[dev-down] error: docker daemon is not running or not reachable"
  exit 1
fi

echo "[dev-down] stopping local dependencies"
(
  cd "${ROOT_DIR}"
  docker compose -f docker-compose.yml down
)

echo "[dev-down] done"
