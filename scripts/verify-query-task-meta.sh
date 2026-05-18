#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
POLL_RETRY_COUNT="${POLL_RETRY_COUNT:-30}"
POLL_INTERVAL_SECONDS="${POLL_INTERVAL_SECONDS:-1}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
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
elif isinstance(value, bool):
    print("true" if value else "false")
elif isinstance(value, (dict, list)):
    print(json.dumps(value, ensure_ascii=False))
else:
    print(value)
' "${field_path}"
}

poll_query_task_until_terminal() {
  local query_task_id="$1"
  local response=""
  local status=""

  for ((attempt = 1; attempt <= POLL_RETRY_COUNT; attempt++)); do
    response="$(
      curl \
        --fail \
        --silent \
        --show-error \
        "${API_BASE_URL}/api/v1/query-tasks/${query_task_id}"
    )"
    status="$(printf '%s' "${response}" | extract_json_field "data.status")"
    echo "[verify-query-task-meta] poll[$attempt] ${query_task_id} -> ${status}"

    if [[ "${status}" == "success" || "${status}" == "partial_success" || "${status}" == "failed" ]]; then
      printf '%s' "${response}"
      return 0
    fi

    sleep "${POLL_INTERVAL_SECONDS}"
  done

  printf '%s' "${response}"
  return 1
}

assert_eq() {
  local expected="$1"
  local actual="$2"
  local label="$3"
  if [[ "${expected}" != "${actual}" ]]; then
    echo "[verify-query-task-meta] error: ${label}: expected=${expected} actual=${actual}"
    exit 1
  fi
}

assert_nonempty() {
  local actual="$1"
  local label="$2"
  if [[ -z "${actual}" ]]; then
    echo "[verify-query-task-meta] error: ${label} is empty"
    exit 1
  fi
}

echo "[verify-query-task-meta] root: ${ROOT_DIR}"
echo "[verify-query-task-meta] api: ${API_BASE_URL}"

echo "[verify-query-task-meta] case 1: success metadata"
SUCCESS_CREATE_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query_type":"directed","keywords":["meta-check"],"time_window":{"preset":"30d"},"force_refresh":true}' \
    "${API_BASE_URL}/api/v1/query-tasks"
)"

SUCCESS_TASK_ID="$(printf '%s' "${SUCCESS_CREATE_RESPONSE}" | extract_json_field "data.query_task_id")"
assert_nonempty "${SUCCESS_TASK_ID}" "success task id"
SUCCESS_FINAL_RESPONSE="$(poll_query_task_until_terminal "${SUCCESS_TASK_ID}")"

SUCCESS_STATUS="$(printf '%s' "${SUCCESS_FINAL_RESPONSE}" | extract_json_field "data.status")"
SUCCESS_WARNING_COUNT="$(printf '%s' "${SUCCESS_FINAL_RESPONSE}" | extract_json_field "meta.warning_count")"
SUCCESS_COVERAGE_STATUS="$(printf '%s' "${SUCCESS_FINAL_RESPONSE}" | extract_json_field "meta.coverage_status")"
SUCCESS_REQUESTED_SOURCE_COUNT="$(printf '%s' "${SUCCESS_FINAL_RESPONSE}" | extract_json_field "meta.requested_source_count")"
SUCCESS_COMPLETED_SOURCE_COUNT="$(printf '%s' "${SUCCESS_FINAL_RESPONSE}" | extract_json_field "meta.completed_source_count")"
SUCCESS_SOURCE_SCOPE_COUNT="$(printf '%s' "${SUCCESS_FINAL_RESPONSE}" | extract_json_field "meta.source_scope_count")"
SUCCESS_RESULT_CLUSTER_COUNT="$(printf '%s' "${SUCCESS_FINAL_RESPONSE}" | extract_json_field "meta.result_cluster_count")"
SUCCESS_PIPELINE_METADATA="$(printf '%s' "${SUCCESS_FINAL_RESPONSE}" | extract_json_field "meta.pipeline_metadata")"

assert_eq "success" "${SUCCESS_STATUS}" "success task final status"
assert_eq "0" "${SUCCESS_WARNING_COUNT}" "success warning_count"
assert_eq "success" "${SUCCESS_COVERAGE_STATUS}" "success coverage_status"
assert_eq "${SUCCESS_REQUESTED_SOURCE_COUNT}" "${SUCCESS_COMPLETED_SOURCE_COUNT}" "success requested/completed source count"
assert_nonempty "${SUCCESS_SOURCE_SCOPE_COUNT}" "success source_scope_count"
assert_nonempty "${SUCCESS_RESULT_CLUSTER_COUNT}" "success result_cluster_count"
assert_nonempty "${SUCCESS_PIPELINE_METADATA}" "success pipeline_metadata"

echo "[verify-query-task-meta] case 2: partial_success metadata"
PARTIAL_CREATE_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query_type":"directed","keywords":["meta-partial"],"subreddits":["a","b","c"],"time_window":{"preset":"30d"},"force_refresh":true}' \
    "${API_BASE_URL}/api/v1/query-tasks"
)"

PARTIAL_TASK_ID="$(printf '%s' "${PARTIAL_CREATE_RESPONSE}" | extract_json_field "data.query_task_id")"
assert_nonempty "${PARTIAL_TASK_ID}" "partial task id"
PARTIAL_FINAL_RESPONSE="$(poll_query_task_until_terminal "${PARTIAL_TASK_ID}")"

PARTIAL_STATUS="$(printf '%s' "${PARTIAL_FINAL_RESPONSE}" | extract_json_field "data.status")"
PARTIAL_WARNING_COUNT="$(printf '%s' "${PARTIAL_FINAL_RESPONSE}" | extract_json_field "meta.warning_count")"
PARTIAL_COVERAGE_STATUS="$(printf '%s' "${PARTIAL_FINAL_RESPONSE}" | extract_json_field "meta.coverage_status")"
PARTIAL_REQUESTED_SOURCE_COUNT="$(printf '%s' "${PARTIAL_FINAL_RESPONSE}" | extract_json_field "meta.requested_source_count")"
PARTIAL_COMPLETED_SOURCE_COUNT="$(printf '%s' "${PARTIAL_FINAL_RESPONSE}" | extract_json_field "meta.completed_source_count")"
PARTIAL_SOURCE_SCOPE_COUNT="$(printf '%s' "${PARTIAL_FINAL_RESPONSE}" | extract_json_field "meta.source_scope_count")"
PARTIAL_RESULT_CLUSTER_COUNT="$(printf '%s' "${PARTIAL_FINAL_RESPONSE}" | extract_json_field "meta.result_cluster_count")"
PARTIAL_WARNINGS="$(printf '%s' "${PARTIAL_FINAL_RESPONSE}" | extract_json_field "data.warnings")"
PARTIAL_PIPELINE_METADATA="$(printf '%s' "${PARTIAL_FINAL_RESPONSE}" | extract_json_field "meta.pipeline_metadata")"

assert_eq "partial_success" "${PARTIAL_STATUS}" "partial task final status"
assert_eq "partial_success" "${PARTIAL_COVERAGE_STATUS}" "partial coverage_status"
assert_nonempty "${PARTIAL_WARNING_COUNT}" "partial warning_count"
assert_nonempty "${PARTIAL_WARNINGS}" "partial warnings"
assert_nonempty "${PARTIAL_SOURCE_SCOPE_COUNT}" "partial source_scope_count"
assert_nonempty "${PARTIAL_RESULT_CLUSTER_COUNT}" "partial result_cluster_count"
assert_nonempty "${PARTIAL_PIPELINE_METADATA}" "partial pipeline_metadata"

if (( PARTIAL_COMPLETED_SOURCE_COUNT >= PARTIAL_REQUESTED_SOURCE_COUNT )); then
  echo "[verify-query-task-meta] error: partial completed_source_count should be less than requested_source_count"
  echo "[verify-query-task-meta] requested=${PARTIAL_REQUESTED_SOURCE_COUNT} completed=${PARTIAL_COMPLETED_SOURCE_COUNT}"
  exit 1
fi

echo "[verify-query-task-meta] success case response:"
echo "${SUCCESS_FINAL_RESPONSE}"
echo
echo "[verify-query-task-meta] partial_success case response:"
echo "${PARTIAL_FINAL_RESPONSE}"
echo
echo "[verify-query-task-meta] all checks passed"
