from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .models import RoleArtifact, RunState


class RunStateStore:
    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def write(self, state: RunState) -> Path:
        target = self.state_dir / f"{state.run_id}.json"
        target.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")
        latest = self.state_dir / "latest.json"
        latest.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")
        return target

    def create(self, run_id: str, product_request: str) -> RunState:
        state = RunState(
            run_id=run_id,
            product_request=product_request,
            status="started",
            current_stage="pm_initialization",
            updated_at=_now(),
        )
        self.write(state)
        return state

    def update(
        self,
        state: RunState,
        *,
        status: str | None = None,
        current_stage: str | None = None,
        artifact: RoleArtifact | None = None,
        error: str | None = None,
    ) -> RunState:
        if status is not None:
            state.status = status
        if current_stage is not None:
            state.current_stage = current_stage
        if artifact is not None:
            state.artifacts.append(artifact.to_dict())
        if error is not None:
            state.error = error
        state.updated_at = _now()
        self.write(state)
        return state

    def latest(self) -> RunState | None:
        latest = self.state_dir / "latest.json"
        if not latest.exists():
            return None
        payload = json.loads(latest.read_text(encoding="utf-8"))
        return RunState(**payload)


def _now() -> str:
    return datetime.now(UTC).isoformat()
