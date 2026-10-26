from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path
from typing import Callable


SpeakFn = Callable[[str], bool]


def beep() -> None:
    try:
        if sys.platform == "win32":
            import winsound

            winsound.Beep(740, 180)
            return
    except Exception:
        pass
    try:
        print("\a", end="", flush=True)
    except Exception:
        pass


def prepare_speech_text(texto: str) -> str:
    """Texto fluido para Piper (sem cortes a mais que soam a ‘travões’)."""
    t = (texto or "").strip()
    if not t:
        return ""
    t = t.replace("…", ",")
    t = t.replace(":", ",")
    t = t.replace(";", ",")
    t = t.replace("/", " ")
    t = t.replace("&", " e ")
    # Evitar vários pontos seguidos → pausas bruscas
    t = re.sub(r"[\[\]\{\}\(\)_*#@]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\.{2,}", ".", t)
    if not t.endswith((".", "!", "?")):
        t = t + "."
    return t


def _escape_ps(texto: str) -> str:
    return texto.replace("'", "''").replace("\r", " ").replace("\n", " ")


def _play_wav(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 44:
        return False
    if sys.platform == "win32" and shutil.which("powershell"):
        safe = str(path.resolve()).replace("'", "''")
        cmd = (
            "Add-Type -AssemblyName System.Media; "
            f"$p = New-Object System.Media.SoundPlayer '{safe}'; "
            "$p.Load(); $p.PlaySync()"
        )
        try:
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", cmd],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if proc.returncode == 0:
                return True
        except Exception:
            pass
    try:
        if sys.platform == "win32":
            import winsound

            winsound.PlaySound(str(path), winsound.SND_FILENAME)
            return True
    except Exception:
        pass
    for player in ("aplay", "ffplay", "afplay"):
        if shutil.which(player):
            cmd = [player, str(path)]
            if player == "ffplay":
                cmd = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", str(path)]
            try:
                subprocess.run(
                    cmd,
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except Exception:
                continue
    return False


def _load_model_inference(model: Path) -> dict[str, float]:
    cfg = Path(str(model) + ".json")
    if not cfg.is_file():
        return {"length_scale": 1.0, "noise_scale": 0.667, "noise_w": 0.8}
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        inf = data.get("inference") or {}
        return {
            "length_scale": float(inf.get("length_scale", 1.0)),
            "noise_scale": float(inf.get("noise_scale", 0.667)),
            "noise_w": float(inf.get("noise_w", 0.8)),
        }
    except Exception:
        return {"length_scale": 1.0, "noise_scale": 0.667, "noise_w": 0.8}


class PiperEngine:
    """Mantém o modelo carregado e escreve WAV PCM válidos."""

    def __init__(self, model: Path, *, length_scale: float = 1.35) -> None:
        self.model = model
        self.length_scale = length_scale
        self._voice = None
        self._lock = threading.Lock()

    def _ensure(self):
        if self._voice is not None:
            return self._voice
        from piper import PiperVoice

        self._voice = PiperVoice.load(self.model)
        return self._voice

    def synthesize_file(self, texto: str, out_path: Path) -> bool:
        texto = prepare_speech_text(texto)
        if not texto or not self.model.is_file():
            return False
        defaults = _load_model_inference(self.model)
        # 1.3–1.4: mais lento sem artefactos; >1.5 costuma “travar” a prosódia
        length_scale = max(min(self.length_scale, 1.5), defaults["length_scale"])
        try:
            from piper.config import SynthesisConfig

            syn = SynthesisConfig(
                length_scale=length_scale,
                # Um pouco menos noise = menos “chiado”; volume < 1 evita estouro
                noise_scale=min(defaults["noise_scale"], 0.6),
                noise_w_scale=min(defaults["noise_w"], 0.75),
                normalize_audio=True,
                volume=0.75,
            )
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with self._lock:
                voice = self._ensure()
                with wave.open(str(out_path), "wb") as wav_file:
                    voice.synthesize_wav(texto, wav_file, syn_config=syn)
            return out_path.is_file() and out_path.stat().st_size > 44
        except Exception as exc:
            print(f"[RIC TTS] Piper falhou: {exc}", flush=True)
            return False


def speak_sapi(texto: str) -> bool:
    if sys.platform != "win32" or not shutil.which("powershell"):
        return False
    safe = _escape_ps(prepare_speech_text(texto))
    if not safe:
        return False
    cmd = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.Rate = -2; "
        "try { $s.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::NotSet, "
        "[System.Speech.Synthesis.VoiceAge]::Adult, 0, "
        "[System.Globalization.CultureInfo]::new('pt-PT')) } catch {}; "
        f"$s.Speak('{safe}')"
    )
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", cmd],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def speak_espeak(texto: str) -> bool:
    bin_name = shutil.which("espeak-ng") or shutil.which("espeak")
    if not bin_name:
        return False
    try:
        subprocess.run(
            [bin_name, "-v", "pt", "-s", "130", prepare_speech_text(texto)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


class VoiceService:
    """TTS: Piper → ficheiro WAV (UI toca no browser) + fallback SAPI/espeak."""

    def __init__(
        self,
        *,
        piper_model: Path | None = None,
        piper_bin: str | None = None,
        cache_dir: Path | None = None,
        length_scale: float = 1.35,
        on_speaking: Callable[[bool], None] | None = None,
        backends: list[SpeakFn] | None = None,
    ) -> None:
        self.piper_model = piper_model
        self.piper_bin = piper_bin
        self.cache_dir = cache_dir
        self.length_scale = length_scale
        self.on_speaking = on_speaking
        self._lock = threading.Lock()
        self._piper: PiperEngine | None = (
            PiperEngine(piper_model, length_scale=length_scale)
            if piper_model and piper_model.is_file()
            else None
        )
        self.last_alert_wav: Path | None = None
        if backends is not None:
            self._backends = backends
        else:
            self._backends = self._default_backends()

    def _default_backends(self) -> list[SpeakFn]:
        backends: list[SpeakFn] = []

        def _piper_local(texto: str) -> bool:
            path = self.synthesize_alert(texto)
            if path is None:
                return False
            return _play_wav(path)

        if self._piper is not None:
            backends.append(_piper_local)
        backends.append(speak_sapi)
        backends.append(speak_espeak)
        return backends

    def synthesize_alert(
        self, texto: str, *, stem: str = "alert"
    ) -> Path | None:
        """Gera WAV único do alerta (evita eco por ficheiro sobrescrito)."""
        if self._piper is None:
            return None
        base = self.cache_dir or Path.cwd() / "ric-data" / "tts"
        base.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem)[:40] or "alert"
        out = base / f"{safe}-{int(time.time() * 1000)}.wav"
        if not self._piper.synthesize_file(texto, out):
            return None
        self.last_alert_wav = out
        # Limpar WAV antigos (manter os 5 mais recentes)
        try:
            old = sorted(base.glob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
            for stale in old[5:]:
                stale.unlink(missing_ok=True)
        except Exception:
            pass
        return out

    def status(self) -> dict:
        piper_ok = self._piper is not None
        return {
            "piper": piper_ok,
            "piper_model": str(self.piper_model) if self.piper_model else None,
            "engine": "piper" if piper_ok else "fallback",
            "length_scale": self.length_scale,
            "playback": "browser+local",
            "sapi": sys.platform == "win32",
            "espeak": bool(shutil.which("espeak-ng") or shutil.which("espeak")),
            "wake": "stub",
            "stt": "stub",
        }

    def speak(self, texto: str, *, async_: bool = True, with_beep: bool = False) -> bool:
        """Fallback local (CLI). Na UI o alerta usa WAV no browser."""
        texto = prepare_speech_text(texto)
        if not texto:
            return False

        def _run() -> None:
            with self._lock:
                if self.on_speaking:
                    self.on_speaking(True)
                try:
                    if with_beep:
                        beep()
                        time.sleep(0.25)
                    for backend in self._backends:
                        try:
                            if backend(texto):
                                return
                        except Exception:
                            continue
                finally:
                    if self.on_speaking:
                        self.on_speaking(False)

        if async_:
            threading.Thread(target=_run, name="ric-tts", daemon=True).start()
            return True
        _run()
        return True
