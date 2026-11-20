# Correções do pré-projeto — feedback Gil Ribeiro

**Data:** 2026-11-20  
**Aluno:** Pedro Albuquerque (n.º — turma 3-TIS)  
**Título:** RIC: companheiro interativo por voz  

Textos prontos a colar / adaptar no Word do pré-projeto. Fonte viva: `CONTEXTO-PAP.md`, `INVENTARIO-HARDWARE.md`, `ORCAMENTO.md`.

---

## O que já estava bem (manter)

- Protótipo a correr com modelo local  
- Privacidade e offline como princípios  
- Lembretes **não** dependem da LLM  
- Limites claros: não diagnostica nem prescreve  

---

## 1. «Robô» sem corpo → corpo mínimo

**Decisão:** manter o nome **RIC — Robô Interativo Companheiro** e apresentar um **corpo mínimo parado**.

**Texto sugerido:**

> O RIC mantém a designação de robô. Nesta PAP a locomoção e os braços ficam de fora. O protótipo tem um **corpo mínimo parado**: estrutura tipo companheiro animal (proporção de gato — cabeça grande, tronco pequeno), sem motores. A «cabeça» é um ecrã tactile com o rosto do RIC; o tronco é suporte fixo reaproveitado. Assim o júri vê um robô físico, sem prometer mobilidade fora de âmbito.

---

## 2. Hardware escolhido (já não é «ainda não sei»)

**Decisão:** cérebro = **Intel NUC5i3RYH** (Core i3-5010U), reaproveitado, expandido a **16 GB** RAM.  
Reserva: NUC DN2820FYK (Celeron) — não é o cérebro.  
UI: ecrã tactile no mesmo NUC. Áudio: microfone + colunas (emprestar ou comprar).  
SO: Linux Mint XFCE.

**Texto sugerido:**

> Hardware principal: mini-PC Intel NUC5i3RYH (i3-5010U) reaproveitado, com expansão de memória para 16 GB DDR3L, ecrã tactile no mesmo equipamento, microfone e colunas. Sistema operativo: Linux Mint XFCE. Um segundo NUC (DN2820FYK, Celeron) existe em reserva mas não sustenta LLM + reconhecimento de voz em simultâneo, por isso não é o cérebro da demonstração. Comparação documentada em inventário de hardware.

---

## 3. Versão mínima (MVP)

| MVP (obrigatório na defesa) | Extra (se sobrar tempo) |
|---|---|
| Voz offline em português de Portugal (STT + TTS Piper) | Música, histórias, livros |
| Lembretes (criar, disparar, «Já fiz», «Adiar») — sem LLM | Agenda completa, meteo, notícias |
| Memória mínima (nome, preferências, histórico curto) | Aviso Telegram ao cuidador, BackOffice |
| UI kiosk (rosto + alertas) | Modelo AMALIA, wake-word perfeito |

**Texto sugerido:**

> A versão mínima desta PAP é: (1) interação por voz offline em português de Portugal; (2) lembretes fiáveis independentes do modelo de linguagem; (3) memória mínima local. Tudo o resto (música, histórias, livros, meteorologia, notícias, BackOffice) é extra. O reconhecimento de fala offline é a parte mais exigente e ainda frágil — os lembretes e a interface por toque garantem a demonstração mesmo se o STT falhar pontualmente.

---

## 4. Função única para o júri (próxima sessão)

**Resposta:**

> Se só pudesse mostrar uma função ao júri, seria o **sistema de lembretes offline**: criar um aviso, disparar à hora com som e ecrã, e confirmar com «Já fiz» ou «Adiar». É a função mais fiável, não depende de Internet nem da LLM, e mostra o valor concreto do companheiro no dia a dia.

---

## 5. Consentimento informado

**Texto sugerido:**

> Nesta PAP não há testes com utentes idosos reais. Os testes são feitos pelo aluno e por pessoas próximas em cenário simulado. Se no futuro houver testes com idosos, será obtido **consentimento informado por escrito** antes de qualquer recolha de dados ou sessão.

---

## 6. C3 — Orçamento

Copiar a tabela de [`ORCAMENTO.md`](ORCAMENTO.md) secção 3.

**Resumo para o formulário:** previsão máxima cerca de **230 €** (se for preciso comprar ecrã, áudio e SSD). Cenário preferido com empréstimos: cerca de **35–90 €** (principalmente a RAM). NUC e software = **0 €**.

---

## 7. C5 — Observações

**Texto sugerido:**

> Projeto **individual**. Não existe cliente externo nesta fase: trata-se de um protótipo escolar sem utentes reais integrados. Limites do trabalho: o RIC não diagnostica doenças nem prescreve medicação; não inclui locomoção nem braços; o núcleo é offline-first com LLM local opcional para conversa. Hardware principal reaproveitado (NUC5i3RYH). Testes sem idosos reais; se houver, com consentimento escrito. A função central a demonstrar é o sistema de lembretes fiáveis.

---

## Checklist antes de entregar a correção

- [ ] Corpo mínimo descrito (não só «sem locomoção»)  
- [ ] Hardware concreto (NUC5i3RYH + 16 GB + ecrã + áudio)  
- [ ] MVP vs extras explícito  
- [ ] Função única = lembretes  
- [ ] Tabela C3 preenchida (mesmo com 0 €)  
- [ ] C5 Observações preenchido  
- [ ] Consentimento: sem utentes reais nesta PAP  
