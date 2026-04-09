from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class RoleArtifact:
    role: str
    title: str
    content: str
    summary: str
    path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunState:
    run_id: str
    product_request: str
    status: str
    current_stage: str
    updated_at: str
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

