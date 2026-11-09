# Design UI do RIC

O ecrã **real** do RIC (`py -m ric ui`) fica limpo para a demo.  
O desenho/layout faz-se no **editor** à parte; quando estiveres satisfeito, colas o JSON no chat e eu aplico no original.

## Editor visual (Canva simples)

```powershell
start docs\design\ui-board.html
```

Blocos fixos do ecrã: `brand`, `face`, `next`, `talk`, `alert`, `form`.

| Acção | Como |
|---|---|
| Seleccionar | Clique no bloco ou na lista de camadas |
| Mover | Arrastar o bloco |
| Redimensionar | Pegas nos cantos |
| Cor | Inspector (fundo / texto) |
| Ocultar | Delete / Backspace, ou «Apagar», ou botão On/Off na camada |
| Desfazer | Ctrl+Z |
| Guardar local | automático (`localStorage` → `ric_ui_layout`) |
| Enviar para aplicar no RIC | **Copiar JSON** ou **Exportar JSON** e colar no chat |

## Fluxo

1. Abre o editor e mexes no layout.
2. **Copiar JSON** → cola no chat («aplica este layout no RIC»).
3. Eu porto as mudanças para `ric/web/static/`.

**Provisório em uso:** [`ric-ui-layout.provisional.json`](ric-ui-layout.provisional.json)  
(cara larga + Próximo|Falar lado a lado). Depois refinamos com a idealização final.

## Laboratório de expressões / olhos

Continua **dentro** do RIC (cara EVE), só para pré-visualizar — não é o editor de layout.

- Expressões (Calmo, Alerta, Contente, …)
- Toggle **Olho A · anel** / **Olho B · pupila** (experimento; ver `docs/codigo/ric_web_ui.md`)
