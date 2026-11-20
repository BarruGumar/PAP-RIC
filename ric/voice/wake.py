"""Wake-word: botão manual sempre; openWakeWord opcional quando o detector estiver disponível."""

from __future__ import annotations

from typing import Any, Callable, Protocol


class WakeDetector(Protocol):
    available: bool

    def start(self, on_detect: Callable[[], None]) -> None: ...

    def stop(self) -> None: ...

    def pause(self) -> None: ...

    def resume(self) -> None: ...


class WakeWordService:
    """Dispara `on_detect` no wake (modelo) ou no botão «Falar»."""

    _PAUSE_STATES = frozenset({"listening", "thinking", "speaking", "alert"})

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

    def pause(self) -> None:
        if self._detector and self._detector.available:
            self._detector.pause()

    def resume(self) -> None:
        if not self._listening:
            return
        if self._detector and self._detector.available:
            self._detector.resume()

    def on_state(self, state: str) -> None:
        """Pausa o microfone contínuo fora de idle (evita eco do TTS / auto-wake)."""
        if state in self._PAUSE_STATES:
            self.pause()
            return
        if state == "idle":
            self.resume()

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

    def status(self) -> dict[str, Any]:
        mode = "openwakeword" if self.available else "manual"
        model_label = None
        paused = False
        # Alvo do produto; temporários (hey_jarvis) mostram o nome real do modelo.
        phrase = "ei RIC"
        if self._detector is not None:
            model_label = getattr(self._detector, "model_label", None)
            paused = bool(getattr(self._detector, "paused", False))
            label = str(model_label or "").casefold().replace("-", "_")
            if label and label not in ("ric", "ei_ric", "ei ric"):
                phrase = str(model_label).replace("_", " ")
        return {
            "available": self.available,
            "mode": mode,
            "listening": self._listening,
            "paused": paused,
            "word": "ei RIC",
            "phrase": phrase,
            "model": model_label,
        }
