# CrewAI IT Department

Monorepo scaffold for an IT department powered by CrewAI with five roles:

- PM
- BA
- Backend
- Frontend
- QC

The workspace contains:

- `apps/it_department`: Python orchestration app for CrewAI, Ollama model mapping, artifact generation, run-state tracking, and Telegram progress notifications
- `apps/frontend`: Next.js + TypeScript production target updated by the frontend delivery stage
- `shared/outputs`: generated artifacts
- `shared/run_state`: execution state used by the Telegram notifier

## Quick start

### 1. Python app

```bash
cd apps/it_department
uv venv
source .venv/bin/activate
uv pip install -e .
cp .env.example .env
python -m it_department.main "Build an internal leave dashboard"
```

### 2. Frontend app

```bash
cd apps/frontend
npm install
npm run dev
```

### 3. Ollama models

Set at least:

- `OLLAMA_BASE_URL`
- `DEFAULT_MODEL`

Recommended role mapping:

- `PM_MODEL=qwen3:14b`
- `BA_MODEL=qwen3:14b`
- `BACKEND_MODEL=qwen2.5-coder:14b`
- `FRONTEND_MODEL=qwen2.5-coder:14b`
- `QC_MODEL=qwen3:8b`

## Telegram progress updates

Enable Telegram push updates by setting:

- `TELEGRAM_ENABLED=true`
- `TELEGRAM_BOT_TOKEN=...`
- `TELEGRAM_CHAT_ID=...`

The Python app pushes updates when a run starts, each role begins/completes, the frontend delivery is generated, and the run completes or fails.

Optional polling mode is available through:

```bash
python -m it_department.telegram_bot
```

This supports lightweight `/status` and `/latest` commands.

## Ubuntu server scripts

Root-level scripts are included so you can bring up the stack on an Ubuntu GPU server with minimal setup.

### 1. Edit server env

Copy [`.env.server.example`](/Users/hai.lam/Documents/Learning/crewai/.env.server.example) to `.env`, then update:

- `PROJECT_ROOT`
- `OLLAMA_BASE_URL`
- Telegram fields if needed
- model names if you prefer different Ollama models

For a `48 GB VRAM` server, the default role mapping in `.env` is a safe starting point.

### 2. Bootstrap once

```bash
cd /Users/ubuntu/crewai-it-department
chmod +x scripts/*.sh
./scripts/bootstrap_ubuntu.sh
```

This script:

- installs system packages
- installs `uv`, `node`, and `ollama` if needed
- creates the Python virtualenv
- installs Python and frontend dependencies
- optionally starts Ollama and pulls the configured models

### 3. Start the stack

```bash
./scripts/start_server.sh
```

This starts:

- `ollama serve` if `OLLAMA_AUTOSTART=true`
- `Next.js` in production mode
- Telegram polling bot if both `START_TELEGRAM_BOT=true` and `TELEGRAM_ENABLED=true`

### 4. Run a department request

```bash
./scripts/run_department.sh "Build an internal leave dashboard"
```

### 5. Stop background services

```bash
./scripts/stop_server.sh
```
