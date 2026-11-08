"""Unit — TTS service usa backends injectados (sem áudio real)."""

from __future__ import annotations

from ric.voice.tts import VoiceService, format_alert_phrase, prepare_speech_text


def test_prepare_speech_text_clears_symbols() -> None:
    assert prepare_speech_text("Lembrete: beber água") == "Lembrete, beber água."
    assert prepare_speech_text("  oi  ") == "oi."
    assert prepare_speech_text("a,, b") == "a, b."


def test_prepare_speech_text_says_ric_not_letters() -> None:
    assert prepare_speech_text("Olá, eu sou o RIC") == "Olá, eu sou o Ric."
    assert prepare_speech_text("R.I.C. está aqui") == "Ric está aqui."
    assert prepare_speech_text("o RIC") == "o Ric."



def test_alert_phrase_avoids_mid_sentence_stop() -> None:
    phrase = format_alert_phrase("Beber água")
    assert phrase == "Atenção, é a hora de Beber água."
    assert "Atenção." not in phrase



def test_speak_uses_first_successful_backend() -> None:
    calls: list[str] = []

    def fail(_texto: str) -> bool:
        calls.append("fail")
        return False

    def ok(texto: str) -> bool:
        calls.append(texto)
        return True

    speaking: list[bool] = []
    voice = VoiceService(
        backends=[fail, ok],
        on_speaking=lambda flag: speaking.append(flag),
    )
    assert voice.speak("Olá RIC", async_=False, with_beep=False) is True
    assert calls == ["fail", "Olá Ric."]
    assert speaking == [True, False]


def test_speak_empty_is_noop() -> None:
    voice = VoiceService(backends=[lambda _t: True])
    assert voice.speak("  ", async_=False) is False


def test_status_keys() -> None:
    voice = VoiceService(backends=[])
    status = voice.status()
    assert "piper" in status
    assert "engine" in status
    assert "wake" not in status
    assert "stt" not in status
