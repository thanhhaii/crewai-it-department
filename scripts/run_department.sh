#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  echo ".env not found at $ROOT_DIR/.env"
  echo "Copy .env.server.example to .env first."
  exit 1
fi

if [[ $# -eq 0 ]]; then
  echo "Usage: scripts/run_department.sh \"Your product request\""
  exit 1
fi

set -a
source "$ROOT_DIR/.env"
set +a

"$ROOT_DIR/apps/it_department/.venv/bin/python" -m it_department.main "$*"
