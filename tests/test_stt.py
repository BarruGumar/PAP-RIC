"""Unit — STT com backend injectável (sem Whisper real)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from ric.voice.stt import SpeechToText, SttUnavailableError, join_transcript_segments


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


def _segment(text: str, **extra: float) -> SimpleNamespace:
    return SimpleNamespace(text=text, **extra)


def test_join_transcript_segments_joins_stripped_text_with_spaces() -> None:
    segments = [_segment("  olá "), _segment("\nric  "), _segment(" tudo bem?")]
    assert join_transcript_segments(segments) == "olá ric tudo bem?"


def test_join_transcript_segments_empty_input_returns_empty_string() -> None:
    assert join_transcript_segments([]) == ""


def test_join_transcript_segments_skips_blank_segments() -> None:
    segments = [_segment("olá"), _segment("   "), _segment("ric")]
    assert join_transcript_segments(segments) == "olá ric"


def test_join_transcript_segments_returns_empty_when_no_speech_prob_at_threshold() -> None:
    segments = [_segment("ruído")]
    assert join_transcript_segments(segments, no_speech_prob=0.6) == ""


def test_join_transcript_segments_returns_empty_when_no_speech_prob_above_threshold() -> None:
    segments = [_segment("ruído")]
    assert join_transcript_segments(segments, no_speech_prob=0.95) == ""


def test_join_transcript_segments_keeps_text_when_no_speech_prob_below_threshold() -> None:
    segments = [_segment("olá ric")]
    assert join_transcript_segments(segments, no_speech_prob=0.59) == "olá ric"


def test_join_transcript_segments_ignores_none_no_speech_prob() -> None:
    segments = [_segment("olá ric")]
    assert join_transcript_segments(segments, no_speech_prob=None) == "olá ric"


def test_join_transcript_segments_respects_custom_no_speech_threshold() -> None:
    segments = [_segment("olá ric")]
    assert join_transcript_segments(segments, no_speech_prob=0.3, no_speech_threshold=0.2) == ""
    assert join_transcript_segments(segments, no_speech_prob=0.3, no_speech_threshold=0.5) == "olá ric"


def test_join_transcript_segments_drops_low_avg_logprob() -> None:
    segments = [
        _segment("olá", avg_logprob=-0.3),
        _segment("alucinação", avg_logprob=-1.5),
        _segment("ric", avg_logprob=-0.8),
    ]
    assert join_transcript_segments(segments) == "olá ric"


def test_join_transcript_segments_keeps_avg_logprob_at_threshold() -> None:
    segments = [_segment("olá", avg_logprob=-1.2)]
    assert join_transcript_segments(segments) == "olá"


def test_join_transcript_segments_keeps_segments_missing_avg_logprob() -> None:
    segments = [_segment("sem métrica"), _segment("descartado", avg_logprob=-2.0)]
    assert join_transcript_segments(segments) == "sem métrica"


def test_join_transcript_segments_respects_custom_min_avg_logprob() -> None:
    segments = [_segment("olá", avg_logprob=-0.9), _segment("ric", avg_logprob=-0.4)]
    assert join_transcript_segments(segments, min_avg_logprob=-0.5) == "ric"


def test_join_transcript_segments_returns_empty_when_all_segments_dropped() -> None:
    segments = [_segment("lixo", avg_logprob=-3.0)]
    assert join_transcript_segments(segments) == ""


def test_join_transcript_segments_drops_high_segment_no_speech_prob() -> None:
    segments = [
        _segment("olá", no_speech_prob=0.1),
        _segment("ruído", no_speech_prob=0.9),
        _segment("ric", no_speech_prob=0.2),
    ]
    assert join_transcript_segments(segments) == "olá ric"
