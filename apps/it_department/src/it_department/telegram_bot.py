from __future__ import annotations

import logging
import time

import requests

from .config import load_config
from .notifier import format_status_lines
from .run_state import RunStateStore

LOGGER = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    config = load_config()
    if not config.telegram_bot_token or not config.telegram_chat_id:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")

    state_store = RunStateStore(config.run_state_dir)
    offset = 0
    while True:
        offset = poll_once(config.telegram_bot_token, config.telegram_chat_id, state_store, offset)
        time.sleep(2)


def poll_once(token: str, default_chat_id: str, state_store: RunStateStore, offset: int) -> int:
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    response = requests.get(url, params={"timeout": 20, "offset": offset}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        return offset
    for update in payload.get("result", []):
        offset = update["update_id"] + 1
        message = update.get("message", {})
        text = (message.get("text") or "").strip()
        chat_id = str(message.get("chat", {}).get("id") or default_chat_id)
        if text in {"/status", "/latest"}:
            latest = state_store.latest()
            reply = "No runs yet." if latest is None else "\n".join(format_status_lines(latest))
            send_reply(token, chat_id, reply)
    return offset


def send_reply(token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=15).raise_for_status()
