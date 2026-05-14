#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_DIR="${ROOT_DIR}/.runtime/pids"

stop_if_running() {
  local pid_file="$1"
  if [[ -f "${pid_file}" ]]; then
    local pid
    pid="$(cat "${pid_file}")"
    if kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" >/dev/null 2>&1 || true
    fi
    rm -f "${pid_file}"
  fi
}

stop_if_running "${PID_DIR}/api.pid"
stop_if_running "${PID_DIR}/worker.pid"
stop_if_running "${PID_DIR}/web.pid"

"${ROOT_DIR}/scripts/dev-down.sh" || true

echo "[server-stop] done"
