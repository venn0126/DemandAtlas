#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
WEB_BASE_URL="${WEB_BASE_URL:-http://127.0.0.1:4173}"
QUERY_TASK_ID="${QUERY_TASK_ID:-qt_pending}"
RESULT_SNAPSHOT_ID="${RESULT_SNAPSHOT_ID:-rs_01JVA1T4WM4B3PG5N8W1HEP7QA}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
WEB_BASE_URL="${WEB_BASE_URL:-http://127.0.0.1:4173}"
QUERY_TASK_ID="${QUERY_TASK_ID:-qt_pending}"
RESULT_SNAPSHOT_ID="${RESULT_SNAPSHOT_ID:-rs_01JVA1T4WM4B3PG5N8W1HEP7QA}"

echo "[smoke-test] root: ${ROOT_DIR}"
echo "[smoke-test] api: ${API_BASE_URL}"
echo "[smoke-test] web: ${WEB_BASE_URL}"

echo "[smoke-test] checking API health"
curl --fail --silent --show-error "${API_BASE_URL}/api/v1/healthz" >/dev/null

echo "[smoke-test] checking topic templates list"
curl --fail --silent --show-error "${API_BASE_URL}/api/v1/topic-templates" >/dev/null

echo "[smoke-test] checking query task create (one_click cache hit)"
curl \
  --fail \
  --silent \
  --show-error \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query_type":"one_click","template_id":"tpl_ai_tools","time_window":{"preset":"30d"}}' \
  "${API_BASE_URL}/api/v1/query-tasks" >/dev/null

echo "[smoke-test] checking query task status"
curl \
  --fail \
  --silent \
  --show-error \
  "${API_BASE_URL}/api/v1/query-tasks/${QUERY_TASK_ID}" >/dev/null

echo "[smoke-test] checking result snapshot summary"
curl \
  --fail \
  --silent \
  --show-error \
  "${API_BASE_URL}/api/v1/result-snapshots/${RESULT_SNAPSHOT_ID}" >/dev/null

echo "[smoke-test] checking web root"
curl --fail --silent --show-error "${WEB_BASE_URL}/" >/dev/null

echo "[smoke-test] smoke test passed"
