from __future__ import annotations

import os
from pathlib import Path


def prepare_crewai_runtime(project_root: Path) -> None:
    runtime_home = project_root / ".runtime-home"
    runtime_home.mkdir(parents=True, exist_ok=True)
    os.environ["HOME"] = str(runtime_home)
    os.environ.setdefault("CREWAI_STORAGE_DIR", "it_department")
    os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
    os.environ.setdefault("CREWAI_DISABLE_TRACKING", "true")
