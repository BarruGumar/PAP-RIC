# Inventário de hardware — RIC (PAP)

Princípio: **reaproveitar primeiro**; só comprar se o reaproveitado não cumprir o requisito.  
Preencher com o que existe em casa / escola.

## Componentes principais

| # | Componente | Origem | Estado | Função no RIC | Compra nova? | Justificação |
|---|---|---|---|---|---|---|
| 1 | PC / NUC / portátil (cérebro) | Reaproveitado / a definir | | Backend + Ollama + UI server | Não / Sim | |
| 2 | Tablet / ecrã (rosto) | Reaproveitado / a definir | | Cliente fino (`py -m ric ui`) | Não / Sim | |
| 3 | Altifalantes / auscultadores | Reaproveitado | | Música + avisos TTS | Não / Sim | |
| 4 | Microfone | Reaproveitado / embutido | | STT local (faster-whisper). O browser envia o áudio à Google | Não / Sim | |
| 5 | Raspberry Pi 5 + AI HAT+ 2 | Fora do foco | | Os modelos prontos vão até 1,5B. O `qwen2.5:3b` não corre lá | Não comprar agora | Mini-PC usado com 16 GB é a opção do orientador |
| 6 | Arduino (fase extra) | | | Locomoção/sensores — **fora do MVP** | | Não crítico |

## Meta de reaproveitamento

- Objetivo: ≥ 50% dos componentes principais reutilizados.
- Contagem atual: ____ / ____ = ____ %

## Notas

- PCs muito antigos (32-bit / pouca RAM) podem servir só como UI; a LLM corre noutro PC da rede local se necessário (ainda local-first).
- Não é obrigatório Raspberry nem cloud para a demo da PAP. O AI HAT+ 2 publica modelos de 1B a 1,5B. O cérebro preferido, se o PC atual não chegar, é um mini-PC usado com 16 GB. Ver [`FEEDBACK-ORIENTADOR.md`](FEEDBACK-ORIENTADOR.md).
- Atualizar este ficheiro quando o hardware final for escolhido.
