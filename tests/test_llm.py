"""Unit — cliente LLM Ollama com backend injectável."""

from __future__ import annotations

from pathlib import Path

from ric.config import Settings
from ric.db.connection import Database
from ric.llm.prompt import needs_reminder_tools
from ric.llm.service import LlmService
from ric.reminders.service import ReminderService


def _reminders(tmp_path: Path) -> ReminderService:
    settings = Settings(data_dir=tmp_path)
    db = Database(settings.db_path)
    db.init_schema()
    return ReminderService(db, settings)


def test_chat_returns_model_text() -> None:
    llm = LlmService(
        reminders=None,
        chat_fn=lambda _messages, _tools: {
            "message": {"role": "assistant", "content": "Olá, eu sou o Ric."}
        },
    )
    assert llm.available is True
    reply = llm.chat("Olá")
    assert reply == "Olá, eu sou o Ric."


def test_greeting_skips_tools() -> None:
    seen: list[object] = []

    def chat_fn(messages, tools):
        seen.append(tools)
        return {"message": {"role": "assistant", "content": "Olá!"}}

    llm = LlmService(reminders=None, chat_fn=chat_fn)
    assert llm.chat("Olá Ric") == "Olá!"
    assert seen == [None]


def test_listar_lembretes_tool(tmp_path: Path) -> None:
    svc = _reminders(tmp_path)
    svc.create(titulo="Água", hora="15:00", tipo="tarefa")
    seen_tools: list[object] = []

    def chat_fn(messages, tools):
        seen_tools.append(tools)
        # 1.ª chamada: tool call; 2.ª: resposta final
        user_turns = [m for m in messages if m.get("role") == "tool"]
        if not user_turns:
            return {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "1",
                            "type": "function",
                            "function": {"name": "listar_lembretes", "arguments": {}},
                        }
                    ],
                }
            }
        return {
            "message": {
                "role": "assistant",
                "content": "Tens um lembrete: Água às 15:00.",
            }
        }

    llm = LlmService(reminders=svc, chat_fn=chat_fn)
    reply = llm.chat("Quais são os meus lembretes?")
    assert "Água" in reply
    assert seen_tools[0] is not None


def test_criar_lembrete_tool_persists(tmp_path: Path) -> None:
    svc = _reminders(tmp_path)
    changed: list[dict] = []

    def chat_fn(messages, tools):
        user_turns = [m for m in messages if m.get("role") == "tool"]
        if not user_turns:
            return {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "1",
                            "type": "function",
                            "function": {
                                "name": "criar_lembrete",
                                "arguments": {
                                    "titulo": "Beber água",
                                    "hora": "18:30",
                                    "tipo": "tarefa",
                                },
                            },
                        }
                    ],
                }
            }
        return {
            "message": {
                "role": "assistant",
                "content": "Pronto, lembro-te de beber água às 18:30.",
            }
        }

    llm = LlmService(
        reminders=svc,
        chat_fn=chat_fn,
        on_reminders_changed=lambda item: changed.append(item),
    )
    reply = llm.chat("Cria um lembrete para beber água às 18:30")
    assert "18:30" in reply
    items = svc.list_all()
    assert len(items) == 1
    assert items[0].titulo == "Beber água"
    assert items[0].hora == "18:30"
    assert changed and changed[0]["titulo"] == "Beber água"


def test_criar_lembrete_rejects_medicamento(tmp_path: Path) -> None:
    svc = _reminders(tmp_path)

    def chat_fn(messages, tools):
        user_turns = [m for m in messages if m.get("role") == "tool"]
        if not user_turns:
            return {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "1",
                            "type": "function",
                            "function": {
                                "name": "criar_lembrete",
                                "arguments": {
                                    "titulo": "Comprimido",
                                    "hora": "09:00",
                                    "tipo": "medicamento",
                                },
                            },
                        }
                    ],
                }
            }
        tool_body = user_turns[0].get("content") or ""
        return {
            "message": {
                "role": "assistant",
                "content": (
                    "Medicação só o cuidador pode criar."
                    if "erro" in tool_body
                    else "ok"
                ),
            }
        }

    llm = LlmService(reminders=svc, chat_fn=chat_fn)
    reply = llm.chat("Cria lembrete de medicamento às 09:00")
    assert "cuidador" in reply.lower()
    assert svc.list_all() == []


def test_apagar_lembrete_tool_by_titulo(tmp_path: Path) -> None:
    svc = _reminders(tmp_path)
    svc.create(titulo="Beber água", hora="18:30", tipo="tarefa")
    changed: list[dict] = []

    def chat_fn(messages, tools):
        user_turns = [m for m in messages if m.get("role") == "tool"]
        if not user_turns:
            return {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "1",
                            "type": "function",
                            "function": {
                                "name": "apagar_lembrete",
                                "arguments": {"titulo": "beber água"},
                            },
                        }
                    ],
                }
            }
        return {
            "message": {
                "role": "assistant",
                "content": "Pronto, apaguei o lembrete de beber água.",
            }
        }

    llm = LlmService(
        reminders=svc,
        chat_fn=chat_fn,
        on_reminders_changed=lambda item: changed.append(item),
    )
    reply = llm.chat("Apaga o lembrete de beber água")
    assert "apaguei" in reply.lower() or "água" in reply.lower()
    assert svc.list_all() == []
    assert changed and changed[0]["titulo"] == "Beber água"


def test_apagar_lembrete_rejects_medicamento(tmp_path: Path) -> None:
    svc = _reminders(tmp_path)
    med = svc.create(
        titulo="Comprimido",
        hora="09:00",
        tipo="medicamento",
        caregiver_authenticated=True,
    )

    def chat_fn(messages, tools):
        user_turns = [m for m in messages if m.get("role") == "tool"]
        if not user_turns:
            return {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "1",
                            "type": "function",
                            "function": {
                                "name": "apagar_lembrete",
                                "arguments": {"id": med.id},
                            },
                        }
                    ],
                }
            }
        tool_body = user_turns[0].get("content") or ""
        return {
            "message": {
                "role": "assistant",
                "content": (
                    "Medicação só o cuidador pode apagar."
                    if "erro" in tool_body
                    else "ok"
                ),
            }
        }

    llm = LlmService(reminders=svc, chat_fn=chat_fn)
    reply = llm.chat("Apaga o comprimido")
    assert "cuidador" in reply.lower()
    assert svc.get(med.id).titulo == "Comprimido"


def test_needs_reminder_tools_hints() -> None:
    assert needs_reminder_tools("Quais são os meus lembretes?") is True
    assert needs_reminder_tools("Cria um lembrete para beber água") is True
    assert needs_reminder_tools("Lembra-me de passear às 17:00") is True
    assert needs_reminder_tools("Apaga o lembrete da água") is True
    assert needs_reminder_tools("Olá Ric") is False


def test_unavailable_returns_fallback() -> None:
    llm = LlmService(
        reminders=None,
        chat_fn=None,
        auto_probe=False,
    )
    assert llm.available is False
    reply = llm.chat("Olá")
    assert "lembretes continuam" in reply.lower() or "desculpa" in reply.lower()


def test_status_keys() -> None:
    llm = LlmService(
        reminders=None,
        chat_fn=lambda _m, _t: {"message": {"role": "assistant", "content": "ok"}},
    )
    status = llm.status()
    assert "available" in status
    assert "model" in status
