#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  echo ".env not found at $ROOT_DIR/.env"
  echo "Copy .env.server.example to .env first."
  exit 1
fi

set -a
source "$ROOT_DIR/.env"
set +a

mkdir -p "$ROOT_DIR/logs" "$ROOT_DIR/pids" "$ROOT_DIR/shared/outputs" "$ROOT_DIR/shared/run_state"

if [[ ! -d "$ROOT_DIR/apps/it_department/.venv" ]]; then
  echo "Missing Python virtualenv. Run scripts/bootstrap_ubuntu.sh first."
  exit 1
fi

if [[ ! -d "$ROOT_DIR/apps/frontend/node_modules" && ! -d "$ROOT_DIR/node_modules" ]]; then
  echo "Missing frontend dependencies. Run scripts/bootstrap_ubuntu.sh first."
  exit 1
fi

if [[ "${OLLAMA_AUTOSTART:-false}" == "true" ]]; then
  if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
    nohup env OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0:11434}" ollama serve >"$ROOT_DIR/logs/ollama.log" 2>&1 &
    echo $! >"$ROOT_DIR/pids/ollama.pid"
    sleep 5
  fi
fi

if [[ ! -f "$ROOT_DIR/apps/frontend/.next/BUILD_ID" ]]; then
  pushd "$ROOT_DIR/apps/frontend" >/dev/null
  npm run build >"$ROOT_DIR/logs/frontend-build.log" 2>&1
  popd >/dev/null
fi

if [[ "${START_TELEGRAM_BOT:-false}" == "true" && "${TELEGRAM_ENABLED:-false}" == "true" ]]; then
  if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
    nohup "$ROOT_DIR/apps/it_department/.venv/bin/python" -m it_department.telegram_bot \
      >"$ROOT_DIR/logs/telegram-bot.log" 2>&1 &
    echo $! >"$ROOT_DIR/pids/telegram-bot.pid"
  fi
fi

nohup npm --prefix "$ROOT_DIR/apps/frontend" run start -- --hostname "${FRONTEND_HOST:-0.0.0.0}" --port "${FRONTEND_PORT:-3000}" \
  >"$ROOT_DIR/logs/frontend.log" 2>&1 &
echo $! >"$ROOT_DIR/pids/frontend.pid"

if [[ "${RUN_SAMPLE_ON_BOOT:-false}" == "true" ]]; then
  nohup "$ROOT_DIR/apps/it_department/.venv/bin/python" -m it_department.main "${BOOT_PRODUCT_REQUEST:-Build an internal dashboard}" \
    >"$ROOT_DIR/logs/bootstrap-run.log" 2>&1 &
  echo $! >"$ROOT_DIR/pids/bootstrap-run.pid"
fi

echo "Frontend URL: http://${FRONTEND_HOST:-0.0.0.0}:${FRONTEND_PORT:-3000}"
echo "Logs: $ROOT_DIR/logs"
echo "PIDs: $ROOT_DIR/pids"
