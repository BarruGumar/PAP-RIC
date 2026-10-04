# Inventário de hardware — RIC (PAP)

Princípio: **reaproveitar primeiro**; só comprar se o reaproveitado não cumprir o requisito.  
Preencher com o que existe em casa / escola.

## Componentes principais

| # | Componente | Origem | Estado | Função no RIC | Compra nova? | Justificação |
|---|---|---|---|---|---|---|
| 1 | PC / NUC / portátil (cérebro) | Reaproveitado / a definir | | Backend + Ollama + UI server | Não / Sim | |
| 2 | Tablet / ecrã (rosto) | Reaproveitado / a definir | | Cliente fino (`py -m ric ui`) | Não / Sim | |
| 3 | Altifalantes / auscultadores | Reaproveitado | | Música + avisos TTS | Não / Sim | |
| 4 | Microfone | Reaproveitado / embutido | | STT opcional (browser) | Não / Sim | |
| 5 | Raspberry Pi 5 + AI HAT (opcional futuro) | | | LLM local mais eficiente | Sim só se necessário | |
| 6 | Arduino (fase extra) | | | Locomoção/sensores — **fora do MVP** | | Não crítico |

## Meta de reaproveitamento

- Objetivo: ≥ 50% dos componentes principais reutilizados.
- Contagem atual: ____ / ____ = ____ %

## Notas

- PCs muito antigos (32-bit / pouca RAM) podem servir só como UI; a LLM corre noutro PC da rede local se necessário (ainda local-first).
- Não é obrigatório Raspberry nem cloud para a demo da PAP.
- Atualizar este ficheiro quando o hardware final for escolhido.
