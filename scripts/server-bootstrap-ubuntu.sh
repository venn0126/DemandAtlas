#!/usr/bin/env bash
set -euo pipefail

echo "[server-bootstrap] installing base dependencies on Ubuntu"

sudo apt-get update
sudo apt-get install -y curl ca-certificates git gnupg lsb-release

if ! command -v docker >/dev/null 2>&1; then
  echo "[server-bootstrap] installing docker"
  curl -fsSL https://get.docker.com | sudo sh
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "[server-bootstrap] installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v node >/dev/null 2>&1; then
  echo "[server-bootstrap] installing nodejs"
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

if ! command -v pnpm >/dev/null 2>&1; then
  echo "[server-bootstrap] installing pnpm"
  sudo npm install -g pnpm
fi

echo "[server-bootstrap] done"
echo "[server-bootstrap] you can now run ./scripts/bootstrap.sh"

