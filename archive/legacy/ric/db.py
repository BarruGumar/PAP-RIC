from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "ric.db"

TIPOS_VALIDOS = ("medicamento", "consulta", "tarefa", "outro")
CHAT_MAX_MENSAGENS = 80
CHAT_RESUMO_APOS = 40


@dataclass
class Lembrete:
    id: int
    titulo: str
    hora: str  # HH:MM
    tipo: str
    estado: str  # pendente | disparado | confirmado | adiado
    proximo_em: str  # ISO datetime
    criado_em: str


@dataclass
class MensagemChat:
    id: int
    role: str
    conteudo: str
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS perfil (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL,
                atualizado_em TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                criado_em TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS confirmacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lembrete_id INTEGER,
                titulo TEXT NOT NULL,
                acao TEXT NOT NULL,
                em TEXT NOT NULL
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


def adicionar_em(titulo: str, proximo: datetime, tipo: str = "tarefa") -> Lembrete:
    """Cria lembrete com instante absoluto (útil para 'daqui X minutos')."""
    tipo = tipo.lower().strip()
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f"Tipo inválido. Usa um de: {', '.join(TIPOS_VALIDOS)}")
    titulo = titulo.strip()
    if not titulo:
        raise ValueError("O título não pode estar vazio.")
    if proximo.tzinfo is not None:
        proximo = proximo.replace(tzinfo=None)

    agora = datetime.now()
    if proximo <= agora:
        raise ValueError("O momento do lembrete já passou. Indica um tempo futuro.")

    hora = proximo.strftime("%H:%M")
    criado = agora.isoformat(timespec="seconds")

    init_db()
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO lembretes (titulo, hora, tipo, estado, proximo_em, criado_em)
            VALUES (?, ?, ?, 'pendente', ?, ?)
            """,
            (
                titulo,
                hora,
                tipo,
                proximo.isoformat(timespec="seconds"),
                criado,
            ),
        )
        conn.commit()
        row_id = int(cur.lastrowid)
    return obter(row_id)


def adicionar(titulo: str, hora: str, tipo: str = "tarefa") -> Lembrete:
    agora = datetime.now()
    proximo = _proximo_para_hora(hora, agora)
    return adicionar_em(titulo, proximo, tipo)


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


def _registar_confirmacao(lembrete_id: int, titulo: str, acao: str) -> None:
    agora = datetime.now().isoformat(timespec="seconds")
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO confirmacoes (lembrete_id, titulo, acao, em)
            VALUES (?, ?, ?, ?)
            """,
            (lembrete_id, titulo, acao, agora),
        )
        conn.commit()


def confirmar(lembrete_id: int) -> Lembrete:
    item = obter(lembrete_id)
    with _connect() as conn:
        conn.execute(
            "UPDATE lembretes SET estado = 'confirmado' WHERE id = ?",
            (lembrete_id,),
        )
        conn.commit()
    _registar_confirmacao(lembrete_id, item.titulo, "confirmar")
    return obter(lembrete_id)


def adiar(lembrete_id: int, minutos: int = 10) -> Lembrete:
    if minutos < 1:
        raise ValueError("Os minutos de adiamento têm de ser >= 1.")
    item = obter(lembrete_id)
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
    _registar_confirmacao(lembrete_id, item.titulo, "adiar")
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


# --- Perfil (preferências) ---


def guardar_preferencia(chave: str, valor: str) -> dict[str, str]:
    chave = (chave or "").strip().lower().replace(" ", "_")
    valor = (valor or "").strip()
    if not chave:
        raise ValueError("A chave da preferência não pode estar vazia.")
    if not valor:
        raise ValueError("O valor da preferência não pode estar vazio.")
    if len(chave) > 64:
        raise ValueError("Chave demasiado longa.")
    if len(valor) > 500:
        raise ValueError("Valor demasiado longo.")
    agora = datetime.now().isoformat(timespec="seconds")
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO perfil (chave, valor, atualizado_em)
            VALUES (?, ?, ?)
            ON CONFLICT(chave) DO UPDATE SET
                valor = excluded.valor,
                atualizado_em = excluded.atualizado_em
            """,
            (chave, valor, agora),
        )
        conn.commit()
    return {"chave": chave, "valor": valor, "atualizado_em": agora}


def obter_preferencia(chave: str) -> str | None:
    chave = (chave or "").strip().lower().replace(" ", "_")
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT valor FROM perfil WHERE chave = ?", (chave,)
        ).fetchone()
    return None if row is None else str(row["valor"])


def obter_perfil() -> dict[str, str]:
    init_db()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT chave, valor FROM perfil ORDER BY chave ASC"
        ).fetchall()
    return {str(r["chave"]): str(r["valor"]) for r in rows}


def perfil_texto() -> str:
    perfil = obter_perfil()
    if not perfil:
        return "Perfil: (ainda sem preferências guardadas)"
    linhas = [f"- {k}: {v}" for k, v in perfil.items()]
    return "Perfil da pessoa:\n" + "\n".join(linhas)


# --- Memória de conversa ---


def adicionar_mensagem(role: str, conteudo: str) -> MensagemChat:
    role = (role or "").strip()
    conteudo = (conteudo or "").strip()
    if role not in ("user", "assistant", "system_resumo"):
        raise ValueError("role inválido.")
    if not conteudo:
        raise ValueError("Mensagem vazia.")
    agora = datetime.now().isoformat(timespec="seconds")
    init_db()
    with _connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO conversas (role, conteudo, criado_em)
            VALUES (?, ?, ?)
            """,
            (role, conteudo[:4000], agora),
        )
        conn.commit()
        row_id = int(cur.lastrowid)
    _podar_conversas()
    return MensagemChat(id=row_id, role=role, conteudo=conteudo[:4000], criado_em=agora)


def listar_mensagens(limite: int = 40) -> list[MensagemChat]:
    init_db()
    limite = max(1, min(int(limite), CHAT_MAX_MENSAGENS))
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM (
                SELECT * FROM conversas
                ORDER BY id DESC
                LIMIT ?
            ) ORDER BY id ASC
            """,
            (limite,),
        ).fetchall()
    return [
        MensagemChat(
            id=int(r["id"]),
            role=str(r["role"]),
            conteudo=str(r["conteudo"]),
            criado_em=str(r["criado_em"]),
        )
        for r in rows
    ]


def limpar_conversas() -> None:
    init_db()
    with _connect() as conn:
        conn.execute("DELETE FROM conversas")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'conversas'")
        conn.commit()


def _podar_conversas() -> None:
    """Mantém as últimas N mensagens; se crescer muito, deixa um resumo curto."""
    with _connect() as conn:
        total = conn.execute("SELECT COUNT(*) AS n FROM conversas").fetchone()["n"]
        if total <= CHAT_MAX_MENSAGENS:
            return
        # Guarda um resumo simples das mensagens antigas antes de apagar
        antigas = conn.execute(
            """
            SELECT role, conteudo FROM conversas
            ORDER BY id ASC
            LIMIT ?
            """,
            (CHAT_RESUMO_APOS,),
        ).fetchall()
        trechos = []
        for r in antigas:
            if r["role"] == "system_resumo":
                continue
            trechos.append(f"{r['role']}: {str(r['conteudo'])[:80]}")
        resumo = "Resumo anterior: " + " | ".join(trechos[:8])
        cutoff = conn.execute(
            """
            SELECT id FROM conversas
            ORDER BY id DESC
            LIMIT 1 OFFSET ?
            """,
            (CHAT_MAX_MENSAGENS - 2,),
        ).fetchone()
        if cutoff:
            conn.execute("DELETE FROM conversas WHERE id <= ?", (int(cutoff["id"]),))
        agora = datetime.now().isoformat(timespec="seconds")
        conn.execute(
            """
            INSERT INTO conversas (role, conteudo, criado_em)
            VALUES ('system_resumo', ?, ?)
            """,
            (resumo[:2000], agora),
        )
        conn.commit()


def historico_para_llm(limite: int = 10) -> list[dict[str, str]]:
    msgs = listar_mensagens(limite=limite + 5)
    out: list[dict[str, str]] = []
    for m in msgs:
        if m.role == "system_resumo":
            out.append({"role": "assistant", "content": f"(memória) {m.conteudo}"})
        elif m.role in ("user", "assistant"):
            out.append({"role": m.role, "content": m.conteudo})
    return out[-limite:]
