from __future__ import annotations

import argparse
import json
import logging
import uuid

from .artifacts import write_json_artifact
from .config import load_config
from .crew_builder import build_crew, persist_role_output
from .frontend_delivery import build_frontend_delivery
from .notifier import TelegramNotifier
from .run_state import RunStateStore
from .sample_data import SAMPLE_REQUEST

LOGGER = logging.getLogger(__name__)


def cli() -> None:
    parser = argparse.ArgumentParser(description="Run the IT Department CrewAI workflow.")
    parser.add_argument("product_request", nargs="?", default=SAMPLE_REQUEST)
    parser.add_argument("--target-module", default="")
    parser.add_argument("--feature-name", default="")
    args = parser.parse_args()
    run(product_request=args.product_request, target_module=args.target_module, feature_name=args.feature_name)


def run(product_request: str, target_module: str = "", feature_name: str = "") -> str:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    config = load_config()
    config.outputs_dir.mkdir(parents=True, exist_ok=True)
    config.run_state_dir.mkdir(parents=True, exist_ok=True)
    config.frontend_generated_dir.mkdir(parents=True, exist_ok=True)

    run_id = uuid.uuid4().hex[:10]
    state_store = RunStateStore(config.run_state_dir)
    notifier = TelegramNotifier(config)
    state = state_store.create(run_id, product_request)
    notifier.send_run_update(state, event="run_started", summary="Execution started.")

    crew = build_crew(config, product_request)
    try:
        result = crew.kickoff(
            inputs={
                "product_request": product_request,
                "target_module": target_module,
                "feature_name": feature_name,
            }
        )
        output_map = _normalize_result(result)

        artifact_specs = [
            ("ba", "BA Artifact", output_map.get("Business Analyst") or output_map.get("ba") or ""),
            ("backend", "Backend Artifact", output_map.get("Backend Architect") or output_map.get("backend") or ""),
            ("frontend-plan", "Frontend Plan", output_map.get("Frontend Lead") or output_map.get("frontend") or ""),
            ("qc", "QC Artifact", output_map.get("Quality Controller") or output_map.get("qc") or ""),
            ("pm", "PM Summary", output_map.get("PM Manager") or output_map.get("pm") or ""),
        ]

        stored = {}
        for role_key, title, content in artifact_specs:
            state = state_store.update(state, current_stage=f"{role_key}_completed", status="in_progress")
            notifier.send_run_update(state, event="stage_started", summary=f"{role_key} artifact persisted.")
            artifact = persist_role_output(config, run_id, role_key, title, content or "_No content generated._")
            stored[role_key] = artifact
            state = state_store.update(state, artifact=artifact)
            notifier.send_run_update(state, event="stage_completed", summary=artifact.summary, artifact=artifact)

        state = state_store.update(state, current_stage="frontend_delivery", status="in_progress")
        notifier.send_run_update(state, event="stage_started", summary="Generating production frontend delivery.")
        frontend_delivery = build_frontend_delivery(
            config.frontend_app_dir,
            product_request=product_request,
            ba_content=stored["ba"].content,
            backend_content=stored["backend"].content,
        )
        state = state_store.update(state, artifact=frontend_delivery)
        notifier.send_run_update(
            state,
            event="stage_completed",
            summary=frontend_delivery.summary,
            artifact=frontend_delivery,
        )

        manifest = {
            "run_id": run_id,
            "product_request": product_request,
            "target_module": target_module,
            "feature_name": feature_name,
            "artifacts": [artifact.to_dict() for artifact in stored.values()] + [frontend_delivery.to_dict()],
        }
        manifest_artifact = write_json_artifact(
            config.outputs_dir,
            run_id,
            "manifest",
            "Run Manifest",
            manifest,
            "Captured the full run manifest.",
        )
        state = state_store.update(state, artifact=manifest_artifact, status="completed", current_stage="completed")
        notifier.send_run_update(state, event="run_completed", summary="Execution completed successfully.")
        LOGGER.info("Run %s completed", run_id)
        return json.dumps(manifest, indent=2)
    except Exception as exc:
        state = state_store.update(state, status="failed", current_stage="failed", error=str(exc))
        notifier.send_error(state, str(exc))
        LOGGER.exception("Run %s failed", run_id)
        raise


def _normalize_result(result: object) -> dict[str, str]:
    if isinstance(result, str):
        return {"pm": result}
    if isinstance(result, dict):
        return {str(key): str(value) for key, value in result.items()}
    text = getattr(result, "raw", None)
    if isinstance(text, str):
        return {"pm": text}
    tasks_output = getattr(result, "tasks_output", None)
    if tasks_output:
        normalized = {}
        for item in tasks_output:
            agent_name = getattr(getattr(item, "agent", None), "role", None) or getattr(item, "name", None) or "task"
            normalized[str(agent_name)] = str(getattr(item, "raw", item))
        return normalized
    return {"pm": str(result)}
