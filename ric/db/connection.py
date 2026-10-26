from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS lembretes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    tipo TEXT NOT NULL,
    critico INTEGER NOT NULL DEFAULT 0,
    hora TEXT NOT NULL,
    diario INTEGER NOT NULL DEFAULT 1,
    estado TEXT NOT NULL DEFAULT 'pendente',
    proximo_em TEXT NOT NULL,
    criado_por TEXT NOT NULL DEFAULT 'idoso',
    avisos_feitos INTEGER NOT NULL DEFAULT 0,
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS confirmacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lembrete_id INTEGER,
    titulo TEXT NOT NULL,
    acao TEXT NOT NULL,
    em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS perfil (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
