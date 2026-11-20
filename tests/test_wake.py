"""Unit — wake-word service (manual + detector injectável)."""

from __future__ import annotations

from ric.voice.wake import WakeWordService


class FakeDetector:
    available = True

    def __init__(self) -> None:
        self.paused = False
        self.model_label = "hey_jarvis"
        self._on = None

    def start(self, on_detect) -> None:
        self._on = on_detect

    def stop(self) -> None:
        return None

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        self.paused = False


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
    wake = WakeWordService(on_detect=lambda: None, detector=FakeDetector())
    assert wake.available is True
    status = wake.status()
    assert status["mode"] == "openwakeword"
    assert status["phrase"] == "hey jarvis"
    assert status["model"] == "hey_jarvis"


def test_on_state_pauses_outside_idle() -> None:
    det = FakeDetector()
    wake = WakeWordService(on_detect=lambda: None, detector=det)
    wake.start()
    wake.on_state("listening")
    assert det.paused is True
    wake.on_state("idle")
    assert det.paused is False


def test_detector_fire_reaches_session_listening() -> None:
    from ric.core.events import EventBus
    from ric.voice.session import VoiceSession
    from ric.voice.stt import SpeechToText

    events = EventBus()
    seen: list[dict] = []
    events.subscribe(seen.append)
    session = VoiceSession(
        events=events,
        stt=SpeechToText(backend=lambda _p: ""),
    )
    det = FakeDetector()
    wake = WakeWordService(on_detect=session.on_wake, detector=det)
    wake.start()
    assert det._on is not None
    det._on()
    assert events.state == "listening"
    assert any(e.get("type") == "wake_detected" for e in seen)
