# CONTEXTO DO PROJETO — RIC (PAP)

> Ficheiro de contexto para qualquer modelo de IA (Cursor, ChatGPT, Claude, etc.).
> **Colocar em:** `C:\Users\pedro\OneDrive\Documentos\PAP\CONTEXTO-PAP.md`
> Atualizar sempre que houver decisões importantes.

**Última atualização:** 2026-10-03 (MVP `ric/` criado e testado com `py`)  
**Aluno:** Pedro Albuquerque  
**Curso:** Profissional de Informática de Sistemas  
**Trabalho:** PAP — Prova de Aptidão Profissional  
**Defesa prevista:** junho/julho (núcleo funcional até final de maio, se possível)

---

## 1. Nome e identidade

**RIC** — Robô Inteligente Companheiro  
**EN:** Robotic Interactive Companion  

Companheiro digital de apoio (principalmente a **idosos** / pessoas que precisam de auxílio):
- lembrar medicamentos, consultas e rotinas;
- fazer companhia (conversar, histórias, músicas);
- responder perguntas;
- valorizar **privacidade** com **LLM local**;
- priorizar **hardware reaproveitado**;
- servir também como estudo sobre **criação/gestão de LLMs locais** (aplicável a casas e empresas).

---

## 2. Objetivo geral

Desenvolver o RIC como sistema de apoio centrado na pessoa e na privacidade, com interação primeiro (companhia + lembretes + memória), autonomia offline sempre que possível, e documentação profissional para a PAP.  
A locomoção é **fase posterior**, só depois da interação estar boa.

---

## 3. Objetivos específicos (oficiais)

### 3.1 Interação e companhia
- Conversar de forma natural (voz e/ou texto)
- Contar histórias
- Reproduzir / “cantar” músicas
- Responder perguntas do dia a dia

### 3.2 Apoio a rotinas
- Agendar lembretes (medicamentos, consultas, tarefas)
- Alertar à hora certa (som + ecrã)
- Registar confirmação (“já tomei” / “adiar”)
- Consultar histórico simples de lembretes

### 3.3 Memória e personalização
- Guardar preferências (nome, rotinas, gostos)
- Manter memória de conversas (resumo + histórico recente)
- Usar essa memória em interações futuras

### 3.4 Privacidade e autonomia
- Funcionar offline nas funções essenciais (lembretes + conversa básica)
- Processar o máximo possível com LLM local
- Não enviar dados sensíveis para a cloud por defeito
- Modo cloud apenas opcional, explícito e desligável

### 3.5 Reaproveitamento de hardware
- Priorizar equipamentos velhos/parados (PC, tablet, NUC, áudio, câmara, etc.)
- Só comprar hardware novo quando o reaproveitado não cumprir o requisito
- Documentar inventário e justificar cada compra
- Dar nova função ao equipamento que não aguente a LLM (UI, backend leve, etc.)

### 3.6 Investigação (LLMs locais)
- Comparar abordagens (só local vs híbrido)
- Avaliar qualidade, latência, consumo, privacidade e gestão
- Extrair conclusões para uso doméstico e empresarial

### 3.7 Documentação PAP
- Arquitetura, implementação, testes, ética/privacidade, custos, limitações e melhorias futuras

---

## 4. Metas mensuráveis

| Meta | Critério de sucesso |
|---|---|
| Lembretes | Criar, disparar e confirmar ≥ 3 tipos de aviso |
| Conversa offline | ≥ 10 perguntas simples sem internet |
| Memória | Usa nome/preferências numa conversa seguinte |
| Privacidade | Local-first; cloud só com autorização |
| Companhia | Demo com história + música + diálogo |
| Reaproveitamento | ≥ 50% dos componentes principais reutilizados (ou justificação clara) |
| Estudo LLM | Tabela comparativa documentada |
| Demo PAP | Apresentação estável de 5–8 min |

---

## 5. Fora de âmbito (por agora)

- Diagnosticar doenças / substituir médico
- Medir pressão automaticamente (no MVP: só **lembrar** e eventualmente registar valor dito pela pessoa)
- Locomoção (fase extra)
- Braços / garra
- LLM enorme tipo ChatGPT completo 100% local em PC muito fraco

---

## 6. Arquitetura atual (direção)

```
Pessoa  ↔  Tablet/ecrã (rosto, chat, botões)
                 ↕
        Cérebro local (PC / NUC / Pi)
        - Backend de lembretes + memória (SQLite)
        - LLM local (Ollama)
        - STT/TTS (depois)
                 ↕ (opcional, desligado por defeito)
        LLM cloud (perguntas complexas)
                 ↕ (fase 2)
        Arduino (motores/sensores)
```

### Divisão de responsabilidades
| Camada | Função |
|---|---|
| **Backend** | Lembretes, horários, confirmações, memória estruturada |
| **LLM local** | Conversa, histórias, companhia, reformular avisos |
| **LLM cloud** | Só suplente opcional para perguntas difíceis |
| **Tablet** | Rosto / interface (cliente fino) |
| **Arduino** | Locomoção/sensores depois — não é obrigatório no MVP de interação |

**Regra de ouro:** segurança e lembretes **não dependem** da LLM nem da internet.

---

## 7. Decisões já tomadas

| Decisão | Estado |
|---|---|
| Nome oficial | **RIC** |
| Prioridade | Interação primeiro; locomoção depois |
| LLM local principal a testar/usar | **`qwen2.5:3b` via Ollama** (Pedro já testou e achou suficientemente boa) |
| Comparação opcional | `llama3.2:3b` / `qwen2.5:1.5b` se PC fraco / `qwen2.5:7b` se PC forte |
| Cloud | Opcional, não obrigatória |
| SO preferido em PC reciclado | Linux (quando for formatar) |
| Braço/garra | Futuro; se existir, via Arduino (não precisa Raspberry só por isso) |
| Medir pressão | Lembrete/registo — não diagnóstico médico |

---

## 8. Hardware a explorar

Ordem de interesse para LLM local + autonomia:

1. **Raspberry Pi 5 + AI HAT+ 2** (Hailo-10H) — forte para GenAI local  
2. **Intel NUC / mini-PC usado** (ideal 16 GB RAM)  
3. **PC reaproveitado** — usar o máximo possível; se for fraco demais para LLM, reutilizar como UI/backend/apoio  
4. **Tablet antigo** — rosto/interface  
5. **Arduino** — fase 2 (motores/sensores/garra)  

PCs muito antigos (início dos anos 2000 / 32-bit) provavelmente **não** correm bem LLM local útil.

---

## 9. Software / stack atual

### Já existente no repositório
- `ric/` — MVP de **lembretes locais** em Python + SQLite
- Comandos (neste Windows: usar `py`, não `python`):
  - `py -m ric demo`
  - `py -m ric run`
  - `py -m ric ui` ← interface web local (`http://127.0.0.1:8787/`)
  - `py -m ric add "Tomar medicamento" 18:00 --tipo medicamento`
  - `py -m ric list`
  - `py -m ric ok ID`
  - `py -m ric adiar ID`
- Dados em `ric/data/ric.db` (local, privado)
- Guia: `docs/GUIA-LEMBRETES-WINDOWS.md`
- Explicações detalhadas de cada ficheiro de código: `docs/codigo/` (atualizar sempre que o código mudar)

### Ferramentas em uso / a usar
- Python 3
- Ollama + Qwen2.5 3B
- SQLite
- Depois: FastAPI/Flask (UI), STT/TTS, possivelmente OpenCV
- Git para versões

### Modelos LLM (referência)
**Locais grátis (Ollama):** Qwen2.5, Llama 3.2, Gemma 2, Phi-3.5, Mistral, SmolLM  
**Cloud (freemium/pago):** GPT, Claude, Gemini, Groq — só suplente

---

## 10. Fases do projeto

**Fase A — Núcleo (agora)**  
Lembretes + LLM local + privacidade local-first  

**Fase B — Companhia**  
Histórias, músicas, memória de conversas, melhor voz/UI  

**Fase C — Investigação**  
Comparar LLMs / local vs híbrido; documentar conclusões  

**Fase D — Extra**  
Locomoção, sensores, cloud opcional, braço  

---

## 11. Estado atual (2026-10-03)

- [x] Conceito e objetivos definidos
- [x] Nome RIC
- [x] Privacidade e reaproveitamento como pilares
- [x] Ollama instalado no PC do Pedro
- [x] `qwen2.5:3b` testado — considerado suficientemente bom
- [x] MVP de lembretes em Python criado no repositório (`ric/`)
- [x] Comandos `demo` / `list` / `add` / `ok` / `adiar` testados no Windows com `py`
- [x] `py -m ric run` experimentado (alerta no terminal)
- [x] Interface web local de lembretes (`py -m ric ui`) — agendar + aviso à hora
- [x] Chat com Ollama (`qwen2.5:3b`) que agenda/confirma/adia via tools + frase no aviso
- [ ] Evoluir UI para “rosto”/companhia (além dos lembretes)
- [ ] Escolher hardware final do cérebro (Pi+HAT / NUC / PC reaproveitado)
- [ ] Inventário físico do que já existe em casa

---

## 12. Próximo passo técnico

1. ~~Criar MVP `ric/` e testar CLI no Windows~~  
2. ~~Experimentar `py -m ric run`~~  
3. ~~Interface web para agendar e ser avisado à hora (`py -m ric ui`)~~  
4. ~~Chat local (Ollama) que agenda e gera frase do aviso~~  
5. Evoluir ecrã para companheiro (rosto + voz) mantendo lembretes fiáveis  

---

## 13. Regras para qualquer IA que ajudar neste projeto

- Escrever em **português de Portugal**
- Manter âmbito realista para PAP
- Priorizar **interação + privacidade + reaproveitamento**
- Não empurrar locomoção/braços como caminho crítico
- Lembretes = backend fiável; LLM = conversa
- Não permitir que o sistema “prescreva” medicamentos ou diagnostique
- Documentar decisões neste ficheiro

---

## 14. Frase-guia

> O RIC é um companheiro de apoio centrado na pessoa e na privacidade: ajuda a lembrar o essencial, faz companhia com IA local, reaproveita equipamento sempre que possível, e só depois evolui para locomoção.

---

## 15. Pasta local do aluno

`C:\Users\pedro\OneDrive\Documentos\PAP`

Ficheiros importantes a manter nesta pasta:
- `CONTEXTO-PAP.md` ← este ficheiro
- código `ric/` (quando copiado/sincronizado)
- diário semanal da PAP
- capturas/testes (Ollama, lembretes, etc.)
