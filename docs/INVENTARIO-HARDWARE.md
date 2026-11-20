# Inventário de hardware — RIC (PAP)

**Atualizado:** 2026-11-20  
**Princípio:** reaproveitar primeiro; só comprar se o reaproveitado não cumprir o requisito.

## Decisão (fechada)

**Cérebro oficial:** Intel **NUC5i3RYH** (Core i3-5010U), reaproveitado, a expandir até **16 GB** DDR3L.  
**Reserva:** Intel **NUC DN2820FYK** (Celeron N2820) — peças / emergência; **não** é o cérebro da demo.  
**UI:** ecrã **tactile** no mesmo NUC (HDMI/DP + USB), `http://127.0.0.1:8787`. Sem tablet à parte.  
**Áudio:** microfone + colunas separados (emprestar ou comprar).  
**Corpo mínimo:** estrutura parada tipo gato (cabeça = ecrã; sem locomoção/braços). Ver [`estudos/VISUAL-E-CORPO.md`](estudos/VISUAL-E-CORPO.md).  
**Orçamento:** [`ORCAMENTO.md`](ORCAMENTO.md).

---

## Componentes principais

| # | Componente | Origem | Estado | Função no RIC | Compra? | Justificação |
|---|---|---|---|---|---|---|
| 1 | **Intel NUC5i3RYH** (i3-5010U) | Já possui (reaproveitado) | Escolhido; RAM a expandir a 16 GB | Cérebro: SO, SQLite, voz, Ollama, UI server | Não (máquina) / Sim (RAM) | Único dos dois NUCs que aguenta MVP completo |
| 2 | Intel NUC DN2820FYK (Celeron N2820) | Já possui | Reserva | Não usado como cérebro | Não | CPU/RAM insuficientes para LLM + STT juntos |
| 3 | RAM 2×8 GB DDR3L-1600 1,35 V SO-DIMM | A adquirir | Planeado | Dual-channel 16 GB no NUC5i3RYH | Sim | Sem 16 GB, Qwen 3B + Whisper apertam |
| 4 | SSD (M.2 ou 2,5") | Verificar no NUC | A confirmar | Sistema + modelos | Só se faltar | SSD evita lentidão de HDD |
| 5 | Ecrã tactile HDMI/DP | Emprestar ou comprar usado | Pendente | Rosto kiosk + toque | Talvez | Cabeça do corpo mínimo |
| 6 | Microfone USB / jack | Emprestar ou comprar | Pendente | STT (faster-whisper) | Talvez | Separado do NUC |
| 7 | Colunas / altifalante | Emprestar ou comprar | Pendente | TTS Piper + alertas + música | Talvez | Separado do NUC |
| 8 | Raspberry Pi 5 + AI HAT | — | Fora | — | Não | Modelos prontos ≤1,5B; 3B não corre bem |
| 9 | Arduino | — | Fora desta PAP | Locomoção | Não | Fora de âmbito |

## Meta de reaproveitamento

- Objetivo: ≥ 50% dos componentes principais reutilizados.
- Contagem atual (núcleo): NUC + (ecrã/mic/colunas se emprestados) → maioria reaproveitada; compra típica = RAM (± ecrã/áudio se não houver empréstimo).

---

## Comparação dos dois NUCs (2026-11-20)

Assumindo RAM no máximo (16 GB no i3, 8 GB no Celeron) + SSD + Linux Mint XFCE.

| Função RIC | NUC5i3RYH (i3) | DN2820FYK (Celeron) |
|---|---|---|
| Kiosk + rosto (IDLE/OPEN/ALERT) | Sim | Sim |
| Lembretes offline (sem LLM) | Sim | Sim |
| Memória SQLite | Sim | Sim |
| TTS Piper tugão | Sim | Sim (mais lento) |
| STT faster-whisper | `tiny`/`base` ok; `small` lento | Só `tiny`, frágil |
| Wake-word | Sim | Apertado com o resto |
| LLM `qwen2.5:1.5b` | Sim | Limite / muito lento |
| LLM `qwen2.5:3b` (alvo) | Sim, **devagar** | Quase inviável com voz |
| AMALIA-9B | Stretch | Não |
| Música / histórias locais | Sim | Sim |
| Demo júri = lembretes | Sim | Sim |
| Demo companheiro por voz | Sim (com paciência) | Não realista |

**Conclusão:** o pré-projeto e a defesa usam o **NUC5i3RYH**. O DN2820FYK não sustenta o MVP completo (voz PT + lembretes + memória + conversa local).

### Limitações honestas (i3-5010U)

- CPU de 2015: respostas do LLM em CPU podem levar vários segundos a dezenas de segundos.
- STT offline continua a parte mais frágil.
- Lembretes **não** dependem da LLM nem da Internet — a função única do júri mantém-se fiável.
