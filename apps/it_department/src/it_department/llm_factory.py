from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import AppConfig
from .runtime_env import prepare_crewai_runtime


@dataclass(frozen=True)
class RoleModels:
    pm: str
    ba: str
    backend: str
    frontend: str
    qc: str


def get_role_models(config: AppConfig) -> RoleModels:
    return RoleModels(
        pm=config.pm_model,
        ba=config.ba_model,
        backend=config.backend_model,
        frontend=config.frontend_model,
        qc=config.qc_model,
    )


def create_llm(config: AppConfig, model: str) -> Any:
    prepare_crewai_runtime(config.project_root)
    from crewai import LLM

    return LLM(model=f"ollama/{model}", base_url=config.ollama_base_url)
