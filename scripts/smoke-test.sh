#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
WEB_BASE_URL="${WEB_BASE_URL:-http://127.0.0.1:4173}"

echo "[smoke-test] root: ${ROOT_DIR}"
echo "[smoke-test] api: ${API_BASE_URL}"
echo "[smoke-test] web: ${WEB_BASE_URL}"

echo "[smoke-test] checking API health"
curl --fail --silent --show-error "${API_BASE_URL}/api/v1/healthz" >/dev/null

echo "[smoke-test] checking topic templates list"
curl --fail --silent --show-error "${API_BASE_URL}/api/v1/topic-templates" >/dev/null

echo "[smoke-test] checking web root"
curl --fail --silent --show-error "${WEB_BASE_URL}/" >/dev/null

echo "[smoke-test] smoke test passed"
