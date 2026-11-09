from __future__ import annotations

import json
import threading
from collections.abc import Callable
from typing import Any


class EventBus:
    """Pub/sub in-process para WebSocket e outros ouvintes."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subscribers: list[Callable[[dict[str, Any]], None]] = []
        self._state = "idle"

    @property
    def state(self) -> str:
        return self._state

    def set_state(self, state: str) -> None:
        self._state = state
        self.publish({"type": "state", "state": state})

    def subscribe(self, callback: Callable[[dict[str, Any]], None]) -> Callable[[], None]:
        with self._lock:
            self._subscribers.append(callback)

        def unsubscribe() -> None:
            with self._lock:
                if callback in self._subscribers:
                    self._subscribers.remove(callback)

        return unsubscribe

    def publish(self, event: dict[str, Any]) -> None:
        with self._lock:
            subs = list(self._subscribers)
        for cb in subs:
            try:
                cb(event)
            except Exception:  # noqa: BLE001
                pass

    @staticmethod
    def encode(event: dict[str, Any]) -> str:
        return json.dumps(event, ensure_ascii=False)
