# `ric/reminders/`

Lógica de lembretes **independente** da LLM e da Internet.

Regra **2A**: tipo `medicamento` ou `critico=True` exige `caregiver_authenticated=True` para **criar e apagar**. Sem PIN nesta fatia — a UI/CLI/voz só gerem rotinas não-críticas; o cuidador com PIN (etapa 2) passará `caregiver_authenticated`.

Estados: `pendente` → `disparado` → `confirmado` | `adiado` | `expirado` (após N avisos).

- **Diário (`diario=True`, default):** ao confirmar, volta a `pendente` na **próxima** ocorrência da hora (tipicamente amanhã) com `avisos_feitos=0`.
- **One-shot (`diario=False`):** ao confirmar fica `confirmado`.
- Reavisos: `register_alert` agenda `proximo_em = agora + RIC_REMINDER_RETRY_MINUTES` (default 2).
- Watchdog (~3 s): regista `lag=` (atraso desde `proximo_em`) e `tts=`; a síntese TTS corre **fora** do lock para não bloquear o tick.

API de serviço: `create`, `create_at`, `delete`, `find_by_titulo`, `due_now`, `register_alert`, `confirm`, `snooze`, `next_pending`, `list_active`.
