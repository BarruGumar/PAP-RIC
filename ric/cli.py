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
        print(f"A usar: {model}")
        voice = VoiceService(
            piper_model=model,
            cache_dir=settings.data_dir / "tts",
            length_scale=settings.piper_length_scale,
        )
        ok = voice.speak(args.texto, async_=False, with_beep=False)
        print("OK" if ok else "Falhou (Piper/SAPI).")
        return 0 if ok else 1

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
