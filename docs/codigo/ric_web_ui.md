# Explicação: interface web (`ric/web/`)

## Ficheiros

| Ficheiro | Função |
|---|---|
| `index.html` | Estrutura da página (agendar + lista + overlay de aviso) |
| `style.css` | Visual calmo, texto grande, bom contraste |
| `app.js` | Lógica no browser (API, lista, alertas) |

## O que o utilizador faz

1. **Fala com o RIC** na conversa (ex.: “Lembra-me de beber água às 16:45”)
2. A LLM agenda na base local e a lista atualiza
3. Também pode agendar manualmente (secção opcional)
4. Quando chega a hora:
   - ecrã de aviso + som;
   - frase gerada pela LLM (se disponível);
   - notificação do browser (se autorizada)
5. Escolhe **Já fiz** ou **Adiar 10 min**

## `app.js` — fluxo

1. `GET /api/llm` → mostra se a LLM local está pronta
2. Chat → `POST /api/chat` com histórico curto
3. `carregarLista()` → `GET /api/lembretes`
4. A cada ~4 s: lista + `GET /api/devidos`
5. Se devido: `disparar` → overlay → `POST .../frase`
6. Botões: `.../ok` ou `.../adiar`

## Design (PAP)

- Público-alvo: pessoas mais velhas → botões grandes, poucos passos
- Sem frameworks pesados
- Fontes locais do sistema (funciona offline)
- Não é diagnóstico médico — só lembretes

## Como abrir

```powershell
py -m ric ui
```

Depois agenda um lembrete 1–2 minutos à frente e espera o aviso.
