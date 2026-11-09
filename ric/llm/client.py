"""Cliente HTTP mínimo para a API de chat do Ollama."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class OllamaError(RuntimeError):
    """Falha de rede / resposta inválida do Ollama."""


def ollama_chat(
    *,
    base_url: str,
    model: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    timeout: float = 90.0,
    num_predict: int = 80,
    num_ctx: int = 2048,
    keep_alive: str | int = "30m",
) -> dict[str, Any]:
    # num_predict baixo = respostas curtas (TTS) e menos tempo no CPU.
    # keep_alive evita descarregar o modelo entre turnos.
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "keep_alive": keep_alive,
        "options": {
            "temperature": 0.3,
            "num_predict": int(num_predict),
            "num_ctx": int(num_ctx),
        },
    }
    if tools:
        payload["tools"] = tools
    url = base_url.rstrip("/") + "/api/chat"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise OllamaError(f"Ollama HTTP {exc.code}: {detail}") from exc
    except Exception as exc:  # noqa: BLE001
        raise OllamaError(str(exc)) from exc
    if not isinstance(body, dict) or "message" not in body:
        raise OllamaError("Resposta Ollama inválida")
    return body


def ollama_alive(base_url: str, *, timeout: float = 2.0) -> bool:
    url = base_url.rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except Exception:  # noqa: BLE001
        return False
