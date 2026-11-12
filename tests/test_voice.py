"""Unit — TTS service usa backends injectados (sem áudio real)."""

from __future__ import annotations

import pytest

from ric.voice.tts import (
    VoiceService,
    format_alert_phrase,
    length_scale_for_stem,
    prepare_speech_text,
)


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
    assert "chatterbox" in status
    assert "wake" not in status
    assert "stt" not in status


def test_normalize_tts_engine() -> None:
    from ric.voice.tts import normalize_tts_engine

    assert normalize_tts_engine(None) == "piper"
    assert normalize_tts_engine("chatterbox") == "chatterbox"
    assert normalize_tts_engine("experimental") == "chatterbox"


def test_synthesize_alert_routes_to_chatterbox(tmp_path, monkeypatch) -> None:
    class FakeCb:
        def synthesize_file(self, texto: str, out_path) -> bool:
            out_path.write_bytes(b"RIFF" + b"\x00" * 60)
            return True

    voice = VoiceService(backends=[], engine="piper", cache_dir=tmp_path)
    monkeypatch.setattr(voice, "_ensure_chatterbox", lambda: FakeCb())
    path = voice.synthesize_alert("Olá", stem="cmp", engine="chatterbox")
    assert path is not None
    assert "chatterbox" in path.name


def test_length_scale_for_stem_reply_is_faster_than_base() -> None:
    assert length_scale_for_stem("reply", 1.35) == pytest.approx(1.20)


def test_length_scale_for_stem_alert_uses_base() -> None:
    assert length_scale_for_stem("alert", 1.35) == pytest.approx(1.35)


def test_length_scale_for_stem_alert_follows_custom_base() -> None:
    assert length_scale_for_stem("alert", 1.1) == pytest.approx(1.1)


def test_length_scale_for_stem_unknown_stem_uses_base() -> None:
    assert length_scale_for_stem("other", 1.35) == pytest.approx(1.35)
