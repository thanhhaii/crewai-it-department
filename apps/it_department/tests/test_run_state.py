from pathlib import Path

from it_department.models import RoleArtifact
from it_department.run_state import RunStateStore


def test_run_state_latest(tmp_path: Path):
    store = RunStateStore(tmp_path)
    state = store.create("abc123", "Build dashboard")
    artifact = RoleArtifact(
        role="BA",
        title="BA Artifact",
        content="content",
        summary="summary",
        path="/tmp/ba.md",
    )
    store.update(state, artifact=artifact, status="in_progress", current_stage="ba_completed")
    latest = store.latest()
    assert latest is not None
    assert latest.current_stage == "ba_completed"
    assert latest.artifacts[0]["role"] == "BA"
