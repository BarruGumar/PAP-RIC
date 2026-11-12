"""TTS experimental Chatterbox — pack/ref pt-PT (Portugal), não o genérico BR."""

from __future__ import annotations

import threading
import urllib.request
import wave
from pathlib import Path
from typing import Any


DEFAULT_BASE_REPO = "ResembleAI/chatterbox"
DEFAULT_PACK_REPO = "ResembleAI/Chatterbox-Multilingual-pt-pt"
DEFAULT_LANGUAGE_ID = "pt"
DEFAULT_T3_MODEL = "pt-pt"
PT_PT_REF_URL = (
    "https://storage.googleapis.com/chatterbox-demo-samples/"
    "mtl-v3-single-language-prompts/pt-pt/pt_pt_m1.wav"
)
DEFAULT_REF_NAME = "pt_pt_ref.wav"


def chatterbox_importable() -> bool:
    try:
        import importlib.util

        return importlib.util.find_spec("chatterbox") is not None
    except Exception:
        return False


def resolve_device(preferred: str = "auto") -> str:
    pref = (preferred or "auto").strip().lower()
    if pref in ("cpu", "cuda", "mps"):
        return pref
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def default_ref_path(data_dir: Path | None = None) -> Path:
    base = data_dir or Path("./ric-data")
    return (base / "vozes" / "extras" / DEFAULT_REF_NAME).resolve()


def ensure_pt_pt_reference(
    dest: Path | None = None, *, data_dir: Path | None = None
) -> Path:
    path = dest or default_ref_path(data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.stat().st_size > 1000:
        return path
    print(f"[RIC TTS] A descarregar referência pt-PT → {path.name}…", flush=True)
    urllib.request.urlretrieve(PT_PT_REF_URL, path)
    if not path.is_file() or path.stat().st_size < 1000:
        raise RuntimeError(f"Falha a descarregar referência pt-PT: {path}")
    return path


def _write_wav_mono(path: Path, samples: Any, sample_rate: int) -> bool:
    try:
        import numpy as np
    except Exception as exc:  # noqa: BLE001
        print(f"[RIC TTS] Chatterbox precisa de numpy: {exc}", flush=True)
        return False

    audio = np.asarray(samples, dtype=np.float32).reshape(-1)
    if audio.size == 0:
        return False
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 1.0:
        audio = audio / peak
    pcm = (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(int(sample_rate))
        wav_file.writeframes(pcm.tobytes())
    return path.is_file() and path.stat().st_size > 44


def pt_pt_pack_cached() -> bool:
    try:
        from huggingface_hub import try_to_load_from_cache

        path = try_to_load_from_cache(DEFAULT_PACK_REPO, "t3_pt_pt.safetensors")
        if not path:
            return False
        p = Path(path)
        return p.is_file() and p.stat().st_size > 500_000_000
    except Exception:
        return False


def _load_s3gen_state(path: Path, map_location):
    import torch
    from safetensors.torch import load_file as load_safetensors

    if path.suffix == ".safetensors":
        return load_safetensors(str(path))
    return torch.load(path, map_location=map_location, weights_only=True)


def load_pt_pt_pack(device: str):
    import torch
    from huggingface_hub import snapshot_download
    from safetensors.torch import load_file as load_safetensors

    from chatterbox.models.s3gen import S3Gen
    from chatterbox.models.t3 import T3
    from chatterbox.models.t3.modules.t3_config import T3Config
    from chatterbox.models.tokenizers import MTLTokenizer
    from chatterbox.models.voice_encoder import VoiceEncoder
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS, Conditionals

    print(
        f"[RIC TTS] A obter pack pt-PT ({DEFAULT_PACK_REPO}) + base partilhada…",
        flush=True,
    )
    base_dir = Path(
        snapshot_download(
            repo_id=DEFAULT_BASE_REPO,
            repo_type="model",
            allow_patterns=[
                "ve.pt",
                "conds.pt",
                "s3gen.pt",
                "grapheme_mtl_merged_expanded_v1.json",
                "Cangjie5_TC.json",
            ],
        )
    )
    pack_dir = Path(
        snapshot_download(
            repo_id=DEFAULT_PACK_REPO,
            repo_type="model",
            allow_patterns=[
                "t3_pt_pt.safetensors",
                "s3gen_v3.pt",
                "s3gen_v3.safetensors",
                "grapheme_mtl_merged_expanded_v1.json",
            ],
        )
    )

    map_location = torch.device("cpu") if device in ("cpu", "mps") else None

    ve = VoiceEncoder()
    ve.load_state_dict(
        torch.load(base_dir / "ve.pt", map_location=map_location, weights_only=True)
    )
    ve.to(device).eval()

    t3 = T3(T3Config.multilingual())
    t3_state = load_safetensors(str(pack_dir / "t3_pt_pt.safetensors"))
    if "model" in t3_state:
        t3_state = t3_state["model"][0]
    t3.load_state_dict(t3_state)
    t3.to(device).eval()

    s3gen = S3Gen()
    s3_candidates = [
        pack_dir / "s3gen_v3.safetensors",
        pack_dir / "s3gen_v3.pt",
        base_dir / "s3gen.pt",
    ]
    s3_path = next((p for p in s3_candidates if p.is_file()), None)
    if s3_path is None:
        raise FileNotFoundError("Não encontrei s3gen_v3 nem s3gen.pt")
    s3_state = _load_s3gen_state(s3_path, map_location)
    missing = s3gen.load_state_dict(s3_state, strict=False)
    bad = [
        k
        for k in getattr(missing, "missing_keys", [])
        if k not in ("tokenizer._mel_filters", "tokenizer.window")
    ]
    if bad:
        raise RuntimeError(f"S3Gen incompleto ({s3_path.name}): missing={bad[:5]}")
    s3gen.to(device).eval()

    tok_path = pack_dir / "grapheme_mtl_merged_expanded_v1.json"
    if not tok_path.is_file():
        tok_path = base_dir / "grapheme_mtl_merged_expanded_v1.json"
    tokenizer = MTLTokenizer(str(tok_path))

    conds = None
    if (base_dir / "conds.pt").exists():
        conds = Conditionals.load(base_dir / "conds.pt", map_location=map_location).to(
            device
        )

    print(f"[RIC TTS] Pack pt-PT carregado (S3Gen={s3_path.name}).", flush=True)
    return ChatterboxMultilingualTTS(t3, s3gen, ve, tokenizer, device, conds=conds)


class ChatterboxEngine:
    """Chatterbox com referência pt-PT (pack Portugal se estiver em cache)."""

    def __init__(
        self,
        *,
        device: str = "auto",
        t3_model: str = DEFAULT_T3_MODEL,
        language_id: str = DEFAULT_LANGUAGE_ID,
        audio_prompt: Path | None = None,
        exaggeration: float = 0.5,
        data_dir: Path | None = None,
        use_pt_pt_pack: bool = True,
    ) -> None:
        self.device_pref = device
        self.t3_model = (t3_model or DEFAULT_T3_MODEL).strip().lower()
        self.language_id = (language_id or DEFAULT_LANGUAGE_ID).strip().lower() or "pt"
        self.audio_prompt = audio_prompt
        self.exaggeration = float(exaggeration)
        self.data_dir = data_dir
        self.use_pt_pt_pack = use_pt_pt_pack and self.t3_model in (
            "pt-pt",
            "pt_pt",
            "ptpt",
            "v3",
            "pack",
        )
        self._model = None
        self._device: str | None = None
        self._resolved_prompt: Path | None = None
        self._lock = threading.Lock()
        self.last_error: str | None = None

    @property
    def available(self) -> bool:
        return chatterbox_importable()

    def warm_up(self) -> None:
        with self._lock:
            self._ensure()

    def _resolve_prompt(self) -> Path:
        if self.audio_prompt is not None and self.audio_prompt.is_file():
            return self.audio_prompt
        return ensure_pt_pt_reference(data_dir=self.data_dir)

    def _ensure(self):
        if self._model is not None:
            return self._model
        if not chatterbox_importable():
            raise RuntimeError(
                "Pacote chatterbox-tts não instalado. "
                "Corre: python -m pip install -r requirements-chatterbox.txt"
            )

        device = resolve_device(self.device_pref)
        self._device = device
        prompt = self._resolve_prompt()
        self._resolved_prompt = prompt
        self.audio_prompt = prompt

        model = None
        if self.use_pt_pt_pack and pt_pt_pack_cached():
            print(f"[RIC TTS] A carregar Chatterbox pack pt-PT em {device}…", flush=True)
            try:
                model = load_pt_pt_pack(device)
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[RIC TTS] Pack pt-PT falhou ({exc}). "
                    "Fallback: base + referência Portugal.",
                    flush=True,
                )
        elif self.use_pt_pt_pack:
            print(
                "[RIC TTS] Pack pt-PT ainda não está no cache. "
                "A usar base + referência Portugal.",
                flush=True,
            )

        if model is None:
            import inspect

            from chatterbox.mtl_tts import ChatterboxMultilingualTTS

            print(
                f"[RIC TTS] A carregar Chatterbox base + ref pt-PT em {device}…",
                flush=True,
            )
            kwargs: dict = {"device": device}
            try:
                params = inspect.signature(
                    ChatterboxMultilingualTTS.from_pretrained
                ).parameters
                if "t3_model" in params and self.t3_model not in (
                    "pt-pt",
                    "pt_pt",
                    "ptpt",
                    "pack",
                ):
                    kwargs["t3_model"] = self.t3_model
            except (TypeError, ValueError):
                pass
            model = ChatterboxMultilingualTTS.from_pretrained(**kwargs)

        model.prepare_conditionals(str(prompt), exaggeration=self.exaggeration)
        print(f"[RIC TTS] Referência de voz (Portugal): {prompt}", flush=True)
        self._model = model
        return model

    def synthesize_file(self, texto: str, out_path: Path) -> bool:
        text = (texto or "").strip()
        if not text:
            return False
        try:
            with self._lock:
                model = self._ensure()
                prompt = self._resolved_prompt or self._resolve_prompt()
                wav = model.generate(
                    text,
                    language_id=self.language_id,
                    audio_prompt_path=str(prompt),
                    exaggeration=self.exaggeration,
                )
                sr = int(getattr(model, "sr", 24000))
            samples = wav.detach().cpu().numpy() if hasattr(wav, "detach") else wav
            ok = _write_wav_mono(out_path, samples, sr)
            self.last_error = None if ok else "falha a gravar WAV"
            return ok
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            msg = str(exc)
            print(f"[RIC TTS] Chatterbox falhou: {msg}", flush=True)
            if "LlamaModel" in msg or "torchvision::nms" in msg:
                print(
                    "[RIC TTS] Dica: torch/torchvision desalinhados. Reinstala:\n"
                    "  python -m pip install --force-reinstall "
                    "torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 "
                    "--index-url https://download.pytorch.org/whl/cpu",
                    flush=True,
                )
            return False

    def status(self) -> dict:
        return {
            "available": self.available,
            "loaded": self._model is not None,
            "device": self._device or resolve_device(self.device_pref),
            "t3_model": self.t3_model,
            "language_id": self.language_id,
            "pack": DEFAULT_PACK_REPO if self.use_pt_pt_pack else DEFAULT_BASE_REPO,
            "audio_prompt": str(self._resolved_prompt or self.audio_prompt)
            if (self._resolved_prompt or self.audio_prompt)
            else None,
            "last_error": self.last_error,
            "repo_hint": DEFAULT_PACK_REPO,
        }
