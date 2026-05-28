#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
WEB_BASE_URL="${WEB_BASE_URL:-http://127.0.0.1:4173}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
WEB_BASE_URL="${WEB_BASE_URL:-http://127.0.0.1:4173}"

echo "[verify-api-contract] root: ${ROOT_DIR}"
echo "[verify-api-contract] api: ${API_BASE_URL}"
echo "[verify-api-contract] web: ${WEB_BASE_URL}"

echo "[verify-api-contract] step 1/5: smoke test"
bash "${ROOT_DIR}/scripts/smoke-test.sh"

echo "[verify-api-contract] step 2/5: query task metadata"
bash "${ROOT_DIR}/scripts/verify-query-task-meta.sh"

echo "[verify-api-contract] step 3/5: result snapshot metadata"
bash "${ROOT_DIR}/scripts/verify-result-snapshot-meta.sh"

echo "[verify-api-contract] step 4/5: result snapshot explore"
bash "${ROOT_DIR}/scripts/verify-result-snapshot-explore.sh"

echo "[verify-api-contract] step 5/5: result consistency"
bash "${ROOT_DIR}/scripts/verify-result-consistency.sh"

echo "[verify-api-contract] all checks passed"
