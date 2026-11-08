"""STT local (faster-whisper / Whisper) com backend injectável para testes."""

from __future__ import annotations

import shutil
import tempfile
import threading
from pathlib import Path
from typing import Callable

TranscribeFn = Callable[[Path], str]

# Ajuda o Whisper a preferir vocabulário do RIC (pt) em clips curtos.
_PT_PROMPT = (
    "Olá RIC. Beber água. Lembrete. Medicamento. Que horas são. "
    "Conta uma história. Põe música. Adeus."
)


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
            # Clips curtos do botão Falar: VAD agressivo corta sílabas e piora o PT.
            segments, _info = model.transcribe(
                str(path),
                language=self.language,
                task="transcribe",
                beam_size=5,
                best_of=5,
                temperature=0.0,
                vad_filter=False,
                condition_on_previous_text=False,
                initial_prompt=_PT_PROMPT,
                without_timestamps=True,
            )
            parts = [seg.text.strip() for seg in segments if seg.text.strip()]
            return " ".join(parts).strip()

        self._engine = "faster-whisper"
        print(f"[RIC] Whisper ({self.model_size}) pronto.", flush=True)
        return _run

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
