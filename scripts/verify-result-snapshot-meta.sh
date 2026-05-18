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
    echo "[verify-result-snapshot-meta] poll[$attempt] ${query_task_id} -> ${status}" >&2

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
    echo "[verify-result-snapshot-meta] error: ${label}: expected=${expected} actual=${actual}"
    exit 1
  fi
}

assert_nonempty() {
  local actual="$1"
  local label="$2"
  if [[ -z "${actual}" ]]; then
    echo "[verify-result-snapshot-meta] error: ${label} is empty"
    exit 1
  fi
}

echo "[verify-result-snapshot-meta] root: ${ROOT_DIR}"
echo "[verify-result-snapshot-meta] api: ${API_BASE_URL}"

echo "[verify-result-snapshot-meta] case 1: success snapshot metadata"
SUCCESS_CREATE_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query_type":"directed","keywords":["snapshot-meta-success"],"time_window":{"preset":"30d"},"force_refresh":true}' \
    "${API_BASE_URL}/api/v1/query-tasks"
)"

SUCCESS_TASK_ID="$(printf '%s' "${SUCCESS_CREATE_RESPONSE}" | extract_json_field "data.query_task_id")"
assert_nonempty "${SUCCESS_TASK_ID}" "success task id"
SUCCESS_TASK_RESPONSE="$(poll_query_task_until_terminal "${SUCCESS_TASK_ID}")"
SUCCESS_TASK_STATUS="$(printf '%s' "${SUCCESS_TASK_RESPONSE}" | extract_json_field "data.status")"
SUCCESS_SNAPSHOT_ID="$(printf '%s' "${SUCCESS_TASK_RESPONSE}" | extract_json_field "data.result_snapshot_id")"

assert_eq "success" "${SUCCESS_TASK_STATUS}" "success task final status"
assert_nonempty "${SUCCESS_SNAPSHOT_ID}" "success snapshot id"

SUCCESS_SNAPSHOT_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    "${API_BASE_URL}/api/v1/result-snapshots/${SUCCESS_SNAPSHOT_ID}"
)"

SUCCESS_RESPONSE_SOURCE="$(printf '%s' "${SUCCESS_SNAPSHOT_RESPONSE}" | extract_json_field "meta.response_source")"
SUCCESS_WARNING_COUNT="$(printf '%s' "${SUCCESS_SNAPSHOT_RESPONSE}" | extract_json_field "meta.warning_count")"
SUCCESS_PIPELINE_METADATA="$(printf '%s' "${SUCCESS_SNAPSHOT_RESPONSE}" | extract_json_field "meta.pipeline_metadata")"
SUCCESS_PIPELINE_COVERAGE_STATUS="$(printf '%s' "${SUCCESS_SNAPSHOT_RESPONSE}" | extract_json_field "meta.pipeline_metadata.coverage.status")"
SUCCESS_PIPELINE_SOURCE_COUNT="$(printf '%s' "${SUCCESS_SNAPSHOT_RESPONSE}" | extract_json_field "meta.pipeline_metadata.source_scope.source_count")"
SUCCESS_PIPELINE_CLUSTER_COUNT="$(printf '%s' "${SUCCESS_SNAPSHOT_RESPONSE}" | extract_json_field "meta.pipeline_metadata.result_profile.cluster_count")"
SUCCESS_SUMMARY_CLUSTER_COUNT="$(printf '%s' "${SUCCESS_SNAPSHOT_RESPONSE}" | extract_json_field "data.summary_stats.cluster_count")"

assert_eq "database" "${SUCCESS_RESPONSE_SOURCE}" "success snapshot response_source"
assert_eq "0" "${SUCCESS_WARNING_COUNT}" "success snapshot warning_count"
assert_eq "success" "${SUCCESS_PIPELINE_COVERAGE_STATUS}" "success snapshot coverage status"
assert_nonempty "${SUCCESS_PIPELINE_METADATA}" "success snapshot pipeline_metadata"
assert_nonempty "${SUCCESS_PIPELINE_SOURCE_COUNT}" "success snapshot source_count"
assert_eq "${SUCCESS_SUMMARY_CLUSTER_COUNT}" "${SUCCESS_PIPELINE_CLUSTER_COUNT}" "success snapshot cluster count consistency"

echo "[verify-result-snapshot-meta] case 2: partial_success snapshot metadata"
PARTIAL_CREATE_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query_type":"directed","keywords":["snapshot-meta-partial"],"subreddits":["a","b","c"],"time_window":{"preset":"30d"},"force_refresh":true}' \
    "${API_BASE_URL}/api/v1/query-tasks"
)"

PARTIAL_TASK_ID="$(printf '%s' "${PARTIAL_CREATE_RESPONSE}" | extract_json_field "data.query_task_id")"
assert_nonempty "${PARTIAL_TASK_ID}" "partial task id"
PARTIAL_TASK_RESPONSE="$(poll_query_task_until_terminal "${PARTIAL_TASK_ID}")"
PARTIAL_TASK_STATUS="$(printf '%s' "${PARTIAL_TASK_RESPONSE}" | extract_json_field "data.status")"
PARTIAL_SNAPSHOT_ID="$(printf '%s' "${PARTIAL_TASK_RESPONSE}" | extract_json_field "data.result_snapshot_id")"

assert_eq "partial_success" "${PARTIAL_TASK_STATUS}" "partial task final status"
assert_nonempty "${PARTIAL_SNAPSHOT_ID}" "partial snapshot id"

PARTIAL_SNAPSHOT_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    "${API_BASE_URL}/api/v1/result-snapshots/${PARTIAL_SNAPSHOT_ID}"
)"

PARTIAL_RESPONSE_SOURCE="$(printf '%s' "${PARTIAL_SNAPSHOT_RESPONSE}" | extract_json_field "meta.response_source")"
PARTIAL_WARNING_COUNT="$(printf '%s' "${PARTIAL_SNAPSHOT_RESPONSE}" | extract_json_field "meta.warning_count")"
PARTIAL_PIPELINE_METADATA="$(printf '%s' "${PARTIAL_SNAPSHOT_RESPONSE}" | extract_json_field "meta.pipeline_metadata")"
PARTIAL_PIPELINE_COVERAGE_STATUS="$(printf '%s' "${PARTIAL_SNAPSHOT_RESPONSE}" | extract_json_field "meta.pipeline_metadata.coverage.status")"
PARTIAL_REQUESTED_SOURCE_COUNT="$(printf '%s' "${PARTIAL_SNAPSHOT_RESPONSE}" | extract_json_field "meta.pipeline_metadata.coverage.requested_source_count")"
PARTIAL_COMPLETED_SOURCE_COUNT="$(printf '%s' "${PARTIAL_SNAPSHOT_RESPONSE}" | extract_json_field "meta.pipeline_metadata.coverage.completed_source_count")"
PARTIAL_PIPELINE_CLUSTER_COUNT="$(printf '%s' "${PARTIAL_SNAPSHOT_RESPONSE}" | extract_json_field "meta.pipeline_metadata.result_profile.cluster_count")"
PARTIAL_SUMMARY_CLUSTER_COUNT="$(printf '%s' "${PARTIAL_SNAPSHOT_RESPONSE}" | extract_json_field "data.summary_stats.cluster_count")"

assert_eq "database" "${PARTIAL_RESPONSE_SOURCE}" "partial snapshot response_source"
assert_eq "partial_success" "${PARTIAL_PIPELINE_COVERAGE_STATUS}" "partial snapshot coverage status"
assert_nonempty "${PARTIAL_WARNING_COUNT}" "partial snapshot warning_count"
assert_nonempty "${PARTIAL_PIPELINE_METADATA}" "partial snapshot pipeline_metadata"
assert_eq "${PARTIAL_SUMMARY_CLUSTER_COUNT}" "${PARTIAL_PIPELINE_CLUSTER_COUNT}" "partial snapshot cluster count consistency"

if (( PARTIAL_WARNING_COUNT < 1 )); then
  echo "[verify-result-snapshot-meta] error: partial snapshot warning_count should be >= 1"
  exit 1
fi

if (( PARTIAL_COMPLETED_SOURCE_COUNT >= PARTIAL_REQUESTED_SOURCE_COUNT )); then
  echo "[verify-result-snapshot-meta] error: partial snapshot completed_source_count should be less than requested_source_count"
  echo "[verify-result-snapshot-meta] requested=${PARTIAL_REQUESTED_SOURCE_COUNT} completed=${PARTIAL_COMPLETED_SOURCE_COUNT}"
  exit 1
fi

echo "[verify-result-snapshot-meta] success snapshot response:"
echo "${SUCCESS_SNAPSHOT_RESPONSE}"
echo
echo "[verify-result-snapshot-meta] partial_success snapshot response:"
echo "${PARTIAL_SNAPSHOT_RESPONSE}"
echo
echo "[verify-result-snapshot-meta] all checks passed"
