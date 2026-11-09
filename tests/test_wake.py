"""Unit — wake-word service (manual + detector injectável)."""

from __future__ import annotations

from ric.voice.wake import WakeWordService


def test_manual_trigger_calls_on_detect() -> None:
    hits: list[str] = []
    wake = WakeWordService(on_detect=lambda: hits.append("ric"))
    wake.trigger_manual()
    assert hits == ["ric"]


def test_start_stop_with_unavailable_detector() -> None:
    wake = WakeWordService(on_detect=lambda: None)
    assert wake.available is False
    wake.start()
    wake.stop()
    status = wake.status()
    assert status["mode"] == "manual"
    assert status["listening"] is False


def test_detector_callback_ignored_after_stop() -> None:
    hits: list[str] = []

    class FakeDetector:
        available = True

        def start(self, on_detect) -> None:
            self._on = on_detect

        def stop(self) -> None:
            return None

    det = FakeDetector()
    wake = WakeWordService(on_detect=lambda: hits.append("x"), detector=det)
    wake.start()
    wake.stop()
    det._on()  # simula late callback do openWakeWord
    assert hits == []
    wake.trigger_manual()  # botão continua a funcionar
    assert hits == ["x"]


def test_on_detect_exception_is_swallowed() -> None:
    def boom() -> None:
        raise RuntimeError("falhou")

    wake = WakeWordService(on_detect=boom)
    wake.start()
    wake.trigger_manual()  # não propaga


def test_injected_detector_marks_available() -> None:
    class FakeDetector:
        available = True

        def start(self, on_detect) -> None:
            self._on = on_detect

        def stop(self) -> None:
            return None

    wake = WakeWordService(on_detect=lambda: None, detector=FakeDetector())
    assert wake.available is True
    assert wake.status()["mode"] == "openwakeword"
