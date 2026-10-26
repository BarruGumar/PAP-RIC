from __future__ import annotations

from datetime import datetime, timedelta

from ric.config import Settings
from ric.db.connection import Database
from ric.reminders.models import ESTADOS_ATIVOS, TIPOS_VALIDOS, Reminder


class ReminderPermissionError(PermissionError):
    """Criação de lembrete crítico/medicamento sem cuidador autenticado."""


class ReminderService:
    def __init__(self, db: Database, settings: Settings) -> None:
        self._db = db
        self._settings = settings

    def create(
        self,
        *,
        titulo: str,
        hora: str,
        tipo: str = "tarefa",
        critico: bool = False,
        diario: bool = True,
        criado_por: str = "idoso",
        caregiver_authenticated: bool = False,
        agora: datetime | None = None,
    ) -> Reminder:
        proximo = self._next_for_time(hora, agora)
        return self.create_at(
            titulo=titulo,
            proximo=proximo,
            tipo=tipo,
            critico=critico,
            diario=diario,
            criado_por=criado_por,
            caregiver_authenticated=caregiver_authenticated,
            hora=hora,
        )

    def create_at(
        self,
        *,
        titulo: str,
        proximo: datetime,
        tipo: str = "tarefa",
        critico: bool = False,
        diario: bool = True,
        criado_por: str = "idoso",
        caregiver_authenticated: bool = False,
        hora: str | None = None,
    ) -> Reminder:
        tipo = tipo.lower().strip()
        if tipo not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido. Usa: {', '.join(TIPOS_VALIDOS)}")
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("O título não pode estar vazio.")

        needs_caregiver = critico or tipo == "medicamento"
        if needs_caregiver and not caregiver_authenticated:
            raise ReminderPermissionError(
                "Lembretes de medicação/críticos só o cuidador pode criar (PIN)."
            )

        if proximo.tzinfo is not None:
            proximo = proximo.replace(tzinfo=None)
        agora = datetime.now()
        hora_val = hora or proximo.strftime("%H:%M")
        criado = agora.isoformat(timespec="seconds")
        criado_por = "cuidador" if caregiver_authenticated else criado_por

        with self._db.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO lembretes (
                    titulo, tipo, critico, hora, diario, estado,
                    proximo_em, criado_por, avisos_feitos, criado_em
                ) VALUES (?, ?, ?, ?, ?, 'pendente', ?, ?, 0, ?)
                """,
                (
                    titulo,
                    tipo,
                    1 if (critico or tipo == "medicamento") else 0,
                    hora_val,
                    1 if diario else 0,
                    proximo.isoformat(timespec="seconds"),
                    criado_por,
                    criado,
                ),
            )
            conn.commit()
            row_id = int(cur.lastrowid)
        return self.get(row_id)

    def get(self, reminder_id: int) -> Reminder:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM lembretes WHERE id = ?", (reminder_id,)
            ).fetchone()
        if row is None:
            raise LookupError(f"Lembrete #{reminder_id} não encontrado.")
        return self._row(row)

    def list_all(self) -> list[Reminder]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM lembretes ORDER BY proximo_em ASC, id ASC"
            ).fetchall()
        return [self._row(r) for r in rows]

    def list_active(self) -> list[Reminder]:
        placeholders = ",".join("?" * len(ESTADOS_ATIVOS))
        with self._db.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM lembretes
                WHERE estado IN ({placeholders})
                ORDER BY proximo_em ASC, id ASC
                """,
                ESTADOS_ATIVOS,
            ).fetchall()
        return [self._row(r) for r in rows]

    def next_pending(self) -> Reminder | None:
        active = self.list_active()
        return active[0] if active else None

    def due_now(self, agora: datetime | None = None) -> list[Reminder]:
        agora = agora or datetime.now()
        with self._db.connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM lembretes
                WHERE estado IN ('pendente', 'adiado', 'disparado')
                  AND proximo_em <= ?
                ORDER BY proximo_em ASC, id ASC
                """,
                (agora.isoformat(timespec="seconds"),),
            ).fetchall()
        return [self._row(r) for r in rows]

    def mark_fired(self, reminder_id: int) -> Reminder:
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE lembretes SET estado = 'disparado' WHERE id = ?",
                (reminder_id,),
            )
            conn.commit()
        return self.get(reminder_id)

    def register_alert(self, reminder_id: int) -> Reminder:
        item = self.get(reminder_id)
        avisos = item.avisos_feitos + 1
        max_alerts = self._settings.reminder_max_alerts
        if avisos >= max_alerts:
            estado = "expirado"
        else:
            estado = "disparado"
            retry = datetime.now() + timedelta(
                minutes=self._settings.reminder_retry_minutes
            )
            with self._db.connect() as conn:
                conn.execute(
                    """
                    UPDATE lembretes
                    SET avisos_feitos = ?, estado = ?, proximo_em = ?
                    WHERE id = ?
                    """,
                    (
                        avisos,
                        estado,
                        retry.isoformat(timespec="seconds"),
                        reminder_id,
                    ),
                )
                conn.commit()
            return self.get(reminder_id)

        with self._db.connect() as conn:
            conn.execute(
                """
                UPDATE lembretes
                SET avisos_feitos = ?, estado = ?
                WHERE id = ?
                """,
                (avisos, estado, reminder_id),
            )
            conn.commit()
        return self.get(reminder_id)

    def confirm(self, reminder_id: int) -> Reminder:
        item = self.get(reminder_id)
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE lembretes SET estado = 'confirmado' WHERE id = ?",
                (reminder_id,),
            )
            conn.execute(
                """
                INSERT INTO confirmacoes (lembrete_id, titulo, acao, em)
                VALUES (?, ?, 'confirmar', ?)
                """,
                (
                    reminder_id,
                    item.titulo,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            conn.commit()
        return self.get(reminder_id)

    def snooze(self, reminder_id: int, minutes: int = 10) -> Reminder:
        if minutes < 1:
            raise ValueError("Os minutos de adiamento têm de ser >= 1.")
        item = self.get(reminder_id)
        novo = datetime.now() + timedelta(minutes=minutes)
        with self._db.connect() as conn:
            conn.execute(
                """
                UPDATE lembretes
                SET estado = 'adiado', proximo_em = ?
                WHERE id = ?
                """,
                (novo.isoformat(timespec="seconds"), reminder_id),
            )
            conn.execute(
                """
                INSERT INTO confirmacoes (lembrete_id, titulo, acao, em)
                VALUES (?, ?, 'adiar', ?)
                """,
                (
                    reminder_id,
                    item.titulo,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            conn.commit()
        return self.get(reminder_id)

    @staticmethod
    def _next_for_time(hora: str, agora: datetime | None = None) -> datetime:
        agora = agora or datetime.now()
        try:
            h, m = map(int, hora.split(":"))
        except ValueError as exc:
            raise ValueError("Hora inválida. Usa HH:MM.") from exc
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Hora inválida. Usa HH:MM.")
        alvo = agora.replace(hour=h, minute=m, second=0, microsecond=0)
        if alvo <= agora:
            alvo += timedelta(days=1)
        return alvo

    @staticmethod
    def _row(row) -> Reminder:
        return Reminder(
            id=int(row["id"]),
            titulo=row["titulo"],
            tipo=row["tipo"],
            critico=bool(row["critico"]),
            hora=row["hora"],
            diario=bool(row["diario"]),
            estado=row["estado"],
            proximo_em=row["proximo_em"],
            criado_por=row["criado_por"],
            avisos_feitos=int(row["avisos_feitos"]),
            criado_em=row["criado_em"],
        )
