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

# Alertas um pouco mais pausados; conversa mais ágil.
_REPLY_LENGTH_SCALE = 1.20


def length_scale_for_stem(stem: str, base: float) -> float:
    """Ritmo Piper por tipo de fala (reply vs alerta)."""
    safe_base = min(max(float(base), 0.9), 1.5)
    if (stem or "").strip().lower() == "reply":
        # Nunca mais lento que o alerta; com default 1.35 → 1.20.
        return min(safe_base, _REPLY_LENGTH_SCALE)
    return safe_base


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
    """Texto fluido para Piper (poucas pausas — vírgulas a mais soam a ‘travões’)."""
    t = (texto or "").strip()
    if not t:
        return ""
    # Maiúsculas «RIC» → soletrado R-I-C. Queremos o hipocorístico de Ricardo («Ric»).
    t = re.sub(
        r"\bR(?:[\s·]*\.?[\s·]*)I(?:[\s·]*\.?[\s·]*)C\b\.?",
        "Ric",
        t,
        flags=re.IGNORECASE,
    )
    t = t.replace("…", ",")
    t = t.replace(":", ",")
    t = t.replace(";", ",")
    t = t.replace("/", " ")
    t = t.replace("&", " e ")
    t = re.sub(r"[\[\]\{\}\(\)_*#@]+", " ", t)
    # Uma vírgula basta; várias seguidas = micro-pausas metálicas
    t = re.sub(r",+", ",", t)
    t = re.sub(r"\s*,\s*", ", ", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\.{2,}", ".", t)
    if not t.endswith((".", "!", "?")):
        t = t + "."
    return t


def format_alert_phrase(titulo: str) -> str:
    """Uma só frase — ponto a meio («Atenção.») causa a travadinha no Piper."""
    nome = re.sub(r"\s+", " ", (titulo or "").strip())
    nome = nome.rstrip(".")
    if not nome:
        nome = "o teu lembrete"
    # Vírgula = pausa curta; evita fim de frase a seguir a «Atenção»
    return f"Atenção, é a hora de {nome}."


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

    def warm_up(self) -> None:
        with self._lock:
            self._ensure()

    def synthesize_file(
        self,
        texto: str,
        out_path: Path,
        *,
        length_scale: float | None = None,
    ) -> bool:
        texto = prepare_speech_text(texto)
        if not texto or not self.model.is_file():
            return False
        defaults = _load_model_inference(self.model)
        # Preferido no RIC: ~1.35 alertas / ~1.20 replies. Acima de ~1.5 trava.
        scale = self.length_scale if length_scale is None else length_scale
        scale = min(max(float(scale), 0.9), 1.5)
        try:
            from piper.config import SynthesisConfig

            syn = SynthesisConfig(
                length_scale=scale,
                # Manter noise perto do default do modelo = prosódia mais natural
                noise_scale=float(defaults["noise_scale"]),
                noise_w_scale=float(defaults["noise_w"]),
                normalize_audio=True,
                volume=0.85,
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


def normalize_tts_engine(value: str | None) -> str:
    """Mantém API estável; o motor activo do RIC é só Piper."""
    _ = value
    return "piper"


class VoiceService:
    """TTS Piper → WAV + fallback SAPI/espeak."""

    def __init__(
        self,
        *,
        piper_model: Path | None = None,
        piper_bin: str | None = None,
        cache_dir: Path | None = None,
        length_scale: float = 1.35,
        engine: str = "piper",
        on_speaking: Callable[[bool], None] | None = None,
        backends: list[SpeakFn] | None = None,
    ) -> None:
        self.piper_model = piper_model
        self.piper_bin = piper_bin
        self.cache_dir = cache_dir
        self.length_scale = length_scale
        self.engine = normalize_tts_engine(engine)
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

        def _file_local(texto: str) -> bool:
            path = self.synthesize_alert(texto)
            if path is None:
                return False
            return _play_wav(path)

        if self._piper is not None:
            backends.append(_file_local)
        backends.append(speak_sapi)
        backends.append(speak_espeak)
        return backends

    def synthesize_alert(
        self, texto: str, *, stem: str = "alert", engine: str | None = None
    ) -> Path | None:
        """Gera WAV único do alerta (evita eco por ficheiro sobrescrito)."""
        chosen = normalize_tts_engine(engine or self.engine)
        base = self.cache_dir or Path.cwd() / "ric-data" / "tts"
        base.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem)[:40] or "alert"
        out = base / f"{safe}-{chosen}-{int(time.time() * 1000)}.wav"

        if self._piper is None:
            return None
        scale = length_scale_for_stem(safe, self.length_scale)
        if not self._piper.synthesize_file(texto, out, length_scale=scale):
            return None

        self.last_alert_wav = out
        try:
            old = sorted(base.glob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
            for stale in old[8:]:
                stale.unlink(missing_ok=True)
        except Exception:
            pass
        return out

    def warm_up(self) -> None:
        """Aquecer o Piper."""
        warm = self.cache_dir or Path.cwd() / "ric-data" / "tts"
        warm.mkdir(parents=True, exist_ok=True)
        if self._piper is None:
            return
        try:
            self._piper.warm_up()
            out = warm / "warmup-piper.wav"
            scale = length_scale_for_stem("reply", self.length_scale)
            self._piper.synthesize_file("Olá.", out, length_scale=scale)
            print("[RIC] TTS (Piper) aquecido.", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[RIC] TTS Piper warm-up falhou: {exc}", flush=True)

    def set_length_scale(self, value: float) -> float:
        """Ajusta ritmo TTS em runtime (ex.: `ric tune`)."""
        self.length_scale = min(max(float(value), 0.9), 1.5)
        if self._piper is not None:
            self._piper.length_scale = self.length_scale
        return self.length_scale

    def status(self) -> dict:
        piper_ok = self._piper is not None
        return {
            "piper": piper_ok,
            "piper_model": str(self.piper_model) if self.piper_model else None,
            "engine": "piper" if piper_ok else "fallback",
            "engine_requested": self.engine,
            "length_scale": self.length_scale,
            "playback": "browser+local",
            "sapi": sys.platform == "win32",
            "espeak": bool(shutil.which("espeak-ng") or shutil.which("espeak")),
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
