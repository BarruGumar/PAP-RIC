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
        # Permitir "extras/foo.onnx" relativo a ric-data/vozes
        candidates = [
            path,
            settings.data_dir / "vozes" / path,
            settings.data_dir / path,
            Path(__file__).resolve().parent.parent / path,
        ]
        path = next((p for p in candidates if p.is_file()), path)
    return path if path.is_file() else None


_TUNE_SAMPLES = (
    "Atenção, é a hora de beber água.",
    "Olá, eu sou o RIC.",
    "Não te esqueças do teu lembrete.",
    "Boa noite, descansa bem.",
)


def _cmd_tune(settings: Settings, model_arg: str | None) -> int:
    """Sessão para ouvir e afinar o TTS (não é STT)."""
    model = _resolve_model(settings, model_arg)
    if model is None:
        print("Modelo não encontrado. Corre: py -m ric voices")
        return 1
    speed = settings.piper_length_scale
    voice = VoiceService(
        piper_model=model,
        cache_dir=settings.data_dir / "tts",
        length_scale=speed,
    )
    print("=== RIC tune — ouvir TTS ===")
    print(f"Modelo: {model.name}")
    print(f"Ritmo actual (length_scale): {speed}")
    print(
        "Comandos: Enter=amostras  |  texto=falar  |  + / - = ritmo  |  "
        "s 1.35 = ritmo exacto  |  q = sair"
    )
    print("Para gravar o ritmo na UI: mete RIC_PIPER_LENGTH_SCALE=… no .env\n")
    sample_i = 0
    while True:
        try:
            raw = input(f"tune[{voice.length_scale:.2f}]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nA sair.")
            return 0
        if raw.lower() in ("q", "quit", "sair"):
            print(
                f"Último ritmo: {voice.length_scale:.2f}  "
                f"(env: RIC_PIPER_LENGTH_SCALE={voice.length_scale:.2f})"
            )
            return 0
        if raw in ("+", "++"):
            voice.set_length_scale(voice.length_scale + 0.05)
            print(f"Mais lento → {voice.length_scale:.2f}")
            continue
        if raw in ("-", "--"):
            voice.set_length_scale(voice.length_scale - 0.05)
            print(f"Mais rápido → {voice.length_scale:.2f}")
            continue
        if raw.lower().startswith("s ") or raw.lower().startswith("speed "):
            try:
                parts = raw.split(None, 1)
                value = float(parts[1])
            except (IndexError, ValueError):
                print("Usa: s 1.35")
                continue
            voice.set_length_scale(value)
            print(f"Ritmo → {voice.length_scale:.2f}")
            continue
        if not raw:
            frase = _TUNE_SAMPLES[sample_i % len(_TUNE_SAMPLES)]
            sample_i += 1
            print(f"» {frase}")
            voice.speak(frase, async_=False, with_beep=False)
            continue
        print(f"» {raw}")
        voice.speak(raw, async_=False, with_beep=False)


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
        "--model",
        help="Caminho .onnx (ex.: extras/outra.onnx). Sem isto usa o default.",
    )
    p_say.add_argument(
        "--speed",
        type=float,
        default=None,
        help="length_scale Piper (ex.: 1.2 rápido, 1.45 lento). Default: .env",
    )
    p_say.add_argument(
        "--loop",
        type=int,
        default=1,
        help="Repetir N vezes (para ouvir e afinar).",
    )

    p_tune = sub.add_parser(
        "tune",
        help="Ouvir TTS em sessão interactiva (afinar ritmo/frases)",
    )
    p_tune.add_argument(
        "--model",
        help="Caminho .onnx opcional (ex.: extras/tugao-quality.onnx)",
    )

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
                mark = " [DEFAULT]" if default and onnx.resolve() == default.resolve() else ""
                where = "extras" if "extras" in onnx.parts else folder.name
                print(f"  ({where}) {onnx.name}{mark}")
                print(f"           {onnx}")
        print("\nTestar sem alterar o default:")
        print('  py -m ric say "Atenção, é a hora de beber água."')
        print('  py -m ric say "Olá" --model extras/OUTRA.onnx')
        return 0

    if args.cmd == "say":
        model = _resolve_model(settings, getattr(args, "model", None))
        if model is None:
            print("Modelo não encontrado. Corre: py -m ric voices")
            return 1
        speed = (
            args.speed
            if args.speed is not None
            else settings.piper_length_scale
        )
        print(f"A usar: {model}  (length_scale={speed})")
        voice = VoiceService(
            piper_model=model,
            cache_dir=settings.data_dir / "tts",
            length_scale=speed,
        )
        loops = max(1, int(args.loop))
        ok = True
        for i in range(loops):
            if loops > 1:
                print(f"  [{i + 1}/{loops}]")
            ok = voice.speak(args.texto, async_=False, with_beep=False) and ok
        print("OK" if ok else "Falhou (Piper/SAPI).")
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
