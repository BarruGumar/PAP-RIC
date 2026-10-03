from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "ric.db"

TIPOS_VALIDOS = ("medicamento", "consulta", "tarefa", "outro")


@dataclass
class Lembrete:
    id: int
    titulo: str
    hora: str  # HH:MM
    tipo: str
    estado: str  # pendente | disparado | confirmado | adiado
    proximo_em: str  # ISO datetime
    criado_em: str


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lembretes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                hora TEXT NOT NULL,
                tipo TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'pendente',
                proximo_em TEXT NOT NULL,
                criado_em TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _proximo_para_hora(hora: str, agora: datetime | None = None) -> datetime:
    agora = agora or datetime.now()
    try:
        h, m = map(int, hora.split(":"))
    except ValueError as exc:
        raise ValueError("Hora inválida. Usa o formato HH:MM (ex.: 18:00).") from exc
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError("Hora inválida. Usa o formato HH:MM (ex.: 18:00).")
    alvo = agora.replace(hour=h, minute=m, second=0, microsecond=0)
    if alvo <= agora:
        alvo += timedelta(days=1)
    return alvo


def adicionar(titulo: str, hora: str, tipo: str = "tarefa") -> Lembrete:
    tipo = tipo.lower().strip()
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f"Tipo inválido. Usa um de: {', '.join(TIPOS_VALIDOS)}")
    titulo = titulo.strip()
    if not titulo:
        raise ValueError("O título não pode estar vazio.")

    agora = datetime.now()
    proximo = _proximo_para_hora(hora, agora)
    criado = agora.isoformat(timespec="seconds")

    init_db()
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO lembretes (titulo, hora, tipo, estado, proximo_em, criado_em)
            VALUES (?, ?, ?, 'pendente', ?, ?)
            """,
            (titulo, f"{int(hora.split(':')[0]):02d}:{int(hora.split(':')[1]):02d}", tipo, proximo.isoformat(timespec="seconds"), criado),
        )
        conn.commit()
        row_id = int(cur.lastrowid)
    return obter(row_id)


def listar(incluir_confirmados: bool = True) -> list[Lembrete]:
    init_db()
    with _connect() as conn:
        if incluir_confirmados:
            rows = conn.execute(
                "SELECT * FROM lembretes ORDER BY proximo_em ASC, id ASC"
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM lembretes
                WHERE estado != 'confirmado'
                ORDER BY proximo_em ASC, id ASC
                """
            ).fetchall()
    return [_row_to_lembrete(r) for r in rows]


def obter(lembrete_id: int) -> Lembrete:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM lembretes WHERE id = ?", (lembrete_id,)
        ).fetchone()
    if row is None:
        raise LookupError(f"Lembrete #{lembrete_id} não encontrado.")
    return _row_to_lembrete(row)


def confirmar(lembrete_id: int) -> Lembrete:
    obter(lembrete_id)
    with _connect() as conn:
        conn.execute(
            "UPDATE lembretes SET estado = 'confirmado' WHERE id = ?",
            (lembrete_id,),
        )
        conn.commit()
    return obter(lembrete_id)


def adiar(lembrete_id: int, minutos: int = 10) -> Lembrete:
    if minutos < 1:
        raise ValueError("Os minutos de adiamento têm de ser >= 1.")
    obter(lembrete_id)
    novo = datetime.now() + timedelta(minutes=minutos)
    with _connect() as conn:
        conn.execute(
            """
            UPDATE lembretes
            SET estado = 'adiado', proximo_em = ?
            WHERE id = ?
            """,
            (novo.isoformat(timespec="seconds"), lembrete_id),
        )
        conn.commit()
    return obter(lembrete_id)


def marcar_disparado(lembrete_id: int) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE lembretes SET estado = 'disparado' WHERE id = ?",
            (lembrete_id,),
        )
        conn.commit()


def devidos(agora: datetime | None = None) -> list[Lembrete]:
    agora = agora or datetime.now()
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM lembretes
            WHERE estado IN ('pendente', 'adiado', 'disparado')
              AND proximo_em <= ?
            ORDER BY proximo_em ASC, id ASC
            """,
            (agora.isoformat(timespec="seconds"),),
        ).fetchall()
    return [_row_to_lembrete(r) for r in rows]


def limpar_tudo() -> None:
    init_db()
    with _connect() as conn:
        conn.execute("DELETE FROM lembretes")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'lembretes'")
        conn.commit()


def _row_to_lembrete(row: sqlite3.Row) -> Lembrete:
    return Lembrete(
        id=row["id"],
        titulo=row["titulo"],
        hora=row["hora"],
        tipo=row["tipo"],
        estado=row["estado"],
        proximo_em=row["proximo_em"],
        criado_em=row["criado_em"],
    )
