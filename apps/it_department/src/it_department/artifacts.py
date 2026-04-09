from __future__ import annotations

import json
import re
from pathlib import Path

from .models import RoleArtifact


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "project"


def write_markdown_artifact(
    outputs_dir: Path,
    run_id: str,
    role: str,
    title: str,
    content: str,
    summary: str,
) -> RoleArtifact:
    target_dir = outputs_dir / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{role.lower()}.md"
    target = target_dir / filename
    target.write_text(content, encoding="utf-8")
    return RoleArtifact(role=role, title=title, content=content, summary=summary, path=str(target))


def write_json_artifact(
    outputs_dir: Path,
    run_id: str,
    role: str,
    title: str,
    payload: dict,
    summary: str,
) -> RoleArtifact:
    target_dir = outputs_dir / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{role.lower()}.json"
    target = target_dir / filename
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return RoleArtifact(
        role=role,
        title=title,
        content=json.dumps(payload, indent=2),
        summary=summary,
        path=str(target),
    )
