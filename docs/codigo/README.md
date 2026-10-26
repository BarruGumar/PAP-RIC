# Explicações do código — RIC

## App atual (reescrita 2026-10-25)

| Ficheiro | Explicação |
|---|---|
| `ric/__main__.py` / `ric/cli.py` | [ric_cli.md](ric_cli.md) |
| `ric/config.py` | [ric_config.md](ric_config.md) |
| `ric/db/` | [ric_db.md](ric_db.md) |
| `ric/reminders/` | [ric_reminders.md](ric_reminders.md) |
| `ric/core/events.py` | [ric_core_events.md](ric_core_events.md) |
| `ric/web/server.py` + `ws.py` + `static/` | [ric_web.md](ric_web.md) |
| `ric/voice/` | [ric_voice.md](ric_voice.md) |

Arranque: `py -m ric ui` → `http://127.0.0.1:8787/` (REST `/api/v1/…`, WS `/ws`).

Testes: `py -m pytest tests/ -v`

## Legado

O protótipo antigo está em [`archive/legacy/`](../../archive/legacy/README.md). As fichas antigas (`ric_llm.md`, `ric_voice.md`, …) descrevem esse código; não são a base da demo.
