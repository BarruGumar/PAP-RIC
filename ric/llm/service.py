"""Serviço LLM: chat Ollama + tools P1 (ler lembretes)."""

from __future__ import annotations

import json
from typing import Any, Callable

from ric.llm.client import OllamaError, ollama_alive, ollama_chat
from ric.llm.prompt import FALLBACK_REPLY, SYSTEM_PROMPT, TOOLS
from ric.reminders.service import ReminderService

ChatFn = Callable[[list[dict[str, Any]], list[dict[str, Any]] | None], dict[str, Any]]


class LlmUnavailableError(RuntimeError):
    """Ollama / modelo indisponível."""


class LlmService:
    def __init__(
        self,
        *,
        reminders: ReminderService | None,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5:3b",
        timeout: float = 10.0,
        chat_fn: ChatFn | None = None,
        auto_probe: bool = True,
        max_tool_rounds: int = 3,
    ) -> None:
        self.reminders = reminders
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.max_tool_rounds = max_tool_rounds
        self._chat_fn = chat_fn
        self._probed_ok: bool | None = None
        if chat_fn is not None:
            self._probed_ok = True
        elif auto_probe:
            self._probed_ok = ollama_alive(base_url)
        else:
            self._probed_ok = False

    @property
    def available(self) -> bool:
        if self._chat_fn is not None:
            return True
        if self._probed_ok is None:
            self._probed_ok = ollama_alive(self.base_url, timeout=1.0)
        return self._probed_ok is True

    def status(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "model": self.model,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "engine": "mock" if self._chat_fn is not None else "ollama",
        }

    def chat(self, user_text: str) -> str:
        text = (user_text or "").strip()
        if not text:
            return "Não percebi. Podes repetir?"
        if not self.available:
            return FALLBACK_REPLY

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
        try:
            for _ in range(self.max_tool_rounds):
                raw = self._call_chat(messages, TOOLS)
                message = raw.get("message") or {}
                tool_calls = message.get("tool_calls") or []
                content = (message.get("content") or "").strip()
                if tool_calls:
                    messages.append(message)
                    for call in tool_calls:
                        result = self._run_tool(call)
                        messages.append(
                            {
                                "role": "tool",
                                "name": _tool_name(call),
                                "content": result,
                            }
                        )
                    continue
                if content:
                    return content
                break
        except LlmUnavailableError:
            self._probed_ok = False
            return FALLBACK_REPLY
        except OllamaError:
            # Timeout / rede: re-probe na próxima vez (não silenciar para sempre)
            self._probed_ok = None
            return FALLBACK_REPLY
        except Exception:  # noqa: BLE001
            return FALLBACK_REPLY
        return FALLBACK_REPLY

    def _call_chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        if self._chat_fn is not None:
            return self._chat_fn(messages, tools)
        return ollama_chat(
            base_url=self.base_url,
            model=self.model,
            messages=messages,
            tools=tools,
            timeout=self.timeout,
        )

    def _run_tool(self, call: dict[str, Any]) -> str:
        name = _tool_name(call)
        args = _tool_args(call)
        if name == "listar_lembretes":
            return self._tool_listar()
        if name == "proximo_lembrete":
            return self._tool_proximo()
        return json.dumps({"erro": f"Ferramenta desconhecida: {name}"}, ensure_ascii=False)

    def _tool_listar(self) -> str:
        if self.reminders is None:
            return json.dumps({"lembretes": []}, ensure_ascii=False)
        items = [
            {
                "id": r.id,
                "titulo": r.titulo,
                "hora": r.hora,
                "tipo": r.tipo,
                "estado": r.estado,
            }
            for r in self.reminders.list_all()
        ]
        return json.dumps({"lembretes": items}, ensure_ascii=False)

    def _tool_proximo(self) -> str:
        if self.reminders is None:
            return json.dumps({"proximo": None}, ensure_ascii=False)
        nxt = self.reminders.next_pending()
        if nxt is None:
            return json.dumps({"proximo": None}, ensure_ascii=False)
        return json.dumps(
            {
                "proximo": {
                    "id": nxt.id,
                    "titulo": nxt.titulo,
                    "hora": nxt.hora,
                    "tipo": nxt.tipo,
                }
            },
            ensure_ascii=False,
        )


def _tool_name(call: dict[str, Any]) -> str:
    fn = call.get("function") or {}
    return str(fn.get("name") or call.get("name") or "")


def _tool_args(call: dict[str, Any]) -> dict[str, Any]:
    fn = call.get("function") or {}
    raw = fn.get("arguments", call.get("arguments", {}))
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}
