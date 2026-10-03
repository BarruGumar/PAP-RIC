from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any

from ric import db

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:3b"
TIMEOUT_S = 120

SYSTEM_PROMPT = """
És o RIC, companheiro digital local de apoio (português de Portugal).
Ajudas a conversar e a gerir lembretes. NÃO diagnosticas nem receitas medicamentos.
Quando o utilizador quiser lembrar algo, usa as ferramentas.
Se faltar a hora, pergunta. Tipos válidos: medicamento, consulta, tarefa, outro.
Horas no formato HH:MM (24h). Sê breve, claro e simpático.
""".strip()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "agendar_lembrete",
            "description": "Agenda um lembrete local (hora HH:MM).",
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {
                        "type": "string",
                        "description": "Texto curto do lembrete",
                    },
                    "hora": {
                        "type": "string",
                        "description": "Hora no formato HH:MM",
                    },
                    "tipo": {
                        "type": "string",
                        "enum": list(db.TIPOS_VALIDOS),
                        "description": "Tipo do lembrete",
                    },
                },
                "required": ["titulo", "hora"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_lembretes",
            "description": "Lista os lembretes atuais.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "confirmar_lembrete",
            "description": "Marca um lembrete como feito (já fiz).",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "ID do lembrete"},
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adiar_lembrete",
            "description": "Adia um lembrete alguns minutos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "minutos": {"type": "integer", "default": 10},
                },
                "required": ["id"],
            },
        },
    },
]


class LlmError(RuntimeError):
    pass


def estado() -> dict[str, Any]:
    try:
        data = _http_json(f"{OLLAMA_URL}/api/tags", method="GET", payload=None, timeout=3)
        nomes = [m.get("name", "") for m in data.get("models", [])]
        return {
            "ok": True,
            "modelo": DEFAULT_MODEL,
            "modelo_disponivel": DEFAULT_MODEL in nomes or any(
                n.startswith("qwen2.5:3b") for n in nomes
            ),
            "modelos": nomes,
        }
    except Exception as exc:  # noqa: BLE001 - estado de saúde
        return {
            "ok": False,
            "modelo": DEFAULT_MODEL,
            "modelo_disponivel": False,
            "erro": str(exc),
        }


def _http_json(
    url: str,
    method: str = "POST",
    payload: dict | None = None,
    timeout: int = TIMEOUT_S,
) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data is not None else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise LlmError(
            "Ollama indisponível. Confirma que está a correr em http://127.0.0.1:11434"
        ) from exc
    except TimeoutError as exc:
        raise LlmError("A LLM demorou demasiado. Tenta outra vez.") from exc


def _contexto_lembretes() -> str:
    itens = db.listar()
    if not itens:
        return "Lembretes atuais: (nenhum)"
    linhas = [
        f"- #{i.id} {i.hora} [{i.tipo}] {i.titulo} ({i.estado}) proximo={i.proximo_em}"
        for i in itens
    ]
    return "Lembretes atuais:\n" + "\n".join(linhas)


def _executar_ferramenta(nome: str, args: dict[str, Any]) -> dict[str, Any]:
    if nome == "agendar_lembrete":
        item = db.adicionar(
            str(args.get("titulo", "")),
            str(args.get("hora", "")),
            str(args.get("tipo", "tarefa") or "tarefa"),
        )
        return {
            "ok": True,
            "acao": "agendar",
            "lembrete": {
                "id": item.id,
                "titulo": item.titulo,
                "hora": item.hora,
                "tipo": item.tipo,
                "proximo_em": item.proximo_em,
            },
        }
    if nome == "listar_lembretes":
        itens = db.listar()
        return {
            "ok": True,
            "acao": "listar",
            "lembretes": [
                {
                    "id": i.id,
                    "titulo": i.titulo,
                    "hora": i.hora,
                    "tipo": i.tipo,
                    "estado": i.estado,
                    "proximo_em": i.proximo_em,
                }
                for i in itens
            ],
        }
    if nome == "confirmar_lembrete":
        item = db.confirmar(int(args["id"]))
        return {
            "ok": True,
            "acao": "confirmar",
            "lembrete": {"id": item.id, "titulo": item.titulo, "estado": item.estado},
        }
    if nome == "adiar_lembrete":
        minutos = int(args.get("minutos", 10) or 10)
        item = db.adiar(int(args["id"]), minutos)
        return {
            "ok": True,
            "acao": "adiar",
            "lembrete": {
                "id": item.id,
                "titulo": item.titulo,
                "estado": item.estado,
                "proximo_em": item.proximo_em,
            },
        }
    return {"ok": False, "erro": f"Ferramenta desconhecida: {nome}"}


def _chat_ollama(messages: list[dict[str, Any]], usar_tools: bool = True) -> dict:
    payload: dict[str, Any] = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    if usar_tools:
        payload["tools"] = TOOLS
    return _http_json(f"{OLLAMA_URL}/api/chat", payload=payload)


def _parse_args(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return {}
        return json.loads(raw)
    return {}


def conversar(mensagem: str, historico: list[dict[str, str]] | None = None) -> dict[str, Any]:
    mensagem = (mensagem or "").strip()
    if not mensagem:
        raise ValueError("A mensagem não pode estar vazia.")

    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    system = (
        f"{SYSTEM_PROMPT}\n\nAgora local: {agora}\n{_contexto_lembretes()}"
    )

    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    for item in (historico or [])[-8:]:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": mensagem})

    acoes: list[dict[str, Any]] = []
    data = _chat_ollama(messages, usar_tools=True)
    msg = data.get("message") or {}
    tool_calls = msg.get("tool_calls") or []

    if tool_calls:
        messages.append(msg)
        for call in tool_calls:
            fn = call.get("function") or {}
            nome = fn.get("name") or ""
            try:
                args = _parse_args(fn.get("arguments"))
                resultado = _executar_ferramenta(nome, args)
            except (ValueError, LookupError, json.JSONDecodeError, KeyError, TypeError) as exc:
                resultado = {"ok": False, "acao": nome, "erro": str(exc)}
            acoes.append(resultado)
            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(resultado, ensure_ascii=False),
                }
            )

        # Pedido final sem tools para obter resposta natural
        data2 = _chat_ollama(messages, usar_tools=False)
        msg = data2.get("message") or {}

    resposta = (msg.get("content") or "").strip()
    if not resposta:
        if any(a.get("ok") for a in acoes):
            resposta = "Feito. Atualizei os teus lembretes."
        else:
            resposta = "Percebi, mas não consegui formular a resposta. Podes repetir?"

    return {
        "resposta": resposta,
        "acoes": acoes,
        "modelo": DEFAULT_MODEL,
        "ollama": True,
    }


def frase_aviso(titulo: str, tipo: str, hora: str) -> str:
    """Gera frase amigável para o alerta; se falhar, devolve texto simples."""
    prompt = (
        "Escreve UMA frase curta em português de Portugal para avisar um lembrete. "
        "Sem diagnósticos. Sem aspas. Máximo 25 palavras.\n"
        f"Lembrete: {titulo}. Tipo: {tipo}. Hora: {hora}."
    )
    try:
        data = _chat_ollama(
            [
                {
                    "role": "system",
                    "content": "És o RIC. Respostas muito curtas e claras.",
                },
                {"role": "user", "content": prompt},
            ],
            usar_tools=False,
        )
        texto = ((data.get("message") or {}).get("content") or "").strip()
        texto = texto.strip(" \"'")
        return texto or f"É a hora: {titulo}"
    except Exception:  # noqa: BLE001 - fallback obrigatório
        return f"É a hora: {titulo}"
