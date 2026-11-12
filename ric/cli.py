from __future__ import annotations

import argparse
import time
import wave
from datetime import datetime, timedelta
from pathlib import Path

from ric.config import Settings
from ric.db.connection import Database
from ric.reminders.service import ReminderPermissionError, ReminderService
from ric.voice.chatterbox_engine import chatterbox_importable
from ric.voice.tts import VoiceService, normalize_tts_engine
from ric.web.server import run_server


def _service() -> ReminderService:
    settings = Settings.from_env()
    db = Database(settings.db_path)
    db.init_schema()
    return ReminderService(db, settings)


def _voice_dirs(settings: Settings) -> list[Path]:
    root = Path(__file__).resolve().parent.parent
    return [
        settings.data_dir / "vozes",
        settings.data_dir / "vozes" / "extras",
        root / "voz-teste" / "vozes",
    ]


def _resolve_model(settings: Settings, model_arg: str | None) -> Path | None:
    if not model_arg:
        return settings.piper_model
    path = Path(model_arg)
    if not path.is_absolute():
        candidates = [
            path,
            settings.data_dir / "vozes" / path,
            settings.data_dir / path,
            Path(__file__).resolve().parent.parent / path,
        ]
        path = next((p for p in candidates if p.is_file()), path)
    return path if path.is_file() else None


def _resolve_prompt(settings: Settings, prompt_arg: str | None) -> Path | None:
    raw = (prompt_arg or "").strip()
    if not raw:
        return settings.chatterbox_audio_prompt
    path = Path(raw)
    if not path.is_absolute():
        root = Path(__file__).resolve().parent.parent
        candidates = [
            path,
            settings.data_dir / "vozes" / path,
            settings.data_dir / "vozes" / "extras" / path,
            settings.data_dir / path,
            root / path,
        ]
        path = next((p for p in candidates if p.is_file()), path)
    return path if path.is_file() else None


def _make_voice(
    settings: Settings,
    *,
    engine: str = "piper",
    model_arg: str | None = None,
    speed: float | None = None,
    prompt_arg: str | None = None,
) -> VoiceService:
    model = _resolve_model(settings, model_arg)
    prompt = _resolve_prompt(settings, prompt_arg)
    return VoiceService(
        piper_model=model,
        cache_dir=settings.data_dir / "tts",
        length_scale=speed if speed is not None else settings.piper_length_scale,
        engine=normalize_tts_engine(engine),
        chatterbox_device=settings.chatterbox_device,
        chatterbox_audio_prompt=prompt,
        chatterbox_t3_model=settings.chatterbox_t3_model,
    )


_TUNE_SAMPLES = (
    "Atenção, é a hora de beber água.",
    "Olá, eu sou o RIC.",
    "Não te esqueças do teu lembrete.",
    "Boa noite, descansa bem.",
)


def _cmd_record_ref(settings: Settings, *, seconds: float, out_arg: str | None) -> int:
    try:
        import numpy as np
        import sounddevice as sd
    except Exception as exc:  # noqa: BLE001
        print(f"Falta sounddevice/numpy para gravar: {exc}")
        return 1

    duration = max(5.0, float(seconds))
    out = (
        Path(out_arg)
        if out_arg
        else settings.data_dir / "vozes" / "extras" / "referencia-pt.wav"
    )
    if not out.is_absolute():
        out = (Path(__file__).resolve().parent.parent / out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    rate = 24000
    print("=== RIC record-ref — voz de referência (zero-shot) ===")
    print(f"Vai gravar {duration:.0f}s → {out}")
    print("Fala em pt-PT. A gravar em 2 s…")
    time.sleep(2.0)
    print("GRAVAR — fala agora!")
    audio = sd.rec(int(duration * rate), samplerate=rate, channels=1, dtype="float32")
    sd.wait()
    pcm = (np.clip(audio.reshape(-1), -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(str(out), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(rate)
        wav_file.writeframes(pcm.tobytes())
    print(f"OK: {out}")
    print(f'  py -m ric say "Olá" --engine chatterbox --prompt "{out}"')
    return 0


def _cmd_tune(settings: Settings, model_arg: str | None) -> int:
    model = _resolve_model(settings, model_arg)
    if model is None:
        print("Modelo não encontrado. Corre: py -m ric voices")
        return 1
    voice = _make_voice(settings, engine="piper", model_arg=model_arg)
    print("=== RIC tune — ouvir TTS Piper ===")
    print(f"Modelo: {model.name}")
    print(f"Ritmo actual (length_scale): {voice.length_scale}")
    print("Comandos: Enter=amostras | texto | + / - | s 1.35 | q\n")
    sample_i = 0
    while True:
        try:
            raw = input(f"tune[{voice.length_scale:.2f}]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nA sair.")
            return 0
        if raw.lower() in ("q", "quit", "sair"):
            return 0
        if raw in ("+", "++"):
            voice.set_length_scale(voice.length_scale + 0.05)
            continue
        if raw in ("-", "--"):
            voice.set_length_scale(voice.length_scale - 0.05)
            continue
        if raw.lower().startswith("s ") or raw.lower().startswith("speed "):
            try:
                voice.set_length_scale(float(raw.split(None, 1)[1]))
            except (IndexError, ValueError):
                print("Usa: s 1.35")
            continue
        frase = raw or _TUNE_SAMPLES[sample_i % len(_TUNE_SAMPLES)]
        if not raw:
            sample_i += 1
        print(f"» {frase}")
        voice.speak(frase, async_=False, with_beep=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ric", description="RIC — companheiro PAP")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ui", help="Arranca UI + API em http://127.0.0.1:8787")

    p_add = sub.add_parser("add", help="Criar lembrete não-crítico")
    p_add.add_argument("titulo")
    p_add.add_argument("hora", help="HH:MM")
    p_add.add_argument("--tipo", default="tarefa")

    p_soon = sub.add_parser("soon", help="Lembrete daqui a N minutos (teste)")
    p_soon.add_argument("titulo")
    p_soon.add_argument("minutos", type=int)

    sub.add_parser("list", help="Listar lembretes")
    sub.add_parser("voices", help="Listar vozes Piper (default + extras)")

    p_say = sub.add_parser("say", help="Testar TTS sem mudar o default da UI")
    p_say.add_argument("texto")
    p_say.add_argument(
        "--engine",
        choices=("piper", "chatterbox"),
        default=None,
        help="Motor TTS: piper (default) ou chatterbox (experimental pt-PT)",
    )
    p_say.add_argument(
        "--prompt",
        help="WAV de referência Chatterbox (ex.: extras/pt_pt_ref.wav)",
    )
    p_say.add_argument("--model", help="Caminho .onnx Piper")
    p_say.add_argument("--speed", type=float, default=None, help="length_scale Piper")
    p_say.add_argument("--loop", type=int, default=1)

    p_cmp = sub.add_parser(
        "tts-compare",
        help="Gerar a mesma frase com Piper e Chatterbox (A/B)",
    )
    p_cmp.add_argument(
        "texto",
        nargs="?",
        default="Atenção, é a hora de beber água.",
    )
    p_cmp.add_argument("--prompt", help="WAV de referência para Chatterbox")
    p_cmp.add_argument("--play", action="store_true")

    p_rec = sub.add_parser(
        "record-ref",
        help="Gravar WAV de referência (>5 s) para clonagem zero-shot",
    )
    p_rec.add_argument("--seconds", type=float, default=8.0)
    p_rec.add_argument("--out", default=None)

    p_tune = sub.add_parser("tune", help="Ouvir TTS Piper em sessão interactiva")
    p_tune.add_argument("--model", help="Caminho .onnx opcional")

    args = parser.parse_args(argv)
    settings = Settings.from_env()

    if args.cmd == "ui":
        run_server()
        return 0

    if args.cmd == "voices":
        default = settings.piper_model
        print("Default actual:")
        print(f"  {default if default else '(nenhum modelo encontrado)'}")
        print("\nModelos encontrados:")
        seen: set[Path] = set()
        for folder in _voice_dirs(settings):
            if not folder.is_dir():
                continue
            for onnx in sorted(folder.glob("*.onnx")):
                if onnx.resolve() in seen:
                    continue
                seen.add(onnx.resolve())
                mark = (
                    " [DEFAULT]"
                    if default and onnx.resolve() == default.resolve()
                    else ""
                )
                where = "extras" if "extras" in onnx.parts else folder.name
                print(f"  ({where}) {onnx.name}{mark}")
                print(f"           {onnx}")
        print("\nTestar:")
        print('  py -m ric say "Olá"')
        print('  py -m ric say "Olá" --engine chatterbox')
        print("  py -m ric tts-compare --play")
        print(
            f"\nChatterbox instalado: "
            f"{'sim' if chatterbox_importable() else 'não (requirements-chatterbox.txt)'}"
        )
        print(f"Motor UI (.env RIC_TTS_ENGINE): {settings.tts_engine}")
        return 0

    if args.cmd == "record-ref":
        return _cmd_record_ref(
            settings,
            seconds=float(getattr(args, "seconds", 8.0)),
            out_arg=getattr(args, "out", None),
        )

    if args.cmd == "say":
        engine = normalize_tts_engine(
            getattr(args, "engine", None) or settings.tts_engine
        )
        prompt_arg = getattr(args, "prompt", None)
        if engine == "piper":
            model = _resolve_model(settings, getattr(args, "model", None))
            if model is None:
                print("Modelo Piper não encontrado. Corre: py -m ric voices")
                return 1
            print(
                f"A usar Piper: {model}  "
                f"(length_scale={args.speed or settings.piper_length_scale})"
            )
        else:
            if not chatterbox_importable():
                print(
                    "Chatterbox não instalado. "
                    "Corre: python -m pip install -r requirements-chatterbox.txt"
                )
                return 1
            prompt = _resolve_prompt(settings, prompt_arg)
            if prompt_arg and prompt is None:
                print(f"WAV de referência não encontrado: {prompt_arg}")
                return 1
            print(
                f"A usar Chatterbox experimental "
                f"(device={settings.chatterbox_device}, t3={settings.chatterbox_t3_model})"
            )
            print(
                f"  prompt: {prompt if prompt else '(auto: amostra oficial pt-PT)'}"
            )
        voice = _make_voice(
            settings,
            engine=engine,
            model_arg=getattr(args, "model", None),
            speed=args.speed,
            prompt_arg=prompt_arg,
        )
        loops = max(1, int(args.loop))
        ok = True
        for i in range(loops):
            if loops > 1:
                print(f"  [{i + 1}/{loops}]")
            wav = voice.synthesize_alert(args.texto, stem="say")
            if wav is None:
                ok = False
                continue
            print(f"  WAV: {wav}")
            from ric.voice.tts import _play_wav

            ok = _play_wav(wav) and ok
        print("OK" if ok else "Falhou.")
        return 0 if ok else 1

    if args.cmd == "tts-compare":
        out_dir = settings.data_dir / "tts" / "compare"
        out_dir.mkdir(parents=True, exist_ok=True)
        frase = args.texto
        prompt_arg = getattr(args, "prompt", None)
        if prompt_arg and _resolve_prompt(settings, prompt_arg) is None:
            print(f"WAV de referência não encontrado: {prompt_arg}")
            return 1
        print("=== RIC TTS A/B — Piper vs Chatterbox ===")
        print(f"Frase: {frase}\n")
        voice = _make_voice(settings, engine="piper", prompt_arg=prompt_arg)
        results: dict[str, Path | None] = {}
        timings: dict[str, float] = {}

        t0 = time.perf_counter()
        piper_wav = voice.synthesize_alert(frase, stem="compare", engine="piper")
        timings["piper"] = time.perf_counter() - t0
        if piper_wav is not None:
            dest = out_dir / f"piper-{piper_wav.name}"
            dest.write_bytes(piper_wav.read_bytes())
            results["piper"] = dest
        else:
            results["piper"] = None

        if not chatterbox_importable():
            print("Chatterbox não instalado — só gerei Piper.")
        else:
            t1 = time.perf_counter()
            cb_wav = voice.synthesize_alert(frase, stem="compare", engine="chatterbox")
            timings["chatterbox"] = time.perf_counter() - t1
            if cb_wav is not None:
                dest = out_dir / f"chatterbox-{cb_wav.name}"
                dest.write_bytes(cb_wav.read_bytes())
                results["chatterbox"] = dest
            else:
                results["chatterbox"] = None

        for name, path in results.items():
            sec = timings.get(name)
            timing = f"  ({sec:.1f}s)" if sec is not None else ""
            print(f"  {name}: {path if path else 'FALHOU'}{timing}")

        if getattr(args, "play", False):
            from ric.voice.tts import _play_wav

            for name in ("piper", "chatterbox"):
                path = results.get(name)
                if path is not None:
                    print(f"A tocar {name}…")
                    _play_wav(path)
        return 0 if results.get("piper") is not None else 1

    if args.cmd == "tune":
        return _cmd_tune(settings, getattr(args, "model", None))

    svc = _service()
    try:
        if args.cmd == "add":
            item = svc.create(titulo=args.titulo, hora=args.hora, tipo=args.tipo)
            print(f"Criado #{item.id}: {item.titulo} às {item.hora}")
            return 0
        if args.cmd == "soon":
            proximo = datetime.now() + timedelta(minutes=args.minutos)
            item = svc.create_at(titulo=args.titulo, proximo=proximo, tipo="tarefa")
            print(f"Criado #{item.id}: {item.titulo} em {item.proximo_em}")
            return 0
        if args.cmd == "list":
            for item in svc.list_all():
                flag = "!" if item.critico else " "
                print(
                    f"{flag}#{item.id} [{item.estado}] {item.titulo} "
                    f"{item.hora} → {item.proximo_em}"
                )
            return 0
    except ReminderPermissionError as exc:
        print(f"Erro: {exc}")
        return 2
    except (ValueError, LookupError) as exc:
        print(f"Erro: {exc}")
        return 1
    return 1
