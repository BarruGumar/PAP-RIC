"""STT (Whisper local) — stub até à próxima fatia de voz."""

from __future__ import annotations


class SpeechToTextStub:
    def transcribe(self, audio_path: str) -> str:
        raise NotImplementedError("STT Whisper ainda não está na 1.ª fatia de voz.")

    @property
    def available(self) -> bool:
        return False
