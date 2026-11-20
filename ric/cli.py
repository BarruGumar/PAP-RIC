from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

from ric.config import Settings
from ric.db.connection import Database
from ric.reminders.service import ReminderPermissionError, ReminderService
from ric.voice.tts import VoiceService
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


def _make_voice(
    settings: Settings,
    *,
    model_arg: str | None = None,
    speed: float | None = None,
) -> VoiceService:
    model = _resolve_model(settings, model_arg)
    return VoiceService(
        piper_model=model,
        cache_dir=settings.data_dir / "tts",
        length_scale=speed if speed is not None else settings.piper_length_scale,
        engine="piper",
    )


_TUNE_SAMPLES = (
    "Atenção, é a hora de beber água.",
    "Olá, eu sou o RIC.",
    "Não te esqueças do teu lembrete.",
    "Boa noite, descansa bem.",
)


def _cmd_tune(settings: Settings, model_arg: str | None) -> int:
    model = _resolve_model(settings, model_arg)
    if model is None:
        print("Modelo não encontrado. Corre: py -m ric voices")
        return 1
    voice = _make_voice(settings, model_arg=model_arg)
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

    p_say = sub.add_parser("say", help="Testar TTS Piper")
    p_say.add_argument("texto")
    p_say.add_argument("--model", help="Caminho .onnx Piper")
    p_say.add_argument("--speed", type=float, default=None, help="length_scale Piper")
    p_say.add_argument("--loop", type=int, default=1)

    p_tune = sub.add_parser("tune", help="Ouvir TTS Piper em sessão interactiva")
    p_tune.add_argument("--model", help="Caminho .onnx opcional")

    sub.add_parser(
        "wake-setup",
        help="Descarregar modelos openWakeWord (hey_jarvis temporário)",
    )

    p_wake_install = sub.add_parser(
        "wake-install",
        help="Instalar ONNX «ei RIC» em ric-data/wake/ric.onnx",
    )
    p_wake_install.add_argument(
        "onnx",
        help="Caminho do .onnx treinado (ex.: Downloads\\ei_ric.onnx)",
    )

    args = parser.parse_args(argv)
    settings = Settings.from_env()

    if args.cmd == "ui":
        run_server()
        return 0

    if args.cmd == "wake-setup":
        wake_dir = settings.data_dir / "wake"
        wake_dir.mkdir(parents=True, exist_ok=True)
        readme = wake_dir / "README.txt"
        if not readme.is_file():
            readme.write_text(
                "Modelos wake-word do RIC.\n"
                "- Por agora: built-in temporário hey_jarvis (openWakeWord).\n"
                "- Alvo: py -m ric wake-install … → ric.onnx («ei RIC»).\n"
                "- Roteiro: docs/ROTEIRO-WAKE-EI-RIC.md\n"
                "- Env: RIC_WAKE_MODEL, RIC_WAKE_THRESHOLD, RIC_WAKE_ENABLED.\n",
                encoding="utf-8",
            )
        try:
            from ric.voice.oww_detector import ensure_wake_models_downloaded

            print("A descarregar modelos openWakeWord…")
            ensure_wake_models_downloaded()
        except ImportError:
            print("Instala deps: py -m pip install openwakeword sounddevice numpy")
            return 1
        except Exception as exc:  # noqa: BLE001
            print(f"Falha no download: {exc}")
            return 1
        print(f"OK. Pasta: {wake_dir}")
        print("Teste: diz «hey jarvis» com py -m ric ui (ou usa o botão Falar).")
        print("Quando tiveres o modelo «ei RIC»: docs/ROTEIRO-WAKE-EI-RIC.md")
        return 0

    if args.cmd == "wake-install":
        from ric.voice.oww_detector import install_wake_model

        try:
            dest = install_wake_model(Path(args.onnx), data_dir=settings.data_dir)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            print(f"Erro: {exc}")
            return 1
        print(f"OK. Modelo «ei RIC» em: {dest}")
        print("Teste: py -m ric ui  →  diz «ei RIC»")
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
        print("  py -m ric tune")
        print(f"\nMotor TTS: Piper")
        return 0

    if args.cmd == "say":
        model = _resolve_model(settings, getattr(args, "model", None))
        if model is None:
            print("Modelo Piper não encontrado. Corre: py -m ric voices")
            return 1
        print(
            f"A usar Piper: {model}  "
            f"(length_scale={args.speed or settings.piper_length_scale})"
        )
        voice = _make_voice(
            settings,
            model_arg=getattr(args, "model", None),
            speed=args.speed,
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
