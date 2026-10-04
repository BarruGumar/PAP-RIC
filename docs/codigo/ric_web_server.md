# Explicação: `ric/web_server.py`

## Para que serve

Serve a **interface web local** do RIC no browser:

```powershell
py -m ric ui
```

Abre `http://127.0.0.1:8787/` e permite:

- conversar (Ollama, se disponível);
- agendar / confirmar / adiar lembretes;
- tocar músicas offline;
- carregar perfil e histórico de chat;
- receber aviso quando chega a hora (UI + **watchdog** no servidor).

Usa só a **biblioteca padrão** do Python (`http.server`) — sem Flask/FastAPI.

## Watchdog de lembretes

Ao arrancar `servir()`:

1. `iniciar_watchdog()` cria uma **thread daemon**;
2. a cada ~5 s chama `db.devidos()`;
3. marca `disparado`, imprime `[RIC watchdog]…`, faz `voice.beep()` e `voice.falar(...)`.

Isto é a **rede de segurança**: mesmo se o JavaScript falhar ou o overlay não abrir, o processo Python avisa.  
A UI continua a fazer polling para o overlay visual.

## API JSON

| Método | Rota | Função |
|---|---|---|
| GET | `/api/lembretes` | Lista todos |
| GET | `/api/devidos` | Lembretes cuja hora já chegou |
| GET | `/api/tipos` | Tipos válidos |
| POST | `/api/lembretes` | Cria |
| POST | `/api/lembretes/{id}/ok` | Confirma |
| POST | `/api/lembretes/{id}/adiar` | Adia |
| POST | `/api/lembretes/{id}/disparar` | Marca disparado |
| POST | `/api/lembretes/{id}/frase` | Frase amigável (LLM + fallback) |
| GET | `/api/llm` | Estado Ollama + info de voz |
| POST | `/api/chat` | Conversa + tools |
| GET | `/api/perfil` | Preferências guardadas |
| POST | `/api/perfil` | Guardar preferência (`chave`, `valor`) |
| GET | `/api/conversas` | Histórico de chat |
| POST | `/api/conversas/limpar` | Apagar histórico |
| POST | `/api/voz/falar` | TTS local (`texto`) |
| GET | `/api/musica` | Géneros + faixas |
| GET | `/api/musica/{id}/stream` | Stream áudio |
| POST | `/api/musica/tocar` | Escolher faixa |

## Degradação sem Ollama

Se Ollama estiver em baixo, `POST /api/chat` devolve 503, mas lembretes, música, perfil e watchdog **continuam**.

## `servir()`

1. `db.init_db()` + pastas de música  
2. Arranca watchdog  
3. `ThreadingHTTPServer`  
4. Abre browser (opcional)  
5. `Ctrl+C` → para watchdog e fecha servidor  
