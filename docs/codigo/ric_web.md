# `ric/web/`

Um processo: `ThreadingHTTPServer` em `:8787`.

- **REST** `/api/v1/health`, `/reminders`, `/reminders/next`, `POST /reminders`, `…/confirm`, `…/snooze` — envelope `{ ok, error, data }`.
- **Voz** `POST /api/v1/voice/wake`, `/voice/cancel`, `/voice/utterance` (`audio_base64` + `content_type`).
- **WebSocket** `/ws` — push de `state`, `alert`, `next_reminder`, `transcript`, etc. (implementação mínima em `ws.py`).
- **Estáticos** `static/` — Idle: marca RIC, relógio, **rosto SVG estilo EVE** (+ laboratório de expressões), próximo lembrete; botão **Falar** (tocar para gravar); painel Já fiz / Adiar; formulário só para rotinas não-médicas.

Watchdog em thread: de X em X segundos consulta `due_now`, regista aviso, publica `alert` no bus e dispara TTS (`ric/voice`).
Wake manual + STT: ver [`ric_voice.md`](ric_voice.md).
