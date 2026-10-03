from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timedelta

from ric import __version__
from ric import db


def _fmt(lembrete: db.Lembrete) -> str:
    return (
        f"#{lembrete.id:>3}  {lembrete.hora}  [{lembrete.tipo}]  "
        f"{lembrete.titulo}  ({lembrete.estado})  -> {lembrete.proximo_em}"
    )


def cmd_demo(_: argparse.Namespace) -> int:
    db.limpar_tudo()
    agora = datetime.now()
    em_1_min = (agora + timedelta(minutes=1)).strftime("%H:%M")
    amostras = [
        ("Tomar medicamento", em_1_min, "medicamento"),
        ("Consulta no centro de saúde", "10:30", "consulta"),
        ("Beber água", "16:00", "tarefa"),
    ]
    print("RIC demo - a criar 3 lembretes de exemplo...\n")
    criados = []
    for titulo, hora, tipo in amostras:
        item = db.adicionar(titulo, hora, tipo)
        criados.append(item)
        print("  +", _fmt(item))
    primeiro = criados[0].id
    print("\nComandos uteis:")
    print("  py -m ric list")
    print("  py -m ric run")
    print(f"  py -m ric ok {primeiro}")
    print(f"  py -m ric adiar {primeiro}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    try:
        item = db.adicionar(args.titulo, args.hora, args.tipo)
    except ValueError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    print("Lembrete criado:")
    print(" ", _fmt(item))
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    itens = db.listar()
    if not itens:
        print('Sem lembretes. Usa: py -m ric add "Titulo" HH:MM')
        return 0
    print(f"Lembretes ({len(itens)}):\n")
    for item in itens:
        print(" ", _fmt(item))
    return 0


def cmd_ok(args: argparse.Namespace) -> int:
    try:
        item = db.confirmar(args.id)
    except LookupError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    print("Confirmado:")
    print(" ", _fmt(item))
    return 0


def cmd_adiar(args: argparse.Namespace) -> int:
    try:
        item = db.adiar(args.id, args.minutos)
    except (LookupError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    print(f"Adiado {args.minutos} min:")
    print(" ", _fmt(item))
    return 0


def _alerta(lembrete: db.Lembrete) -> None:
    print("\n" + "=" * 50)
    print("  RIC - LEMBRETE")
    print(f"  {lembrete.titulo}")
    print(f"  Tipo: {lembrete.tipo}  |  Hora prevista: {lembrete.hora}")
    print(f"  Confirmar:  py -m ric ok {lembrete.id}")
    print(f"  Adiar:      py -m ric adiar {lembrete.id}")
    print("=" * 50 + "\n")
    try:
        import winsound

        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:
        print("\a", end="", flush=True)


def cmd_run(args: argparse.Namespace) -> int:
    db.init_db()
    print(f"RIC a vigiar lembretes (intervalo {args.intervalo}s). Ctrl+C para sair.")
    avisados: set[int] = set()
    try:
        while True:
            for item in db.devidos():
                if item.id in avisados and item.estado == "disparado":
                    continue
                db.marcar_disparado(item.id)
                avisados.add(item.id)
                _alerta(item)
            # Se foi confirmado ou adiado noutro terminal, limpar cache local
            atuais = {i.id for i in db.listar(incluir_confirmados=False)}
            avisados &= atuais
            for item in db.listar(incluir_confirmados=False):
                if item.estado == "adiado" and item.id in avisados:
                    # permite novo alerta após adiar
                    if item.proximo_em > datetime.now().isoformat(timespec="seconds"):
                        avisados.discard(item.id)
            time.sleep(args.intervalo)
    except KeyboardInterrupt:
        print("\nRIC parado.")
        return 0


def cmd_ui(args: argparse.Namespace) -> int:
    from ric.web_server import servir

    servir(host=args.host, port=args.port, abrir_browser=not args.sem_browser)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ric",
        description="RIC — lembretes locais (offline, SQLite).",
    )
    parser.add_argument("--version", action="version", version=f"ric {__version__}")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_demo = sub.add_parser("demo", help="Cria lembretes de exemplo")
    p_demo.set_defaults(func=cmd_demo)

    p_add = sub.add_parser("add", help="Adiciona um lembrete")
    p_add.add_argument("titulo", help='Ex.: "Tomar medicamento"')
    p_add.add_argument("hora", help="HH:MM")
    p_add.add_argument(
        "--tipo",
        default="tarefa",
        choices=db.TIPOS_VALIDOS,
        help="Tipo do lembrete",
    )
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="Lista lembretes")
    p_list.set_defaults(func=cmd_list)

    p_ok = sub.add_parser("ok", help="Confirma um lembrete (já fiz)")
    p_ok.add_argument("id", type=int)
    p_ok.set_defaults(func=cmd_ok)

    p_adiar = sub.add_parser("adiar", help="Adia um lembrete")
    p_adiar.add_argument("id", type=int)
    p_adiar.add_argument("--minutos", type=int, default=10)
    p_adiar.set_defaults(func=cmd_adiar)

    p_run = sub.add_parser("run", help="Vigia e dispara lembretes devidos")
    p_run.add_argument("--intervalo", type=int, default=5, help="Segundos entre verificações")
    p_run.set_defaults(func=cmd_run)

    p_ui = sub.add_parser("ui", help="Abre a interface web local de lembretes")
    p_ui.add_argument("--host", default="127.0.0.1")
    p_ui.add_argument("--port", type=int, default=8787)
    p_ui.add_argument(
        "--sem-browser",
        action="store_true",
        help="Não abrir o browser automaticamente",
    )
    p_ui.set_defaults(func=cmd_ui)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
