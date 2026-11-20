# Anexo I — rascunho para transcrição

Texto para copiar para o formulário oficial. Não substitui o formulário.

Planeamento: [`PLANEAMENTO.md`](PLANEAMENTO.md). Correções do pré-projeto (Gil, 2026-11-20): [`CORRECOES-PRE-PROJETO.md`](CORRECOES-PRE-PROJETO.md).

## Identificação

Pedro Albuquerque, turma 3-TIS, orientador Gil Ribeiro.

## O que é o RIC

O RIC (Robô Interativo Companheiro) é um protótipo de companheiro digital para quem precisa de apoio no dia a dia — em especial idosos. Ajuda a lembrar o essencial e faz companhia. Nesta PAP o trabalho é construir e testar o próprio robô: interação, privacidade e hardware reaproveitado.

Tem **corpo mínimo parado** (estrutura tipo gato: cabeça = ecrã tactile com rosto; tronco fixo; sem locomoção nem braços). A pessoa fala e ouve (TTS e STT); botões grandes e texto existem para quem ouve mal ou quando o reconhecimento falha.

## Versão mínima (MVP)

1. Voz offline em português de Portugal (STT + TTS Piper)  
2. Lembretes fiáveis (criar, disparar, Já fiz, Adiar) — **não** dependem da LLM  
3. Memória mínima local (nome, preferências, histórico curto)  
4. UI kiosk (rosto + alertas)

**Função única para o júri:** sistema de lembretes offline.

Extra (se sobrar tempo): música, histórias, livros, meteo, notícias, Telegram cuidador.

## Hardware e orçamento

- Cérebro: Intel NUC5i3RYH (i3-5010U) reaproveitado → 16 GB RAM  
- Ecrã tactile + microfone + colunas no mesmo equipamento / periféricos  
- SO: Linux Mint XFCE  
- Previsão: ver tabela em [`ORCAMENTO.md`](ORCAMENTO.md) (teto ≈ 70–230 €; com empréstimos ≈ 35–90 €)

## Etapas

| Até | O que se faz |
|---|---|
| Aceitação pré-projeto | Correções: corpo, hardware, MVP, C3, C5 |
| 08/01/2027 | Voz, conversação, lembretes, base UI |
| 26/03/2027 | Memória/gostos; extras se estáveis (música/histórias) |
| 21/05/2027 | Polish, testes, privacidade, limites |
| 18/06/2027 | Relatório |
| 09/07/2027 | Defesa |

## Recursos

Hardware reaproveitado (NUC5i3RYH), Python, Ollama, SQLite, Piper, faster-whisper. Lembretes e núcleo offline funcionam sem Internet.

## O que não entra

- Diagnóstico de doenças e prescrição de medicação  
- Testes com utentes idosos reais nesta PAP (se houver no futuro: consentimento escrito)  
- Recolha escolar de equipamentos  
- Locomoção e braços  
- BackOffice como produto desta PAP  

## C5 Observações (rascunho)

Projeto individual. Sem cliente externo nesta fase: protótipo escolar sem utentes reais. Limites: não diagnostica nem prescreve; sem locomoção/braços; núcleo offline-first; LLM local para conversa. Hardware principal reaproveitado (NUC5i3RYH). Função central a demonstrar: lembretes fiáveis.
