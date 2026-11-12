# Explicação: interface web (`ric/web/`)

## Ficheiros

| Ficheiro | Função |
|---|---|
| `index.html` | Layout: marca RIC + rosto SVG EVE + lembretes + Falar |
| `style.css` | Contraste alto, painel EVE, glow e estados |
| `eye-shapes.css` | Morph SVG das expressões (paths) |
| `app.js` | Estados, face, STT, TTS, laboratório de expressões |

## Rosto (estilo EVE)

- SVG com **dois olhos** num painel escuro estilo EVE (glow cyan, scanlines, reflexo de vidro). Tema **Círculo** removido — EVE é a cara definitiva por agora.
- Olhos com **paths SVG** que mudam de forma (oval → crescente, barra inclinada, etc.); piscar fecha o contorno; idle ambient + laboratório.
- Detalhe «Morgana-light» (provisório, a decidir):
  - **Olho A · anel** — anel claro junto à borda + highlight afiado (`data-eye-style="ring"`)
  - **Olho B · pupila** — A + pupila oval fina (`data-eye-style="pupil"`); a pupila/anel reagem por expressão (escala, inclinação, pulso em `talk`)
  - Toggle temporário no ecrã; preferência em `localStorage` (`ric-eye-style`)
- Estados → expressões: `idle→calm`, `listening→curious`, `thinking→think`, `speaking→talk`, `alert→alert`.
- **Idle ambient:** sem interação, cicla expressões base (calmo, curioso, contente, pensar, sono, confuso) com pausas longas; pisca sozinho de 3–8 s.
- **Laboratório de expressões:** Calmo, Curioso, Pensar, Falar, Alerta, Contente, Triste, Surpreso, Sono, Confuso, Pisca, Piscar.  
  Morph fluido. Estado real (ex. Falar) tem prioridade; «Calmo» em idle volta ao ambient.

## Design / layout

O kiosk **não** inclui editor de layout.  
Prototipar: [`docs/design/ui-board.html`](../design/ui-board.html) — ver [`docs/design/README.md`](../design/README.md).  

**Ecrã actual:** cara EVE em ecrã inteiro. RIC e relógio ficam por cima. O resto abre com um toque e fecha sozinho ao fim de 8 segundos, ou quando um lembrete está a tocar.

## Ecrã

Em repouso a cara fica ao centro. Por cima, RIC e as horas. Por baixo dos olhos, a frase que o RIC está a dizer.

Um toque abre o resto à volta da cara: o próximo lembrete ao centro em cima, a lista de música à esquerda, e Adicionar em baixo. Outro toque na cara fecha. Sem uso, fecha ao fim de 8 segundos.

Um lembrete a disparar mostra um cartão com o título, a hora e os botões Já fiz e Adiar.

## Layout (público mais velho)

- **Marca RIC** e relógio sempre visíveis  
- **Botões em pastilha:** Falar e Já fiz a azul-claro, Adiar só com contorno, só quando fazem falta  
- Textos em **pt-PT**; foco visível no teclado  

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
