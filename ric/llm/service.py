"""Serviço LLM: chat Ollama + tools P1 (ler/criar lembretes não médicos)."""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from ric.llm.client import OllamaError, ollama_alive, ollama_chat
from ric.llm.prompt import (
    FALLBACK_REPLY,
    SYSTEM_PROMPT,
    TOOLS,
    needs_reminder_tools,
)
from ric.reminders.service import ReminderPermissionError, ReminderService

ChatFn = Callable[[list[dict[str, Any]], list[dict[str, Any]] | None], dict[str, Any]]
RemindersChangedFn = Callable[[dict[str, Any]], None]

_ALLOWED_CREATE_TIPOS = frozenset({"tarefa", "consulta", "outro"})


def _log(msg: str) -> None:
    print(f"[RIC] {msg}", flush=True)


class LlmUnavailableError(RuntimeError):
    """Ollama / modelo indisponível."""


class LlmService:
    def __init__(
        self,
        *,
        reminders: ReminderService | None,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5:3b",
        timeout: float = 90.0,
        chat_fn: ChatFn | None = None,
        auto_probe: bool = True,
        max_tool_rounds: int = 3,
        on_reminders_changed: RemindersChangedFn | None = None,
    ) -> None:
        self.reminders = reminders
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.max_tool_rounds = max_tool_rounds
        self.on_reminders_changed = on_reminders_changed
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

    def warm_up(self) -> None:
        """Aquecer o modelo (evita 1.º turno de ~50s no CPU)."""
        if self._chat_fn is not None or not self.available:
            return
        try:
            ollama_chat(
                base_url=self.base_url,
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": "diz só ok"},
                ],
                tools=None,
                timeout=self.timeout,
            )
            self._probed_ok = True
            _log(f"LLM aquecido ({self.model})")
        except Exception as exc:  # noqa: BLE001
            _log(f"LLM warm-up falhou: {exc}")
            self._probed_ok = None

    def chat(self, user_text: str) -> str:
        text = (user_text or "").strip()
        if not text:
            return "Não percebi. Podes repetir?"
        if not self.available:
            _log("LLM indisponível — a usar fallback")
            return FALLBACK_REPLY

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ]
        tools = TOOLS if needs_reminder_tools(text) else None
        try:
            for _ in range(self.max_tool_rounds):
                raw = self._call_chat(messages, tools)
                message = raw.get("message") or {}
                tool_calls = message.get("tool_calls") or []
                content = (message.get("content") or "").strip()
                if tool_calls and tools:
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
        except LlmUnavailableError as exc:
            _log(f"LLM unavailable: {exc}")
            self._probed_ok = False
            return FALLBACK_REPLY
        except OllamaError as exc:
            # Timeout / rede: re-probe na próxima vez (não silenciar para sempre)
            _log(f"LLM OllamaError: {exc}")
            self._probed_ok = None
            return FALLBACK_REPLY
        except Exception as exc:  # noqa: BLE001
            _log(f"LLM erro inesperado: {exc}")
            return FALLBACK_REPLY
        _log("LLM sem conteúdo útil — fallback")
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
        if name == "criar_lembrete":
            return self._tool_criar(args)
        if name == "apagar_lembrete":
            return self._tool_apagar(args)
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

    def _tool_criar(self, args: dict[str, Any]) -> str:
        if self.reminders is None:
            return json.dumps(
                {"erro": "Serviço de lembretes indisponível."},
                ensure_ascii=False,
            )
        titulo = str(args.get("titulo") or "").strip()
        hora = _normalize_hora(str(args.get("hora") or ""))
        tipo = str(args.get("tipo") or "tarefa").strip().lower() or "tarefa"
        if not titulo:
            return json.dumps({"erro": "Falta o título do lembrete."}, ensure_ascii=False)
        if not hora:
            return json.dumps(
                {"erro": "Falta a hora. Usa HH:MM (ex.: 18:30)."},
                ensure_ascii=False,
            )
        if tipo == "medicamento" or tipo not in _ALLOWED_CREATE_TIPOS:
            return json.dumps(
                {
                    "erro": (
                        "Medicação e lembretes críticos só o cuidador pode criar. "
                        "Usa tipo tarefa, consulta ou outro."
                    )
                },
                ensure_ascii=False,
            )
        try:
            item = self.reminders.create(
                titulo=titulo,
                hora=hora,
                tipo=tipo,
                critico=False,
                criado_por="voz",
                caregiver_authenticated=False,
            )
        except ReminderPermissionError as exc:
            return json.dumps({"erro": str(exc)}, ensure_ascii=False)
        except ValueError as exc:
            return json.dumps({"erro": str(exc)}, ensure_ascii=False)
        payload = {
            "ok": True,
            "lembrete": {
                "id": item.id,
                "titulo": item.titulo,
                "hora": item.hora,
                "tipo": item.tipo,
                "proximo_em": item.proximo_em,
            },
        }
        if self.on_reminders_changed is not None:
            try:
                self.on_reminders_changed(item.to_dict())
            except Exception as exc:  # noqa: BLE001
                _log(f"on_reminders_changed falhou: {exc}")
        _log(f"lembrete criado via voz: #{item.id} {item.titulo!r} {item.hora}")
        return json.dumps(payload, ensure_ascii=False)

    def _tool_apagar(self, args: dict[str, Any]) -> str:
        if self.reminders is None:
            return json.dumps(
                {"erro": "Serviço de lembretes indisponível."},
                ensure_ascii=False,
            )
        raw_id = args.get("id")
        titulo = str(args.get("titulo") or "").strip()
        reminder_id: int | None = None
        if raw_id is not None and str(raw_id).strip() != "":
            try:
                reminder_id = int(raw_id)
            except (TypeError, ValueError):
                return json.dumps({"erro": "ID de lembrete inválido."}, ensure_ascii=False)

        if reminder_id is None and not titulo:
            return json.dumps(
                {"erro": "Indica o id ou o título do lembrete a apagar."},
                ensure_ascii=False,
            )

        if reminder_id is None:
            matches = self.reminders.find_by_titulo(titulo)
            if not matches:
                return json.dumps(
                    {"erro": f"Não encontrei lembrete com «{titulo}»."},
                    ensure_ascii=False,
                )
            if len(matches) > 1:
                opcoes = [
                    {"id": r.id, "titulo": r.titulo, "hora": r.hora, "tipo": r.tipo}
                    for r in matches
                ]
                return json.dumps(
                    {
                        "erro": "Há vários lembretes parecidos. Diz o id ou a hora.",
                        "opcoes": opcoes,
                    },
                    ensure_ascii=False,
                )
            reminder_id = matches[0].id

        try:
            item = self.reminders.delete(
                reminder_id,
                caregiver_authenticated=False,
            )
        except ReminderPermissionError as exc:
            return json.dumps({"erro": str(exc)}, ensure_ascii=False)
        except LookupError as exc:
            return json.dumps({"erro": str(exc)}, ensure_ascii=False)

        payload = {
            "ok": True,
            "apagado": {
                "id": item.id,
                "titulo": item.titulo,
                "hora": item.hora,
                "tipo": item.tipo,
            },
        }
        if self.on_reminders_changed is not None:
            try:
                self.on_reminders_changed(item.to_dict())
            except Exception as exc:  # noqa: BLE001
                _log(f"on_reminders_changed falhou: {exc}")
        _log(f"lembrete apagado via voz: #{item.id} {item.titulo!r}")
        return json.dumps(payload, ensure_ascii=False)


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


def _normalize_hora(raw: str) -> str | None:
    """Aceita '18:30', '18h30', '18.30' → 'HH:MM'."""
    t = (raw or "").strip().casefold().replace(" ", "")
    if not t:
        return None
    m = re.fullmatch(r"(\d{1,2})[:hH\.](\d{2})", t)
    if not m:
        m = re.fullmatch(r"(\d{1,2})h?", t)
        if not m:
            return None
        hour = int(m.group(1))
        minute = 0
    else:
        hour = int(m.group(1))
        minute = int(m.group(2))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return f"{hour:02d}:{minute:02d}"
