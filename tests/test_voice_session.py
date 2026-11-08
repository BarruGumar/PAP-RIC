"""Unit — sessão de voz wake → listening → STT → transcript."""

from __future__ import annotations

from ric.core.events import EventBus
from ric.voice.session import VoiceSession
from ric.voice.stt import SpeechToText
from ric.voice.wake import WakeWordService


def test_wake_sets_listening_and_publishes() -> None:
    events = EventBus()
    published: list[dict] = []
    events.subscribe(published.append)

    session = VoiceSession(
        events=events,
        stt=SpeechToText(backend=lambda _p: "água"),
    )
    wake = WakeWordService(on_detect=session.on_wake)
    wake.trigger_manual()

    assert events.state == "listening"
    assert any(e.get("type") == "wake_detected" for e in published)


def test_process_audio_publishes_transcript_and_returns_idle() -> None:
    events = EventBus()
    published: list[dict] = []
    events.subscribe(published.append)
    session = VoiceSession(
        events=events,
        stt=SpeechToText(backend=lambda _p: "beber água"),
    )
    session.on_wake()
    text = session.process_audio(b"RIFF-fake", content_type="audio/wav")

    assert text == "beber água"
    assert events.state == "idle"
    assert any(
        e.get("type") == "transcript" and e.get("text") == "beber água"
        for e in published
    )


def test_cancel_listen_returns_idle() -> None:
    events = EventBus()
    session = VoiceSession(
        events=events,
        stt=SpeechToText(backend=lambda _p: "x"),
    )
    session.on_wake()
    session.cancel()
    assert events.state == "idle"


def test_process_audio_does_not_clobber_alert_state() -> None:
    events = EventBus()

    def backend(_path) -> str:
        events.set_state("alert")
        return "x"

    session = VoiceSession(
        events=events,
        stt=SpeechToText(backend=backend),
    )
    session.on_wake()
    text = session.process_audio(b"fake")
    assert text == "x"
    assert events.state == "alert"


def test_invalid_base64_returns_idle() -> None:
    import pytest

    events = EventBus()
    session = VoiceSession(
        events=events,
        stt=SpeechToText(backend=lambda _p: "x"),
    )
    session.on_wake()
    with pytest.raises(ValueError):
        session.process_base64("!!!not-base64!!!")
    assert events.state == "idle"
