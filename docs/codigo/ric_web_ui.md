# Explicação: interface web (`ric/web/`)

## Ficheiros

| Ficheiro | Função |
|---|---|
| `index.html` | Layout kiosk: RIC + horas + rosto SVG EVE + controlos + alerta + Lab PAP |
| `style.css` | Outline kiosk, alerta, biblioteca, debug HUD; CSS dos olhos SVG |
| `eye-shapes.css` | Morph SVG das expressões (paths) |
| `app.js` | Estados, face, STT, TTS, biblioteca local, laboratório |

## Rosto (estilo EVE)

- SVG com **dois olhos** num fundo escuro estilo EVE (glow cyan, scanlines, shine). Tema **Círculo** removido — EVE é a cara definitiva por agora.
- Olhos com **paths SVG** que mudam de forma; piscar fecha o contorno; idle ambient + laboratório.
- Detalhe «Morgana-light» (provisório, a decidir):
  - **Olho A · anel** — anel claro junto à borda + highlight (`data-eye-style="ring"`)
  - **Olho B · pupila** — A + pupila oval fina (`data-eye-style="pupil"`)
  - Toggle no **Lab PAP** (botão canto inferior direito ou tecla `D`); preferência em `localStorage` (`ric-eye-style`)
- Estados → expressões: `idle→calm`, `listening→curious`, `thinking→think`, `speaking→talk`, `alert→alert`.
- **Idle ambient:** cicla expressões base com pausas longas; pisca sozinho de 3–8 s.
- **Laboratório de expressões:** dentro do Lab PAP (Calmo, Curioso, Pensar, Falar, Alerta, …).

## Design / layout

O kiosk **não** inclui editor de layout.  
Prototipar: [`docs/design/ui-board.html`](../design/ui-board.html) — ver [`docs/design/README.md`](../design/README.md).

**Ecrã actual:** cara EVE em ecrã inteiro. Estética outline (borda fina, cantos ~0.25rem, fundo `#0b1018`).

## Ecrã — 3 estados

1. **Repouso (idle):** RIC + horas + pill **«Próximo: …»** no topo; olhos ao centro; legenda em baixo (`#heard`) + hint «toque no ecrã». Sem botões.
2. **Aberto (toque):** à esquerda Música / Histórias / Livros (widget flutuante); em baixo Falar + Lembrete. Fecha ao toque na cara ou aos 8 s sem uso.
3. **Alerta:** cartão modal com badge «Lembrete agora», título, hora, **Já fiz** (ciano) e **Adiar (10 min)** (outline). Controlos do aberto ficam escondidos.

## Layout (público mais velho)

- **Marca RIC**, relógio e **próximo lembrete** sempre visíveis (não dependem do toque)  
- Botões outline grandes; Falar e Já fiz a ciano  
- Textos em **pt-PT**; foco visível no teclado  
- Lab PAP só para demonstração / júri (não é UI do idoso)

## Voz (botão Falar)

- Microfone abre logo; o wake corre em paralelo.
- Envia **sozinho** após ~0,9 s de silêncio (mín. ~0,35 s de fala); **Parar** força o envio; máximo ~15 s.
- PCM a 16 kHz com silêncio à cabeça/cauda cortado antes do STT.

## Como abrir

```powershell
py -m ric ui
```

Reiniciar o processo após alterações de código.  
Ver também `docs/CHECKLIST-REGRESSAO.md` e `docs/GUIAO-DEMO.md`.
