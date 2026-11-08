"""Unit — cliente LLM Ollama com backend injectável."""

from __future__ import annotations

from pathlib import Path

from ric.config import Settings
from ric.db.connection import Database
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


def test_listar_lembretes_tool(tmp_path: Path) -> None:
    svc = _reminders(tmp_path)
    svc.create(titulo="Água", hora="15:00", tipo="tarefa")

    def chat_fn(messages, tools):
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
