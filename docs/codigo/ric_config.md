# `ric/config.py`

Carrega definições locais a partir de variáveis de ambiente e de `.env` (ver `config.example.env` na raiz).

- `RIC_DATA_DIR` — pasta de dados (`ric.db`, futuros media/backups). Default: `./ric-data` na raiz do repo.
- `RIC_HOST` / `RIC_PORT` — default `127.0.0.1:8787`.
- `RIC_DEBUG` — logs HTTP verbosos.
- `RIC_REMINDER_MAX_ALERTS` / `RIC_REMINDER_RETRY_MINUTES` — retries de lembrete (default 3 × 2 min).

Não contém segredos no código; tokens Telegram ficam só no `.env` (etapa 3).
