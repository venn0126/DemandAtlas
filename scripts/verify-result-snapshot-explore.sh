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
    echo "[verify-result-snapshot-explore] poll[$attempt] ${query_task_id} -> ${status}" >&2

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
    echo "[verify-result-snapshot-explore] error: ${label}: expected=${expected} actual=${actual}"
    exit 1
  fi
}

assert_nonempty() {
  local actual="$1"
  local label="$2"
  if [[ -z "${actual}" ]]; then
    echo "[verify-result-snapshot-explore] error: ${label} is empty"
    exit 1
  fi
}

echo "[verify-result-snapshot-explore] root: ${ROOT_DIR}"
echo "[verify-result-snapshot-explore] api: ${API_BASE_URL}"

echo "[verify-result-snapshot-explore] case 1: success board and cluster detail"
SUCCESS_CREATE_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query_type":"directed","keywords":["explore-success"],"time_window":{"preset":"30d"},"force_refresh":true}' \
    "${API_BASE_URL}/api/v1/query-tasks"
)"

SUCCESS_TASK_ID="$(printf '%s' "${SUCCESS_CREATE_RESPONSE}" | extract_json_field "data.query_task_id")"
assert_nonempty "${SUCCESS_TASK_ID}" "success task id"
SUCCESS_TASK_RESPONSE="$(poll_query_task_until_terminal "${SUCCESS_TASK_ID}")"
SUCCESS_TASK_STATUS="$(printf '%s' "${SUCCESS_TASK_RESPONSE}" | extract_json_field "data.status")"
SUCCESS_SNAPSHOT_ID="$(printf '%s' "${SUCCESS_TASK_RESPONSE}" | extract_json_field "data.result_snapshot_id")"

assert_eq "success" "${SUCCESS_TASK_STATUS}" "success task final status"
assert_nonempty "${SUCCESS_SNAPSHOT_ID}" "success snapshot id"

SUCCESS_BOARD_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    "${API_BASE_URL}/api/v1/result-snapshots/${SUCCESS_SNAPSHOT_ID}/boards/hot"
)"

SUCCESS_BOARD_SOURCE="$(printf '%s' "${SUCCESS_BOARD_RESPONSE}" | extract_json_field "meta.response_source")"
SUCCESS_BOARD_WARNING_COUNT="$(printf '%s' "${SUCCESS_BOARD_RESPONSE}" | extract_json_field "meta.warning_count")"
SUCCESS_BOARD_CLUSTER_ID="$(printf '%s' "${SUCCESS_BOARD_RESPONSE}" | extract_json_field "data.items.0.cluster_id")"
SUCCESS_BOARD_TYPE="$(printf '%s' "${SUCCESS_BOARD_RESPONSE}" | extract_json_field "data.board_type")"

assert_eq "database" "${SUCCESS_BOARD_SOURCE}" "success board response_source"
assert_eq "hot" "${SUCCESS_BOARD_TYPE}" "success board board_type"
assert_eq "0" "${SUCCESS_BOARD_WARNING_COUNT}" "success board warning_count"
assert_nonempty "${SUCCESS_BOARD_CLUSTER_ID}" "success board cluster_id"

SUCCESS_CLUSTER_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    "${API_BASE_URL}/api/v1/result-snapshots/${SUCCESS_SNAPSHOT_ID}/clusters/${SUCCESS_BOARD_CLUSTER_ID}"
)"

SUCCESS_CLUSTER_SOURCE="$(printf '%s' "${SUCCESS_CLUSTER_RESPONSE}" | extract_json_field "meta.response_source")"
SUCCESS_CLUSTER_ID="$(printf '%s' "${SUCCESS_CLUSTER_RESPONSE}" | extract_json_field "data.cluster_id")"
SUCCESS_CLUSTER_TITLE="$(printf '%s' "${SUCCESS_CLUSTER_RESPONSE}" | extract_json_field "data.title")"
SUCCESS_CLUSTER_EVIDENCE_COUNT="$(printf '%s' "${SUCCESS_CLUSTER_RESPONSE}" | extract_json_field "data.supporting_evidence.0.evidence_id")"

assert_eq "database" "${SUCCESS_CLUSTER_SOURCE}" "success cluster response_source"
assert_eq "${SUCCESS_BOARD_CLUSTER_ID}" "${SUCCESS_CLUSTER_ID}" "success cluster id consistency"
assert_nonempty "${SUCCESS_CLUSTER_TITLE}" "success cluster title"
assert_nonempty "${SUCCESS_CLUSTER_EVIDENCE_COUNT}" "success cluster supporting evidence"

echo "[verify-result-snapshot-explore] case 2: partial_success board and cluster detail"
PARTIAL_CREATE_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query_type":"directed","keywords":["explore-partial"],"subreddits":["a","b","c"],"time_window":{"preset":"30d"},"force_refresh":true}' \
    "${API_BASE_URL}/api/v1/query-tasks"
)"

PARTIAL_TASK_ID="$(printf '%s' "${PARTIAL_CREATE_RESPONSE}" | extract_json_field "data.query_task_id")"
assert_nonempty "${PARTIAL_TASK_ID}" "partial task id"
PARTIAL_TASK_RESPONSE="$(poll_query_task_until_terminal "${PARTIAL_TASK_ID}")"
PARTIAL_TASK_STATUS="$(printf '%s' "${PARTIAL_TASK_RESPONSE}" | extract_json_field "data.status")"
PARTIAL_SNAPSHOT_ID="$(printf '%s' "${PARTIAL_TASK_RESPONSE}" | extract_json_field "data.result_snapshot_id")"

assert_eq "partial_success" "${PARTIAL_TASK_STATUS}" "partial task final status"
assert_nonempty "${PARTIAL_SNAPSHOT_ID}" "partial snapshot id"

PARTIAL_BOARD_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    "${API_BASE_URL}/api/v1/result-snapshots/${PARTIAL_SNAPSHOT_ID}/boards/hot"
)"

PARTIAL_BOARD_SOURCE="$(printf '%s' "${PARTIAL_BOARD_RESPONSE}" | extract_json_field "meta.response_source")"
PARTIAL_BOARD_WARNING_COUNT="$(printf '%s' "${PARTIAL_BOARD_RESPONSE}" | extract_json_field "meta.warning_count")"
PARTIAL_BOARD_CLUSTER_ID="$(printf '%s' "${PARTIAL_BOARD_RESPONSE}" | extract_json_field "data.items.0.cluster_id")"

assert_eq "database" "${PARTIAL_BOARD_SOURCE}" "partial board response_source"
assert_nonempty "${PARTIAL_BOARD_WARNING_COUNT}" "partial board warning_count"
assert_nonempty "${PARTIAL_BOARD_CLUSTER_ID}" "partial board cluster_id"

if (( PARTIAL_BOARD_WARNING_COUNT < 1 )); then
  echo "[verify-result-snapshot-explore] error: partial board warning_count should be >= 1"
  exit 1
fi

PARTIAL_CLUSTER_RESPONSE="$(
  curl \
    --fail \
    --silent \
    --show-error \
    "${API_BASE_URL}/api/v1/result-snapshots/${PARTIAL_SNAPSHOT_ID}/clusters/${PARTIAL_BOARD_CLUSTER_ID}"
)"

PARTIAL_CLUSTER_SOURCE="$(printf '%s' "${PARTIAL_CLUSTER_RESPONSE}" | extract_json_field "meta.response_source")"
PARTIAL_CLUSTER_ID="$(printf '%s' "${PARTIAL_CLUSTER_RESPONSE}" | extract_json_field "data.cluster_id")"
PARTIAL_CLUSTER_COVERAGE_NOTE="$(printf '%s' "${PARTIAL_CLUSTER_RESPONSE}" | extract_json_field "data.coverage_note")"
PARTIAL_CLUSTER_SUBREDDIT="$(printf '%s' "${PARTIAL_CLUSTER_RESPONSE}" | extract_json_field "data.top_subreddits.0")"

assert_eq "database" "${PARTIAL_CLUSTER_SOURCE}" "partial cluster response_source"
assert_eq "${PARTIAL_BOARD_CLUSTER_ID}" "${PARTIAL_CLUSTER_ID}" "partial cluster id consistency"
assert_nonempty "${PARTIAL_CLUSTER_COVERAGE_NOTE}" "partial cluster coverage_note"
assert_nonempty "${PARTIAL_CLUSTER_SUBREDDIT}" "partial cluster top_subreddits"

echo "[verify-result-snapshot-explore] success board response:"
echo "${SUCCESS_BOARD_RESPONSE}"
echo
echo "[verify-result-snapshot-explore] success cluster response:"
echo "${SUCCESS_CLUSTER_RESPONSE}"
echo
echo "[verify-result-snapshot-explore] partial board response:"
echo "${PARTIAL_BOARD_RESPONSE}"
echo
echo "[verify-result-snapshot-explore] partial cluster response:"
echo "${PARTIAL_CLUSTER_RESPONSE}"
echo
echo "[verify-result-snapshot-explore] all checks passed"
