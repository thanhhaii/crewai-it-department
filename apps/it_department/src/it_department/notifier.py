from __future__ import annotations

import logging
from typing import Iterable

import requests

from .config import AppConfig
from .models import RoleArtifact, RunState

LOGGER = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, config: AppConfig) -> None:
        self.enabled = (
            config.telegram_enabled
            and bool(config.telegram_bot_token)
            and bool(config.telegram_chat_id)
        )
        self.bot_token = config.telegram_bot_token
        self.chat_id = config.telegram_chat_id

    def send_run_update(
        self,
        state: RunState,
        *,
        event: str,
        summary: str,
        artifact: RoleArtifact | None = None,
    ) -> None:
        if not self.enabled:
            return
        lines = [
            f"*IT Department Update*",
            f"Run: `{state.run_id}`",
            f"Event: `{event}`",
            f"Stage: `{state.current_stage}`",
            f"Status: `{state.status}`",
            f"Summary: {summary}",
        ]
        if artifact is not None:
            lines.extend(
                [
                    f"Artifact: `{artifact.role}`",
                    f"Path: `{artifact.path}`",
                ]
            )
        self._send_message("\n".join(lines))

    def send_error(self, state: RunState, error: str) -> None:
        self.send_run_update(state, event="error", summary=error)

    def _send_message(self, text: str) -> None:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        try:
            response = requests.post(
                url,
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                },
                timeout=15,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            LOGGER.warning("Failed to send Telegram update: %s", exc)


def format_status_lines(state: RunState) -> Iterable[str]:
    yield f"Run: {state.run_id}"
    yield f"Status: {state.status}"
    yield f"Stage: {state.current_stage}"
    yield f"Updated at: {state.updated_at}"
    if state.artifacts:
        latest = state.artifacts[-1]
        yield f"Latest artifact: {latest['role']} -> {latest['path']}"
    if state.error:
        yield f"Error: {state.error}"
