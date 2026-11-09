# `ric/reminders/`

Lógica de lembretes **independente** da LLM e da Internet.

Regra **2A**: tipo `medicamento` ou `critico=True` exige `caregiver_authenticated=True` para **criar e apagar**. Sem PIN nesta fatia — a UI/CLI/voz só gerem rotinas não-críticas; o cuidador com PIN (etapa 2) passará `caregiver_authenticated`.

Estados: `pendente` → `disparado` → `confirmado` | `adiado` | `expirado` (após N avisos).

API de serviço: `create`, `create_at`, `delete`, `find_by_titulo`, `due_now`, `register_alert`, `confirm`, `snooze`, `next_pending`.
