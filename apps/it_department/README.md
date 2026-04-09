# IT Department App

Python application that orchestrates the IT department workflow.

## Features

- CrewAI agents for PM, BA, Backend, Frontend, QC
- Role-based Ollama model mapping
- Run-state persistence for execution monitoring
- Telegram progress notifications
- Deterministic frontend delivery generator for the Next.js target app

## Run

```bash
cp .env.example .env
python -m it_department.main "Build an internal leave management dashboard"
```
