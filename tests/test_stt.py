"""Unit — STT com backend injectável (sem Whisper real)."""

from __future__ import annotations

from pathlib import Path

import pytest

from ric.voice.stt import SpeechToText, SttUnavailableError


def test_transcribe_file_uses_backend(tmp_path: Path) -> None:
    wav = tmp_path / "clip.wav"
    wav.write_bytes(b"RIFF....")

    stt = SpeechToText(backend=lambda path: f"ouvi:{path.name}")
    assert stt.available is True
    assert stt.transcribe_file(wav) == "ouvi:clip.wav"


def test_transcribe_bytes_writes_temp_and_cleans(tmp_path: Path) -> None:
    seen: list[Path] = []

    def backend(path: Path) -> str:
        seen.append(path)
        assert path.is_file()
        return "olá ric"

    stt = SpeechToText(backend=backend, cache_dir=tmp_path)
    text = stt.transcribe_bytes(b"fake-wav", suffix=".wav")
    assert text == "olá ric"
    assert seen and not seen[0].exists()


def test_unavailable_without_backend_raises() -> None:
    stt = SpeechToText(backend=None, auto_load=False)
    assert stt.available is False
    with pytest.raises(SttUnavailableError):
        stt.transcribe_bytes(b"x")


def test_status_keys() -> None:
    stt = SpeechToText(backend=lambda _p: "ok")
    status = stt.status()
    assert status["available"] is True
    assert "engine" in status
