# `ric/llm/`

Cliente **Ollama** local (`qwen2.5:3b` por defeito) + tools P1 mínimas.

## Ficheiros

| Ficheiro | Papel |
|---|---|
| `client.py` | HTTP `/api/chat` e probe `/api/tags` |
| `prompt.py` | System prompt PT-PT + tools + fallback |
| `service.py` | `LlmService.chat()` com tool loop |

## Tools (esta fatia)

- `listar_lembretes` — leitura
- `proximo_lembrete` — leitura
- `criar_lembrete` — cria rotina **não médica** (`tarefa` / `consulta` / `outro`) com `titulo` + `hora` HH:MM
- `apagar_lembrete` — apaga rotina **autorizada** (não médica / não crítica) por `id` ou `titulo`

**Proibido:** criar/apagar/editar medicamentos ou críticos (só cuidador com PIN).  
Após criar/apagar por voz publica `reminders_changed` + `next_reminder` no WebSocket.

## Config

```text
RIC_OLLAMA_URL=http://127.0.0.1:11434
RIC_MODEL=qwen2.5:3b
RIC_LLM_TIMEOUT=90
```

No CPU, o 1.º turno com tools pode levar ~50s; o timeout por defeito é 90s.  
Cumprimentos simples **não** enviam tools (mais rápido).  
Ollama: `num_predict=80`, `num_ctx=2048`, `keep_alive=30m`.  
Ao arrancar a UI há warm-up em background (Piper + Whisper + Ollama).

## Resiliência

Se Ollama estiver em baixo, o core (lembretes/UI/TTS) sobe na mesma.  
`chat()` devolve frase de fallback; não rebenta o servidor.  
Falhas LLM aparecem no terminal como `[RIC] LLM …`.

## Fluxo na voz

`VoiceSession`: STT → `llm.chat` → Piper (`assistant_reply` + `audio_url` no WS).
