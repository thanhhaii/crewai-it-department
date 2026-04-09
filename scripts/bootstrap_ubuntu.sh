#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  if [[ -f "$ROOT_DIR/.env.server.example" ]]; then
    cp "$ROOT_DIR/.env.server.example" "$ROOT_DIR/.env"
    echo "Created .env from .env.server.example. Review it before the next run."
  else
    echo ".env not found at $ROOT_DIR/.env"
    exit 1
  fi
fi

set -a
source "$ROOT_DIR/.env"
set +a

mkdir -p "$ROOT_DIR/logs" "$ROOT_DIR/pids" "$ROOT_DIR/shared/outputs" "$ROOT_DIR/shared/run_state"

sudo apt-get update
sudo apt-get install -y curl git build-essential python3 python3-venv python3-pip ca-certificates

if ! command -v node >/dev/null 2>&1; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi

pushd "$ROOT_DIR/apps/it_department" >/dev/null
if [[ ! -d .venv ]]; then
  uv venv
fi
./.venv/bin/python -m pip install --upgrade pip >/dev/null
uv pip install --python .venv/bin/python -e '.[dev]'
popd >/dev/null

pushd "$ROOT_DIR/apps/frontend" >/dev/null
npm install
popd >/dev/null

if [[ "${OLLAMA_AUTOSTART:-false}" == "true" ]]; then
  if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
    nohup env OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0:11434}" ollama serve >"$ROOT_DIR/logs/ollama.log" 2>&1 &
    echo $! >"$ROOT_DIR/pids/ollama.pid"
    sleep 5
  fi
fi

if [[ "${OLLAMA_PULL_MODELS:-false}" == "true" ]]; then
  declare -a models=(
    "${PM_MODEL:-}"
    "${BA_MODEL:-}"
    "${BACKEND_MODEL:-}"
    "${FRONTEND_MODEL:-}"
    "${QC_MODEL:-}"
  )

  declare -A seen=()
  for model in "${models[@]}"; do
    if [[ -n "$model" && -z "${seen[$model]:-}" ]]; then
      seen[$model]=1
      ollama pull "$model"
    fi
  done
fi

echo "Bootstrap completed."
