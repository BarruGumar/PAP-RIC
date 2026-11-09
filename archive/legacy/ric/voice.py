from __future__ import annotations

import shutil
import subprocess
import sys
import threading
from typing import Any


def beep() -> None:
    """Som curto de aviso (Windows winsound; senão bell ASCII)."""
    try:
        import winsound

        winsound.Beep(880, 400)
        return
    except Exception:
        pass
    try:
        print("\a", end="", flush=True)
    except Exception:
        pass


def _escape_ps(texto: str) -> str:
    return texto.replace("'", "''").replace("\r", " ").replace("\n", " ")


def _speak_sapi(texto: str) -> bool:
    """TTS via System.Speech (incluído no Windows) através do PowerShell."""
    if sys.platform != "win32":
        return False
    if not shutil.which("powershell"):
        return False
    safe = _escape_ps(texto.strip())
    if not safe:
        return False
    cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "try { $s.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::NotSet, "
        "[System.Speech.Synthesis.VoiceAge]::Adult, 0, "
        "[System.Globalization.CultureInfo]::new('pt-PT')) } catch {}; "
        f"$s.Speak('{safe}')"
    )
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def _speak_pyttsx3(texto: str) -> bool:
    try:
        import pyttsx3  # type: ignore
    except Exception:
        return False
    try:
        engine = pyttsx3.init()
        engine.say(texto)
        engine.runAndWait()
        return True
    except Exception:
        return False


def falar(texto: str, *, async_: bool = True) -> bool:
    """Lê o texto em voz alta. Degrada graciosamente se TTS falhar."""
    texto = (texto or "").strip()
    if not texto:
        return False

    def _run() -> None:
        if _speak_sapi(texto):
            return
        _speak_pyttsx3(texto)

    if async_:
        threading.Thread(target=_run, daemon=True).start()
        return True
    _run()
    return True


def estado() -> dict[str, Any]:
    sapi = sys.platform == "win32" and bool(shutil.which("powershell"))
    pyttsx = False
    try:
        import pyttsx3  # noqa: F401

        pyttsx = True
    except Exception:
        pass
    return {
        "tts_disponivel": sapi or pyttsx,
        "sapi": sapi,
        "pyttsx3": pyttsx,
        "stt_nota": (
            "STT no browser via Web Speech API quando o browser suportar; "
            "sem dependências Python pesadas."
        ),
    }
