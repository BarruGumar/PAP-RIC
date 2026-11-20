"""Unit — openWakeWord detector gate (pause/debounce) e factory sem deps."""

from __future__ import annotations

import pytest

from ric.voice.oww_detector import WakeGate, install_wake_model, try_create_detector


def test_wake_gate_fires_above_threshold() -> None:
    clock = {"t": 0.0}
    gate = WakeGate(threshold=0.5, debounce_s=1.5, clock=lambda: clock["t"])
    assert gate.should_fire(0.4) is False
    assert gate.should_fire(0.6) is True


def test_wake_gate_debounce_blocks_burst() -> None:
    clock = {"t": 0.0}
    gate = WakeGate(threshold=0.5, debounce_s=1.5, clock=lambda: clock["t"])
    assert gate.should_fire(0.9) is True
    clock["t"] = 0.5
    assert gate.should_fire(0.9) is False
    clock["t"] = 1.6
    assert gate.should_fire(0.9) is True


def test_wake_gate_pause_blocks_fire() -> None:
    gate = WakeGate(threshold=0.5, debounce_s=0.0, clock=lambda: 0.0)
    gate.pause()
    assert gate.paused is True
    assert gate.should_fire(0.99) is False
    gate.resume()
    assert gate.paused is False
    assert gate.should_fire(0.99) is True


def test_try_create_detector_disabled_returns_none() -> None:
    class S:
        wake_enabled = False
        wake_model = None
        wake_threshold = 0.5
        wake_debounce_s = 1.5
        data_dir = None

    assert try_create_detector(S()) is None


def test_resolve_prefers_ric_onnx(tmp_path) -> None:
    from ric.voice.oww_detector import resolve_wake_model_paths

    wake_dir = tmp_path / "wake"
    wake_dir.mkdir()
    (wake_dir / "other.onnx").write_bytes(b"x")
    ric = wake_dir / "ric.onnx"
    ric.write_bytes(b"x")

    class S:
        wake_enabled = True
        wake_model = None
        wake_threshold = 0.5
        wake_debounce_s = 1.5
        data_dir = tmp_path

    paths, label = resolve_wake_model_paths(S())
    assert paths == [str(ric)]
    assert label == "ei RIC"


def test_resolve_falls_back_to_hey_jarvis(tmp_path) -> None:
    from ric.voice.oww_detector import DEFAULT_TEMP_MODEL, resolve_wake_model_paths

    class S:
        wake_enabled = True
        wake_model = None
        wake_threshold = 0.5
        wake_debounce_s = 1.5
        data_dir = tmp_path

    paths, label = resolve_wake_model_paths(S())
    assert paths == [DEFAULT_TEMP_MODEL]
    assert label == DEFAULT_TEMP_MODEL


def test_install_wake_model_rejects_missing(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        install_wake_model(tmp_path / "no.onnx", data_dir=tmp_path)


def test_install_wake_model_rejects_wrong_suffix(tmp_path) -> None:
    src = tmp_path / "x.bin"
    src.write_bytes(b"x" * 300)
    with pytest.raises(ValueError, match="onnx"):
        install_wake_model(src, data_dir=tmp_path)


def test_install_wake_model_copies_when_load_ok(tmp_path, monkeypatch) -> None:
    class FakeModel:
        def __init__(self, *args, **kwargs) -> None:
            return None

    monkeypatch.setattr("openwakeword.model.Model", FakeModel)
    src = tmp_path / "ei_ric.onnx"
    src.write_bytes(b"fake-onnx-bytes" * 40)
    data_dir = tmp_path / "ric-data"
    dest = install_wake_model(src, data_dir=data_dir)
    assert dest == data_dir / "wake" / "ric.onnx"
    assert dest.is_file()
    assert (data_dir / "wake" / "README.txt").is_file()


def test_install_wake_model_removes_dest_when_invalid(tmp_path, monkeypatch) -> None:
    class Boom:
        def __init__(self, *args, **kwargs) -> None:
            raise RuntimeError("bad onnx")

    monkeypatch.setattr("openwakeword.model.Model", Boom)
    src = tmp_path / "ei_ric.onnx"
    src.write_bytes(b"fake-onnx-bytes" * 40)
    data_dir = tmp_path / "ric-data"
    with pytest.raises(RuntimeError, match="inválido"):
        install_wake_model(src, data_dir=data_dir)
    assert not (data_dir / "wake" / "ric.onnx").exists()


def test_detector_process_scores_uses_gate() -> None:
    from ric.voice.oww_detector import OpenWakeWordDetector

    hits: list[str] = []
    det = OpenWakeWordDetector.__new__(OpenWakeWordDetector)
    det._gate = WakeGate(threshold=0.5, debounce_s=1.5, clock=lambda: 10.0)
    det._on_detect = lambda: hits.append("ok")
    det._running = True
    det._model_label = "hey_jarvis"
    det._process_scores({"hey_jarvis": 0.8})
    assert hits == ["ok"]
    det._process_scores({"hey_jarvis": 0.9})
    assert hits == ["ok"]  # debounce


def test_detector_ignored_when_not_running() -> None:
    from ric.voice.oww_detector import OpenWakeWordDetector

    hits: list[str] = []
    det = OpenWakeWordDetector.__new__(OpenWakeWordDetector)
    det._gate = WakeGate(threshold=0.5, debounce_s=0.0, clock=lambda: 0.0)
    det._on_detect = lambda: hits.append("ok")
    det._running = False
    det._process_scores({"hey_jarvis": 0.99})
    assert hits == []
