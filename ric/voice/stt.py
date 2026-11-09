"""STT local (faster-whisper / Whisper) com backend injectável para testes."""

from __future__ import annotations

import shutil
import struct
import tempfile
import threading
import wave
from pathlib import Path
from typing import Any, Callable, Iterable

TranscribeFn = Callable[[Path], str]

# Prompt curto: prompts longos fazem o Whisper «alucinar» frases do exemplo.
_PT_PROMPT = "Olá. Português de Portugal."
_NO_SPEECH_THRESHOLD = 0.6
_MIN_AVG_LOGPROB = -1.2


def join_transcript_segments(
    segments: Iterable[Any],
    *,
    no_speech_prob: float | None = None,
    no_speech_threshold: float = _NO_SPEECH_THRESHOLD,
    min_avg_logprob: float = _MIN_AVG_LOGPROB,
) -> str:
    """Junta texto dos segmentos Whisper, rejeitando silêncio e segmentos fracos."""
    if isinstance(no_speech_prob, (int, float)) and float(no_speech_prob) >= no_speech_threshold:
        return ""
    parts: list[str] = []
    for seg in segments:
        text = (getattr(seg, "text", None) or "").strip()
        if not text:
            continue
        seg_ns = getattr(seg, "no_speech_prob", None)
        if isinstance(seg_ns, (int, float)) and float(seg_ns) >= no_speech_threshold:
            continue
        if hasattr(seg, "avg_logprob"):
            score = getattr(seg, "avg_logprob", None)
            if isinstance(score, (int, float)) and float(score) < min_avg_logprob:
                continue
        parts.append(text)
    return " ".join(parts).strip()


def _write_silent_wav(path: Path, *, seconds: float = 0.35, rate: int = 16000) -> None:
    """WAV PCM silencioso curto — aquece o decoder CTranslate2."""
    n = max(1, int(rate * seconds))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(struct.pack(f"<{n}h", *([0] * n)))


class SttUnavailableError(RuntimeError):
    """Whisper/faster-whisper não está disponível neste ambiente."""


class SpeechToText:
    def __init__(
        self,
        *,
        backend: TranscribeFn | None = None,
        cache_dir: Path | None = None,
        model_size: str = "small",
        language: str = "pt",
        auto_load: bool = True,
    ) -> None:
        self.cache_dir = cache_dir
        self.model_size = model_size
        self.language = language
        self._auto_load = auto_load
        self._backend = backend
        self._engine = "mock" if backend is not None else "none"
        self._load_lock = threading.Lock()
        self._load_error: str | None = None
        # Lazy: não descarregar/carregar o modelo no __init__ (UI e testes arrancam já).

    def _ensure_backend(self) -> TranscribeFn:
        if self._backend is not None:
            return self._backend
        if not self._auto_load:
            raise SttUnavailableError(
                "STT indisponível. Instala faster-whisper: py -m pip install faster-whisper"
            )
        with self._load_lock:
            if self._backend is not None:
                return self._backend
            loaded = self._try_load_faster_whisper()
            if loaded is None:
                detail = self._load_error or "faster-whisper não disponível"
                raise SttUnavailableError(detail)
            self._backend = loaded
            return self._backend

    def _try_load_faster_whisper(self) -> TranscribeFn | None:
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except ImportError:
            self._load_error = (
                "STT indisponível. Instala faster-whisper: py -m pip install faster-whisper"
            )
            return None
        try:
            print(
                f"[RIC] A carregar Whisper ({self.model_size})… "
                "(1.ª vez pode demorar a descarregar)",
                flush=True,
            )
            model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        except Exception as exc:  # noqa: BLE001
            self._load_error = f"faster-whisper não carregou: {exc}"
            print(f"[RIC] {self._load_error}", flush=True)
            return None

        def _run(path: Path) -> str:
            # beam=3: meio-termo CPU (5 era lento; 1 alucinava em clips curtos).
            # VAD no modelo desligado — o browser já corta silêncio à cabeça/cauda.
            segments, _info = model.transcribe(
                str(path),
                language=self.language,
                task="transcribe",
                beam_size=3,
                best_of=3,
                temperature=0.0,
                vad_filter=False,
                condition_on_previous_text=False,
                initial_prompt=_PT_PROMPT,
                without_timestamps=True,
                no_speech_threshold=_NO_SPEECH_THRESHOLD,
            )
            # no_speech_prob vive nos Segment (faster-whisper).
            return join_transcript_segments(segments)

        self._engine = "faster-whisper"
        print(f"[RIC] Whisper ({self.model_size}) pronto.", flush=True)
        return _run

    def warm_up(self) -> None:
        """Carregar o modelo e aquecer o decoder com um clip curto."""
        if self._backend is not None and self._engine == "mock":
            return
        try:
            self._ensure_backend()
            if self._engine != "faster-whisper":
                return
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            path = Path(tmp.name)
            tmp.close()
            try:
                _write_silent_wav(path)
                self.transcribe_file(path)
            finally:
                path.unlink(missing_ok=True)
            print("[RIC] STT aquecido.", flush=True)
        except SttUnavailableError as exc:
            print(f"[RIC] STT warm-up falhou: {exc}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[RIC] STT warm-up falhou: {exc}", flush=True)

    @property
    def available(self) -> bool:
        if self._backend is not None:
            return True
        if not self._auto_load:
            return False
        try:
            import faster_whisper  # noqa: F401
        except ImportError:
            return False
        return self._load_error is None

    def status(self) -> dict:
        loaded = self._backend is not None and self._engine == "faster-whisper"
        return {
            "available": self.available,
            "engine": self._engine if self._backend is not None else (
                "faster-whisper (lazy)" if self.available else "none"
            ),
            "loaded": loaded or (self._backend is not None and self._engine == "mock"),
            "model_size": self.model_size,
            "language": self.language,
        }

    def transcribe_file(self, path: Path) -> str:
        backend = self._ensure_backend()
        text = backend(path)
        return (text or "").strip()

    def transcribe_bytes(self, data: bytes, *, suffix: str = ".wav") -> str:
        self._ensure_backend()
        if self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            tmp_ctx = tempfile.NamedTemporaryFile(
                delete=False, suffix=suffix, dir=self.cache_dir
            )
        else:
            tmp_ctx = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        with tmp_ctx as tmp:
            tmp.write(data)
            path = Path(tmp.name)
        try:
            if self.cache_dir is not None:
                try:
                    shutil.copy2(path, self.cache_dir / f"last{suffix}")
                except Exception:  # noqa: BLE001
                    pass
            return self.transcribe_file(path)
        finally:
            path.unlink(missing_ok=True)
