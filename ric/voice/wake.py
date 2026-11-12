"""Wake-word: botão manual sempre; openWakeWord opcional quando houver modelo «RIC»."""

from __future__ import annotations

from typing import Callable, Protocol


class WakeDetector(Protocol):
    available: bool

    def start(self, on_detect: Callable[[], None]) -> None: ...

    def stop(self) -> None: ...


class WakeWordService:
    """Dispara `on_detect` no wake (modelo) ou no botão «Falar»."""

    def __init__(
        self,
        *,
        on_detect: Callable[[], None],
        detector: WakeDetector | None = None,
    ) -> None:
        self._on_detect = on_detect
        self._detector = detector
        self._listening = False

    @property
    def available(self) -> bool:
        return bool(self._detector and self._detector.available)

    def start(self) -> None:
        if self._listening:
            return
        self._listening = True
        if self._detector and self._detector.available:
            self._detector.start(self._safe_detect)

    def stop(self) -> None:
        if not self._listening:
            return
        self._listening = False
        if self._detector and self._detector.available:
            self._detector.stop()

    def trigger_manual(self) -> None:
        """Fallback táctil — sempre activo (botão Falar)."""
        self._fire()

    def _safe_detect(self) -> None:
        """Callback do detector contínuo — só enquanto start() estiver activo."""
        if not self._listening:
            return
        self._fire()

    def _fire(self) -> None:
        try:
            self._on_detect()
        except Exception as exc:  # noqa: BLE001
            print(f"[RIC] erro no callback wake: {exc}", flush=True)

    def status(self) -> dict:
        mode = "openwakeword" if self.available else "manual"
        return {
            "available": self.available,
            "mode": mode,
            "listening": self._listening,
            "word": "RIC",
        }
