# `ric/db/`

SQLite local-first. `Database` abre `ric.db` sob `RIC_DATA_DIR` e cria o schema.

Tabelas na 1.ª fatia:

- `lembretes` — schema A: tipo, crítico, diário, estado, `proximo_em`, `criado_por`, `avisos_feitos` (sem dose estruturada).
- `confirmacoes` — histórico leve confirmar/adiar.
- `perfil` — reservado para preferências (etapa 2).

Sem rede; sem LLM.
