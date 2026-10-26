# `ric/web/`

Um processo: `ThreadingHTTPServer` em `:8787`.

- **REST** `/api/v1/health`, `/reminders`, `/reminders/next`, `POST /reminders`, `…/confirm`, `…/snooze` — envelope `{ ok, error, data }`.
- **WebSocket** `/ws` — push de `state`, `alert`, `next_reminder`, etc. (implementação mínima em `ws.py`).
- **Estáticos** `static/` — Idle: marca RIC, relógio, rosto, próximo lembrete; painel Já fiz / Adiar; formulário só para rotinas não-médicas.

Watchdog em thread: de X em X segundos consulta `due_now`, regista aviso, publica `alert` no bus e dispara TTS (`ric/voice`).
