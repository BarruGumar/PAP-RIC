"""Detector openWakeWord + sounddevice (modelo temporário ou ONNX em ric-data/wake/)."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any, Callable, Protocol


SAMPLE_RATE = 16_000
BLOCK_SAMPLES = 1280  # 80 ms — mínimo openWakeWord
DEFAULT_TEMP_MODEL = "hey_jarvis"
DEFAULT_THRESHOLD = 0.5
DEFAULT_DEBOUNCE_S = 1.5


class WakeSettings(Protocol):
    wake_enabled: bool
    wake_model: Path | None
    wake_threshold: float
    wake_debounce_s: float
    data_dir: Path


class WakeGate:
    """Threshold + debounce + pause — testável sem microfone."""

    def __init__(
        self,
        *,
        threshold: float = DEFAULT_THRESHOLD,
        debounce_s: float = DEFAULT_DEBOUNCE_S,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.threshold = float(threshold)
        self.debounce_s = float(debounce_s)
        self._clock = clock or time.monotonic
        self._paused = False
        self._last_fire = float("-inf")

    @property
    def paused(self) -> bool:
        return self._paused

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def should_fire(self, score: float) -> bool:
        if self._paused:
            return False
        if float(score) < self.threshold:
            return False
        now = self._clock()
        if now - self._last_fire < self.debounce_s:
            return False
        self._last_fire = now
        return True


class OpenWakeWordDetector:
    """Captura PCM 16 kHz e dispara `on_detect` quando o score passa o limiar."""

    def __init__(
        self,
        *,
        model_paths: list[str],
        model_label: str,
        threshold: float = DEFAULT_THRESHOLD,
        debounce_s: float = DEFAULT_DEBOUNCE_S,
        inference_framework: str = "onnx",
    ) -> None:
        self._model_paths = list(model_paths)
        self._model_label = model_label
        self._inference_framework = inference_framework
        self._gate = WakeGate(threshold=threshold, debounce_s=debounce_s)
        self._on_detect: Callable[[], None] | None = None
        self._running = False
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._model: Any = None
        self._available = False
        self._load_model()

    @property
    def available(self) -> bool:
        return self._available

    @property
    def model_label(self) -> str:
        return self._model_label

    @property
    def paused(self) -> bool:
        return self._gate.paused

    def pause(self) -> None:
        self._gate.pause()

    def resume(self) -> None:
        self._gate.resume()

    def start(self, on_detect: Callable[[], None]) -> None:
        if not self._available:
            return
        if self._running:
            return
        self._on_detect = on_detect
        self._stop.clear()
        self._running = True
        self._gate.resume()
        self._thread = threading.Thread(
            target=self._loop,
            name="ric-wake-oww",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        self._stop.set()
        thread = self._thread
        self._thread = None
        if thread and thread.is_alive():
            thread.join(timeout=2.0)
        self._on_detect = None

    def _load_model(self) -> None:
        try:
            from openwakeword.model import Model
        except ImportError as exc:
            print(f"[RIC] openwakeword não instalado: {exc}", flush=True)
            self._available = False
            return
        try:
            self._model = Model(
                wakeword_models=self._model_paths,
                inference_framework=self._inference_framework,
            )
            self._available = True
        except Exception as exc:  # noqa: BLE001
            print(f"[RIC] falha a carregar modelo wake: {exc}", flush=True)
            self._model = None
            self._available = False

    def _loop(self) -> None:
        try:
            import numpy as np
            import sounddevice as sd
        except ImportError as exc:
            print(f"[RIC] sounddevice/numpy indisponível para wake: {exc}", flush=True)
            self._running = False
            return

        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
                blocksize=BLOCK_SAMPLES,
            ) as stream:
                print(
                    f"[RIC] wake openWakeWord a ouvir ({self._model_label})",
                    flush=True,
                )
                while self._running and not self._stop.is_set():
                    chunk, overflowed = stream.read(BLOCK_SAMPLES)
                    if overflowed:
                        print(
                            "[RIC] wake overflow — amostras perdidas",
                            flush=True,
                        )
                    audio = (np.asarray(chunk).reshape(-1) * 32767.0).astype(
                        np.int16
                    )
                    self._predict_chunk(audio)
        except Exception as exc:  # noqa: BLE001
            print(f"[RIC] microfone wake falhou: {exc}", flush=True)
        finally:
            self._running = False

    def _predict_chunk(self, audio: Any) -> None:
        if not self._running or self._model is None:
            return
        try:
            scores = self._model.predict(audio)
        except Exception as exc:  # noqa: BLE001
            print(f"[RIC] wake predict erro: {exc}", flush=True)
            return
        self._process_scores(scores)

    def _process_scores(self, scores: dict[str, Any] | None) -> None:
        if not self._running or not scores:
            return
        best = 0.0
        for value in scores.values():
            try:
                best = max(best, float(value))
            except (TypeError, ValueError):
                continue
        if not self._gate.should_fire(best):
            return
        callback = self._on_detect
        if callback is None:
            return
        print(
            f"[RIC] wake detectado ({self._model_label} score≈{best:.2f})",
            flush=True,
        )
        try:
            callback()
        except Exception as exc:  # noqa: BLE001
            print(f"[RIC] erro no callback wake oww: {exc}", flush=True)


def _label_for_wake_path(path: Path) -> str:
    stem = path.stem.casefold().replace("-", "_")
    if stem in ("ric", "ei_ric"):
        return "ei RIC"
    return path.stem.replace("_", " ")


def resolve_wake_model_paths(settings: WakeSettings) -> tuple[list[str], str]:
    """Devolve (paths, label). Preferência: RIC_WAKE_MODEL → ric-data/wake/*.onnx → hey_jarvis."""
    if settings.wake_model is not None and settings.wake_model.is_file():
        return [str(settings.wake_model)], _label_for_wake_path(settings.wake_model)

    wake_dir = settings.data_dir / "wake"
    if wake_dir.is_dir():
        preferred = wake_dir / "ric.onnx"
        if preferred.is_file():
            return [str(preferred)], "ei RIC"
        onnx_files = sorted(wake_dir.glob("*.onnx"))
        if onnx_files:
            path = onnx_files[0]
            return [str(path)], _label_for_wake_path(path)

    return [DEFAULT_TEMP_MODEL], DEFAULT_TEMP_MODEL


def install_wake_model(source: Path, *, data_dir: Path) -> Path:
    """Copia um ONNX treinado para ric-data/wake/ric.onnx e valida o carregamento."""
    src = source.expanduser().resolve()
    if not src.is_file():
        raise FileNotFoundError(f"Ficheiro não encontrado: {src}")
    if src.suffix.casefold() != ".onnx":
        raise ValueError(f"Esperado um ficheiro .onnx, recebi: {src.name}")

    wake_dir = data_dir / "wake"
    wake_dir.mkdir(parents=True, exist_ok=True)
    dest = wake_dir / "ric.onnx"

    data = src.read_bytes()
    if len(data) < 256:
        raise ValueError("Ficheiro ONNX demasiado pequeno / inválido.")
    dest.write_bytes(data)

    readme = wake_dir / "README.txt"
    readme.write_text(
        "Modelos wake-word do RIC.\n"
        "- Activo: ric.onnx → frase «ei RIC».\n"
        "- Sem ric.onnx: fallback temporário hey_jarvis.\n"
        "- Instalar: py -m ric wake-install CAMINHO\\ei_ric.onnx\n"
        "- Roteiro: docs/ROTEIRO-WAKE-EI-RIC.md\n"
        "- Env: RIC_WAKE_MODEL, RIC_WAKE_THRESHOLD, RIC_WAKE_ENABLED.\n",
        encoding="utf-8",
    )

    try:
        from openwakeword.model import Model

        Model(wakeword_models=[str(dest)], inference_framework="onnx")
    except ImportError as exc:
        raise RuntimeError(
            "openwakeword não instalado — py -m pip install openwakeword"
        ) from exc
    except Exception as exc:  # noqa: BLE001
        dest.unlink(missing_ok=True)
        raise RuntimeError(f"ONNX inválido para openWakeWord: {exc}") from exc

    return dest


def ensure_wake_models_downloaded() -> None:
    """Descarrega embeddings + modelos built-in openWakeWord (1.ª vez)."""
    import openwakeword.utils as oww_utils

    oww_utils.download_models()


def try_create_detector(settings: WakeSettings) -> OpenWakeWordDetector | None:
    if not settings.wake_enabled:
        return None
    try:
        import openwakeword  # noqa: F401
        import sounddevice  # noqa: F401
    except ImportError as exc:
        print(f"[RIC] wake contínuo off (deps): {exc}", flush=True)
        return None

    paths, label = resolve_wake_model_paths(settings)
    wake_dir = settings.data_dir / "wake"
    try:
        wake_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    # Download só via `py -m ric wake-setup` (local-first; sem HTTP no arranque).
    try:
        det = OpenWakeWordDetector(
            model_paths=paths,
            model_label=label,
            threshold=settings.wake_threshold,
            debounce_s=settings.wake_debounce_s,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[RIC] wake detector falhou: {exc}", flush=True)
        return None
    if not det.available:
        print(
            "[RIC] wake contínuo indisponível — corre: py -m ric wake-setup",
            flush=True,
        )
        return None
    return det
