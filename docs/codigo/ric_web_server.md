# Explicação: `ric/web_server.py`

## Para que serve

Serve a **interface web local** dos lembretes no browser:

```powershell
py -m ric ui
```

Abre `http://127.0.0.1:8787/` e permite:

- agendar lembretes;
- ver a lista;
- confirmar (`Já fiz`) ou adiar;
- receber aviso quando chega a hora.

Usa só a **biblioteca padrão** do Python (`http.server`) — sem Flask/FastAPI instalados.

## Ideia importante

- A UI é um **cliente fino**.
- A verdade dos dados continua em `ric/db.py` + SQLite.
- Não precisa de internet nem de LLM.

## Peças principais

### Constantes

- `WEB_DIR` → pasta `ric/web/` (HTML/CSS/JS)
- `HOST` / `PORT` → `127.0.0.1:8787` (só neste PC)

### API JSON

| Método | Rota | Função |
|---|---|---|
| GET | `/api/lembretes` | Lista todos |
| GET | `/api/devidos` | Lembretes cuja hora já chegou |
| GET | `/api/tipos` | Tipos válidos |
| POST | `/api/lembretes` | Cria (`titulo`, `hora`, `tipo`) |
| POST | `/api/lembretes/{id}/ok` | Confirma |
| POST | `/api/lembretes/{id}/adiar` | Adia (`minutos`) |
| POST | `/api/lembretes/{id}/disparar` | Marca como disparado |
| GET | `/api/llm` | Estado do Ollama/modelo |
| POST | `/api/chat` | Conversa + ações (agendar/ok/adiar) via LLM |
| POST | `/api/lembretes/{id}/frase` | Frase amigável do aviso (LLM, com fallback) |

### Ficheiros estáticos

`GET /`, `/index.html`, `/style.css`, `/app.js` → lidos de `ric/web/`.

Há proteção contra `..` no caminho (path traversal).

### `servir()`

1. Garante a base (`init_db`)
2. Arranca `ThreadingHTTPServer`
3. Abre o browser (opcional)
4. Fica a servir até `Ctrl+C`

## Relação com a UI

O JavaScript (`ric/web/app.js`) faz pedidos a estas rotas de poucos em poucos segundos para atualizar a lista e mostrar o overlay de aviso.
