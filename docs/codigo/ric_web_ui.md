# Explicação: interface web (`ric/web/`)

## Ficheiros

| Ficheiro | Função |
|---|---|
| `index.html` | Layout companheiro: marca RIC + rosto + chat + painel |
| `style.css` | Contraste alto, botões grandes, tipografia local |
| `app.js` | Chat persistente, lembretes, player, face, STT, alertas |

## Layout (público mais velho)

- **Marca RIC** dominante no topo do painel de conversa  
- **Rosto** CSS simples: estados `listening` / `thinking` / `alerting`  
- **Botões grandes:** Já fiz, Adiar, Pausar, Continuar, Enviar, Falar  
- Textos em **pt-PT**; foco visível no teclado  

## Comportamentos importantes

1. Ao abrir: carrega `/api/conversas` e `/api/perfil`  
2. Polling de `/api/devidos` → overlay + pedido TTS ao servidor  
3. Conversa normal **não** para a música (só se a mensagem pedir controlo)  
4. Player: estado em `localStorage` (posição + volume)  
5. STT: Web Speech API — `pt-BR` por defeito (mais preciso no Chrome), alternativas + correções RIC, silêncio ~1,5 s → envia; senão texto continua  

## Como abrir

```powershell
py -m ric ui
```

Reiniciar o processo após alterações de código.  
Ver também `docs/CHECKLIST-REGRESSAO.md` e `docs/GUIAO-DEMO.md`.
