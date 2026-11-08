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

**Proibido** (ainda sem tool): criar/editar medicamentos.

## Config

```text
RIC_OLLAMA_URL=http://127.0.0.1:11434
RIC_MODEL=qwen2.5:3b
RIC_LLM_TIMEOUT=10
```

## Resiliência

Se Ollama estiver em baixo, o core (lembretes/UI/TTS) sobe na mesma.  
`chat()` devolve frase de fallback; não rebenta o servidor.

## Fluxo na voz

`VoiceSession`: STT → `llm.chat` → Piper (`assistant_reply` + `audio_url` no WS).
