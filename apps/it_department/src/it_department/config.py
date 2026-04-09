from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional until dependencies are installed
    def load_dotenv() -> bool:
        return False


def _find_project_root() -> Path:
    env_root = os.getenv("PROJECT_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[4]


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    project_root: Path
    ollama_base_url: str
    default_model: str
    pm_model: str
    ba_model: str
    backend_model: str
    frontend_model: str
    qc_model: str
    telegram_enabled: bool
    telegram_bot_token: str
    telegram_chat_id: str

    @property
    def outputs_dir(self) -> Path:
        return self.project_root / "shared" / "outputs"

    @property
    def run_state_dir(self) -> Path:
        return self.project_root / "shared" / "run_state"

    @property
    def frontend_app_dir(self) -> Path:
        return self.project_root / "apps" / "frontend"

    @property
    def frontend_generated_dir(self) -> Path:
        return self.frontend_app_dir / "app" / "generated"


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> AppConfig:
    project_root = _find_project_root()
    default_model = os.getenv("DEFAULT_MODEL", "qwen3:14b")
    return AppConfig(
        project_root=project_root,
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        default_model=default_model,
        pm_model=os.getenv("PM_MODEL", default_model),
        ba_model=os.getenv("BA_MODEL", default_model),
        backend_model=os.getenv("BACKEND_MODEL", default_model),
        frontend_model=os.getenv("FRONTEND_MODEL", default_model),
        qc_model=os.getenv("QC_MODEL", default_model),
        telegram_enabled=_env_bool("TELEGRAM_ENABLED", default=False),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
    )
