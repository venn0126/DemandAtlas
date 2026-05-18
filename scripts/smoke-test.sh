#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
WEB_BASE_URL="${WEB_BASE_URL:-http://127.0.0.1:4173}"
SMOKE_TEST_MODE="${SMOKE_TEST_MODE:-real_async}"
QUERY_TASK_ID="${QUERY_TASK_ID:-qt_pending}"
RESULT_SNAPSHOT_ID="${RESULT_SNAPSHOT_ID:-rs_01JVA1T4WM4B3PG5N8W1HEP7QA}"
POLL_RETRY_COUNT="${POLL_RETRY_COUNT:-30}"
POLL_INTERVAL_SECONDS="${POLL_INTERVAL_SECONDS:-1}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
WEB_BASE_URL="${WEB_BASE_URL:-http://127.0.0.1:4173}"
SMOKE_TEST_MODE="${SMOKE_TEST_MODE:-real_async}"
QUERY_TASK_ID="${QUERY_TASK_ID:-qt_pending}"
RESULT_SNAPSHOT_ID="${RESULT_SNAPSHOT_ID:-rs_01JVA1T4WM4B3PG5N8W1HEP7QA}"
POLL_RETRY_COUNT="${POLL_RETRY_COUNT:-30}"
POLL_INTERVAL_SECONDS="${POLL_INTERVAL_SECONDS:-1}"

extract_json_field() {
  local field_path="$1"
  python3 -c '
import json
import sys

payload = json.load(sys.stdin)
value = payload
for key in sys.argv[1].split("."):
    if isinstance(value, list):
        value = value[int(key)]
    else:
        value = value[key]

if value is None:
    print("")
elif isinstance(value, (dict, list)):
    print(json.dumps(value, ensure_ascii=False))
else:
    print(value)
' "${field_path}"
}

echo "[smoke-test] root: ${ROOT_DIR}"
echo "[smoke-test] api: ${API_BASE_URL}"
echo "[smoke-test] web: ${WEB_BASE_URL}"
echo "[smoke-test] mode: ${SMOKE_TEST_MODE}"

echo "[smoke-test] checking API health"
curl --fail --silent --show-error "${API_BASE_URL}/api/v1/healthz" >/dev/null

echo "[smoke-test] checking topic templates list"
curl --fail --silent --show-error "${API_BASE_URL}/api/v1/topic-templates" >/dev/null

echo "[smoke-test] checking query task create (one_click warmup)"
ONE_CLICK_WARMUP_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query_type":"one_click","template_id":"tpl_ai_tools","time_window":{"preset":"30d"}}' \
    "${API_BASE_URL}/api/v1/query-tasks"
)"

echo "[smoke-test] checking query task create (one_click cache hit)"
ONE_CLICK_CACHE_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query_type":"one_click","template_id":"tpl_ai_tools","time_window":{"preset":"30d"}}' \
    "${API_BASE_URL}/api/v1/query-tasks"
)"

ONE_CLICK_EXECUTION_MODE="$(printf '%s' "${ONE_CLICK_CACHE_RESPONSE}" | extract_json_field "data.execution_mode")"
if [[ "${ONE_CLICK_EXECUTION_MODE}" != "cache_hit" ]]; then
  echo "[smoke-test] error: one_click second request did not return cache_hit"
  echo "${ONE_CLICK_WARMUP_RESPONSE}"
  echo "${ONE_CLICK_CACHE_RESPONSE}"
  exit 1
fi

echo "[smoke-test] checking query task create (one_click force_refresh bypass)"
ONE_CLICK_FORCE_REFRESH_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query_type":"one_click","template_id":"tpl_ai_tools","time_window":{"preset":"30d"},"force_refresh":true}' \
    "${API_BASE_URL}/api/v1/query-tasks"
)"

ONE_CLICK_FORCE_REFRESH_MODE="$(printf '%s' "${ONE_CLICK_FORCE_REFRESH_RESPONSE}" | extract_json_field "data.execution_mode")"
ONE_CLICK_FORCE_REFRESH_APPLIED="$(printf '%s' "${ONE_CLICK_FORCE_REFRESH_RESPONSE}" | extract_json_field "meta.force_refresh_applied")"
if [[ "${ONE_CLICK_FORCE_REFRESH_MODE}" != "async" || "${ONE_CLICK_FORCE_REFRESH_APPLIED}" != "True" ]]; then
  echo "[smoke-test] error: one_click force_refresh did not bypass cache as expected"
  echo "${ONE_CLICK_FORCE_REFRESH_RESPONSE}"
  exit 1
fi

if [[ "${SMOKE_TEST_MODE}" == "demo_static" ]]; then
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
else
  echo "[smoke-test] checking query task create (directed async)"
  CREATE_RESPONSE="$(
    curl \
      --fail \
      --silent \
      --show-error \
      -X POST \
      -H "Content-Type: application/json" \
      -d '{"query_type":"directed","keywords":["smoke-test"],"time_window":{"preset":"30d"}}' \
      "${API_BASE_URL}/api/v1/query-tasks"
  )"

  QUERY_TASK_ID="$(printf '%s' "${CREATE_RESPONSE}" | extract_json_field "data.query_task_id")"

  if [[ -z "${QUERY_TASK_ID}" ]]; then
    echo "[smoke-test] error: failed to parse query_task_id from create response"
    echo "${CREATE_RESPONSE}"
    exit 1
  fi

  echo "[smoke-test] polling query task status: ${QUERY_TASK_ID}"
  TASK_RESPONSE=""
  TASK_STATUS=""
  RESULT_SNAPSHOT_ID=""

  for ((attempt = 1; attempt <= POLL_RETRY_COUNT; attempt++)); do
    TASK_RESPONSE="$(
      curl \
        --fail \
        --silent \
        --show-error \
        "${API_BASE_URL}/api/v1/query-tasks/${QUERY_TASK_ID}"
    )"
    TASK_STATUS="$(printf '%s' "${TASK_RESPONSE}" | extract_json_field "data.status")"

    if [[ "${TASK_STATUS}" == "success" || "${TASK_STATUS}" == "partial_success" ]]; then
      RESULT_SNAPSHOT_ID="$(printf '%s' "${TASK_RESPONSE}" | extract_json_field "data.result_snapshot_id")"
      break
    fi

    if [[ "${TASK_STATUS}" == "failed" ]]; then
      echo "[smoke-test] error: query task failed"
      echo "${TASK_RESPONSE}"
      exit 1
    fi

    sleep "${POLL_INTERVAL_SECONDS}"
  done

  if [[ -z "${RESULT_SNAPSHOT_ID}" ]]; then
    echo "[smoke-test] error: query task did not finish within polling window"
    echo "${TASK_RESPONSE}"
    exit 1
  fi

  echo "[smoke-test] checking result snapshot summary: ${RESULT_SNAPSHOT_ID}"
  curl \
    --fail \
    --silent \
    --show-error \
    "${API_BASE_URL}/api/v1/result-snapshots/${RESULT_SNAPSHOT_ID}" >/dev/null

  echo "[smoke-test] checking query task create (directed cache hit)"
  DIRECTED_CACHE_RESPONSE="$(
    curl \
      --fail \
      --silent \
      --show-error \
      -X POST \
      -H "Content-Type: application/json" \
      -d '{"query_type":"directed","keywords":["smoke-test"],"time_window":{"preset":"30d"}}' \
      "${API_BASE_URL}/api/v1/query-tasks"
  )"

  DIRECTED_EXECUTION_MODE="$(printf '%s' "${DIRECTED_CACHE_RESPONSE}" | extract_json_field "data.execution_mode")"
  if [[ "${DIRECTED_EXECUTION_MODE}" != "cache_hit" ]]; then
    echo "[smoke-test] error: directed second request did not return cache_hit"
    echo "${DIRECTED_CACHE_RESPONSE}"
    exit 1
  fi

  echo "[smoke-test] checking query task create (directed force_refresh bypass)"
  DIRECTED_FORCE_REFRESH_RESPONSE="$(
    curl \
      --fail \
      --silent \
      --show-error \
      -X POST \
      -H "Content-Type: application/json" \
      -d '{"query_type":"directed","keywords":["smoke-test"],"time_window":{"preset":"30d"},"force_refresh":true}' \
      "${API_BASE_URL}/api/v1/query-tasks"
  )"

  DIRECTED_FORCE_REFRESH_MODE="$(printf '%s' "${DIRECTED_FORCE_REFRESH_RESPONSE}" | extract_json_field "data.execution_mode")"
  DIRECTED_FORCE_REFRESH_APPLIED="$(printf '%s' "${DIRECTED_FORCE_REFRESH_RESPONSE}" | extract_json_field "meta.force_refresh_applied")"
  if [[ "${DIRECTED_FORCE_REFRESH_MODE}" != "async" || "${DIRECTED_FORCE_REFRESH_APPLIED}" != "True" ]]; then
    echo "[smoke-test] error: directed force_refresh did not bypass cache as expected"
    echo "${DIRECTED_FORCE_REFRESH_RESPONSE}"
    exit 1
  fi
fi

echo "[smoke-test] checking web root"
curl --fail --silent --show-error "${WEB_BASE_URL}/" >/dev/null

echo "[smoke-test] smoke test passed"
