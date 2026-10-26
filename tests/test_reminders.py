"""Unit tests — reminders schema A + regra 2A (crítico só com cuidador)."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from ric.config import Settings
from ric.db.connection import Database
from ric.reminders.service import ReminderService, ReminderPermissionError


@pytest.fixture()
def service(tmp_path: Path) -> ReminderService:
    settings = Settings(
        data_dir=tmp_path,
        reminder_max_alerts=3,
        reminder_retry_minutes=2,
    )
    db = Database(settings.db_path)
    db.init_schema()
    return ReminderService(db, settings)


def test_create_non_critical_ok(service: ReminderService) -> None:
    item = service.create(
        titulo="Beber água",
        hora="18:00",
        tipo="tarefa",
        critico=False,
        criado_por="idoso",
        caregiver_authenticated=False,
    )
    assert item.id >= 1
    assert item.titulo == "Beber água"
    assert item.critico is False
    assert item.estado == "pendente"
    assert item.criado_por == "idoso"


def test_create_medicamento_without_caregiver_blocked(service: ReminderService) -> None:
    with pytest.raises(ReminderPermissionError):
        service.create(
            titulo="Medicamento manhã",
            hora="09:00",
            tipo="medicamento",
            critico=True,
            criado_por="idoso",
            caregiver_authenticated=False,
        )


def test_create_critico_flag_without_caregiver_blocked(service: ReminderService) -> None:
    with pytest.raises(ReminderPermissionError):
        service.create(
            titulo="Consulta importante",
            hora="10:00",
            tipo="consulta",
            critico=True,
            criado_por="idoso",
            caregiver_authenticated=False,
        )


def test_create_medicamento_with_caregiver_ok(service: ReminderService) -> None:
    item = service.create(
        titulo="Medicamento manhã",
        hora="09:00",
        tipo="medicamento",
        critico=True,
        criado_por="cuidador",
        caregiver_authenticated=True,
    )
    assert item.critico is True
    assert item.tipo == "medicamento"


def test_list_and_next(service: ReminderService) -> None:
    service.create(titulo="A", hora="08:00", tipo="tarefa")
    service.create(titulo="B", hora="20:00", tipo="tarefa")
    items = service.list_active()
    assert len(items) == 2
    nxt = service.next_pending()
    assert nxt is not None


def test_confirm_and_snooze(service: ReminderService) -> None:
    soon = datetime.now() + timedelta(seconds=2)
    item = service.create_at(
        titulo="Teste",
        proximo=soon,
        tipo="tarefa",
    )
    service.mark_fired(item.id)
    confirmed = service.confirm(item.id)
    assert confirmed.estado == "confirmado"

    item2 = service.create_at(
        titulo="Adiar",
        proximo=datetime.now() + timedelta(seconds=2),
        tipo="tarefa",
    )
    service.mark_fired(item2.id)
    snoozed = service.snooze(item2.id, minutes=10)
    assert snoozed.estado == "adiado"
    assert datetime.fromisoformat(snoozed.proximo_em) > datetime.now()


def test_due_and_expire_after_max_alerts(service: ReminderService) -> None:
    past = datetime.now() - timedelta(minutes=1)
    item = service.create_at(titulo="Vencido", proximo=past, tipo="tarefa")
    due = service.due_now()
    assert any(d.id == item.id for d in due)

    for _ in range(3):
        service.register_alert(item.id)
    expired = service.get(item.id)
    assert expired.estado == "expirado"
    assert expired.avisos_feitos == 3
