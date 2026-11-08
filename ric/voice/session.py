"""Sessão de voz: wake → listening → STT → LLM → TTS → idle."""

from __future__ import annotations

import base64
import binascii
import threading
from typing import Any, Protocol

from ric.core.events import EventBus
from ric.voice.stt import SpeechToText, SttUnavailableError


class LlmLike(Protocol):
    available: bool

    def chat(self, text: str) -> str: ...

    def status(self) -> dict: ...


class TtsLike(Protocol):
    def synthesize_alert(self, texto: str, *, stem: str = "alert") -> Any: ...


class VoiceSession:
    def __init__(
        self,
        *,
        events: EventBus,
        stt: SpeechToText,
        llm: LlmLike | None = None,
        tts: TtsLike | None = None,
    ) -> None:
        self.events = events
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self._lock = threading.Lock()
        self.last_transcript: str | None = None
        self.last_reply: str | None = None
        self.last_audio_url: str | None = None

    def on_wake(self) -> None:
        with self._lock:
            # Não interromper alerta crítico nesta fatia
            if self.events.state == "alert":
                return
            self.events.set_state("listening")
            self.events.publish({"type": "wake_detected"})

    def cancel(self) -> None:
        with self._lock:
            if self.events.state == "listening":
                self.events.set_state("idle")
                self.events.publish({"type": "listen_cancelled"})

    def process_audio(
        self,
        data: bytes,
        *,
        content_type: str = "audio/wav",
    ) -> str:
        with self._lock:
            if self.events.state == "alert":
                raise ValueError("Alerta activo — termina o lembrete primeiro.")
            self.events.set_state("thinking")
            self.events.publish({"type": "stt_started"})
        try:
            suffix = _suffix_for(content_type)
            text = self.stt.transcribe_bytes(data, suffix=suffix)
        except SttUnavailableError:
            self._finish_error("Reconhecimento de voz indisponível neste PC.")
            raise
        except Exception as exc:  # noqa: BLE001
            self._finish_error(str(exc))
            raise

        with self._lock:
            self.last_transcript = text
            self.events.publish({"type": "transcript", "text": text})
            if self.events.state == "alert":
                return text

        reply = self._maybe_chat(text)
        audio_url = None
        if reply and self.tts is not None and self.events.state != "alert":
            with self._lock:
                if self.events.state != "alert":
                    self.events.set_state("speaking")
            try:
                wav = self.tts.synthesize_alert(reply, stem="reply")
                if wav is not None:
                    audio_url = f"/api/v1/tts/{wav.name}"
                    self.last_audio_url = audio_url
                    self.events.publish(
                        {
                            "type": "assistant_reply",
                            "text": reply,
                            "audio_url": audio_url,
                            "play_id": f"reply-{wav.stem}",
                        }
                    )
                else:
                    self.events.publish(
                        {"type": "assistant_reply", "text": reply, "audio_url": None}
                    )
            except Exception as exc:  # noqa: BLE001
                self.events.publish(
                    {
                        "type": "assistant_reply",
                        "text": reply,
                        "audio_url": None,
                        "tts_error": str(exc),
                    }
                )
        elif reply:
            self.events.publish(
                {"type": "assistant_reply", "text": reply, "audio_url": None}
            )

        with self._lock:
            if self.events.state != "alert":
                self.events.set_state("idle")
        return text

    def _maybe_chat(self, text: str) -> str | None:
        if self.llm is None:
            return None
        if not text.strip():
            return None
        try:
            reply = (self.llm.chat(text) or "").strip()
        except Exception as exc:  # noqa: BLE001
            self.events.publish({"type": "llm_error", "error": str(exc)})
            return None
        self.last_reply = reply or None
        return self.last_reply

    def process_base64(
        self,
        audio_b64: str,
        *,
        content_type: str = "audio/wav",
    ) -> str:
        try:
            raw = base64.b64decode(audio_b64, validate=True)
        except (binascii.Error, ValueError) as exc:
            self._finish_error("Áudio inválido.")
            raise ValueError("audio_base64 inválido") from exc
        return self.process_audio(raw, content_type=content_type)

    def _finish_error(self, message: str) -> None:
        with self._lock:
            if self.events.state != "alert":
                self.events.set_state("idle")
            self.events.publish({"type": "stt_error", "error": message})

    def status(self) -> dict[str, Any]:
        return {
            "last_transcript": self.last_transcript,
            "last_reply": self.last_reply,
            "last_audio_url": self.last_audio_url,
            "stt": self.stt.status(),
            "llm": self.llm.status() if self.llm is not None else {"available": False},
        }


def _suffix_for(content_type: str) -> str:
    ct = (content_type or "").lower()
    if "webm" in ct:
        return ".webm"
    if "ogg" in ct:
        return ".ogg"
    if "mpeg" in ct or "mp3" in ct:
        return ".mp3"
    return ".wav"
