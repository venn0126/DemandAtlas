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
      curl --fail --silent --show-error \
        "${API_BASE_URL}/api/v1/query-tasks/${query_task_id}"
    )"
    status="$(printf '%s' "${response}" | extract_json_field "data.status")"
    if [[ "${status}" == "success" || "${status}" == "partial_success" || "${status}" == "failed" ]]; then
      printf '%s' "${response}"
      return 0
    fi
    sleep "${POLL_INTERVAL_SECONDS}"
  done

  printf '%s' "${response}"
  return 1
}

echo "[verify-result-consistency] root: ${ROOT_DIR}"
echo "[verify-result-consistency] api: ${API_BASE_URL}"

CREATE_RESPONSE="$(
  curl --fail --silent --show-error \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"query_type":"directed","keywords":["consistency-check","workflow"],"subreddits":["productivity","ChatGPT"],"time_window":{"preset":"30d"},"force_refresh":true}' \
    "${API_BASE_URL}/api/v1/query-tasks"
)"

QUERY_TASK_ID="$(printf '%s' "${CREATE_RESPONSE}" | extract_json_field "data.query_task_id")"
TASK_RESPONSE="$(poll_query_task_until_terminal "${QUERY_TASK_ID}")"
TASK_STATUS="$(printf '%s' "${TASK_RESPONSE}" | extract_json_field "data.status")"
RESULT_SNAPSHOT_ID="$(printf '%s' "${TASK_RESPONSE}" | extract_json_field "data.result_snapshot_id")"

if [[ "${TASK_STATUS}" != "success" && "${TASK_STATUS}" != "partial_success" ]]; then
  echo "[verify-result-consistency] error: task did not finish successfully"
  echo "${TASK_RESPONSE}"
  exit 1
fi

SUMMARY_RESPONSE="$(
  curl --fail --silent --show-error \
    "${API_BASE_URL}/api/v1/result-snapshots/${RESULT_SNAPSHOT_ID}"
)"
BOARD_RESPONSE="$(
  curl --fail --silent --show-error \
    "${API_BASE_URL}/api/v1/result-snapshots/${RESULT_SNAPSHOT_ID}/boards/hot"
)"
CLUSTER_ID="$(printf '%s' "${BOARD_RESPONSE}" | extract_json_field "data.items.0.cluster_id")"
DETAIL_RESPONSE="$(
  curl --fail --silent --show-error \
    "${API_BASE_URL}/api/v1/result-snapshots/${RESULT_SNAPSHOT_ID}/clusters/${CLUSTER_ID}"
)"

SUMMARY_CLUSTER_COUNT="$(printf '%s' "${SUMMARY_RESPONSE}" | extract_json_field "data.summary_stats.cluster_count")"
BOARD_ITEMS_COUNT="$(printf '%s' "${BOARD_RESPONSE}" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["data"]["items"]))')"
DETAIL_CLUSTER_ID="$(printf '%s' "${DETAIL_RESPONSE}" | extract_json_field "data.cluster_id")"
DETAIL_POST_COUNT="$(printf '%s' "${DETAIL_RESPONSE}" | extract_json_field "data.metrics.post_count")"
BOARD_POST_COUNT="$(printf '%s' "${BOARD_RESPONSE}" | extract_json_field "data.items.0.post_count")"

if [[ -z "${SUMMARY_CLUSTER_COUNT}" || "${SUMMARY_CLUSTER_COUNT}" == "0" ]]; then
  echo "[verify-result-consistency] error: summary cluster_count invalid"
  echo "${SUMMARY_RESPONSE}"
  exit 1
fi

if [[ "${BOARD_ITEMS_COUNT}" == "0" ]]; then
  echo "[verify-result-consistency] error: board returned no items"
  echo "${BOARD_RESPONSE}"
  exit 1
fi

if [[ "${CLUSTER_ID}" != "${DETAIL_CLUSTER_ID}" ]]; then
  echo "[verify-result-consistency] error: board/detail cluster id mismatch"
  echo "${BOARD_RESPONSE}"
  echo "${DETAIL_RESPONSE}"
  exit 1
fi

if [[ "${BOARD_POST_COUNT}" != "${DETAIL_POST_COUNT}" ]]; then
  echo "[verify-result-consistency] error: board/detail post_count mismatch"
  echo "${BOARD_RESPONSE}"
  echo "${DETAIL_RESPONSE}"
  exit 1
fi

echo "[verify-result-consistency] summary:"
echo "${SUMMARY_RESPONSE}"
echo
echo "[verify-result-consistency] board:"
echo "${BOARD_RESPONSE}"
echo
echo "[verify-result-consistency] detail:"
echo "${DETAIL_RESPONSE}"
echo
echo "[verify-result-consistency] all checks passed"
