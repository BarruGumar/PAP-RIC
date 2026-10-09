# CONTEXTO DO PROJETO — RIC (PAP)

> Ficheiro de contexto para qualquer modelo de IA (Cursor, ChatGPT, Claude, etc.).
> **Colocar em:** `C:\Users\pedro\OneDrive\Documentos\PAP\CONTEXTO-PAP.md`
> Atualizar sempre que houver decisões importantes.

**Última atualização:** 2026-10-09 (planeamento em `docs/PLANEAMENTO.md`; rascunho do Anexo I; calendário das etapas na secção 12; orçamento e tablet)  
**Aluno:** Pedro Albuquerque  
**Curso:** Profissional de Técnico/a de Informática — Sistemas (turma 3-TIS)  
**Orientador:** Gil Ribeiro  
**Trabalho:** PAP — Prova de Aptidão Profissional  
**Calendário:** provisório. Fonte: COORD.007 Regulamento da PAP 2025/26, art.º 8.º, versão de 03/10/2026. O regulamento 2026/27 ainda não foi publicado. A Direção Pedagógica indicou que os prazos se mantêm iguais aos de 2025/26; como o mesmo dia do mês cai um dia da semana mais tarde, cada prazo passa para a sexta-feira dessa semana.

---

## 1. Nome e identidade

**RIC** — Robô Interativo Companheiro  
**EN:** Robotic Interactive Companion  

Companheiro digital de apoio (principalmente a **idosos** / pessoas que precisam de auxílio):
- lembrar medicamentos, consultas e rotinas;
- fazer companhia (conversar, histórias, músicas);
- responder perguntas;
- valorizar **privacidade** com **LLM local**;
- priorizar **hardware reaproveitado**;
- servir também como estudo sobre **criação/gestão de LLMs locais** (aplicável a casas e empresas).

O RIC usa, sempre que possível, equipamentos eletrónicos e periféricos reciclados ou reaproveitados.

---

## 2. Visão e âmbito desta PAP

### 2.1 Nesta PAP

O foco é **desenvolver o próprio RIC**: criar e testar o protótipo e as funcionalidades que forem realistas no prazo. Interação, privacidade e reaproveitamento de hardware do próprio projeto vêm primeiro. A locomoção é fase posterior.

### 2.2 Aplicação futura (ainda não existe na escola)

A escola poderá, mais tarde, recolher equipamentos eletrónicos e periféricos que já não sejam utilizados, em pontos de recolha ou através de uma possível parceria com o **Ponto Eletrão** (recolha e encaminhamento deste tipo de equipamentos).

Dois cursos podem ter um papel nesse processo:

| Curso | Papel possível |
|---|---|
| **TAS** (Técnico Auxiliar de Saúde) | Identificar um utente, avaliar necessidades e indicar soluções ou funcionalidades úteis para esse caso |
| **TIS** (Técnico de Informática — Sistemas) | Analisar os equipamentos recolhidos, avaliar o estado e decidir o que se reutiliza ou adapta. Os dados dos equipamentos poderão ser registados para facilitar a gestão e a reutilização |

A partir das necessidades e dos equipamentos disponíveis poderão surgir várias soluções tecnológicas. O RIC é **uma** dessas soluções possíveis.

Este processo **não está implementado**. Não há sistema de recolha com este objetivo, nem utentes integrados no projeto. A colaboração TAS/TIS e o uso do RIC por utentes são visão e aplicação futura, não entregáveis desta PAP.

---

## 3. Objetivo geral

Desenvolver e testar o RIC como protótipo de apoio centrado na pessoa e na privacidade, com interação primeiro (companhia + lembretes + memória), autonomia offline sempre que possível, e documentação profissional para a PAP.

As funcionalidades aprofundam-se uma a uma ao longo do desenvolvimento: como deve funcionar, que recursos precisa e o que cabe no prazo. Não se promete implementar a lista inteira de metas.

---

## 4. Metas de funcionalidades

Cada meta regista-se em [`docs/metas/`](docs/metas/README.md). A ficha diz o que é, como a pessoa a usa, como o Pedro a idealiza e o que não faz. Conversação e voz, lembretes, gestão de agenda, cantar música (reprodução da biblioteca), contar histórias, leitura de livros, recomendações de entretenimento, meteorologia e notícias, e atualizações e BackOffice já têm ficha. O foco desta PAP é o RIC.

A voz (TTS e STT) é a forma principal de uso, porque a literacia digital de muitos idosos é baixa. Falar e ouvir é uma das melhores formas de interagirem com o RIC. Botões grandes e texto são apoio (quem ouve mal, ou quando o reconhecimento falha). Não substituem a voz.

Cantar música (reproduzir da biblioteca local), leitura de livros e recomendações de entretenimento entram nesta PAP até à entrega (18/06/2027). Recolha escolar, Ponto Eletrão, TAS/TIS, utentes, diagnóstico, prescrição, locomoção e braços continuam fora (secção 7). O estado na tabela descreve o protótipo em 2026-10-09.

### 4.1 Offline (sem Internet)

| Meta | Estado no protótipo |
|---|---|
| Conversação e voz | Ficha: [`docs/metas/conversacao-e-voz.md`](docs/metas/conversacao-e-voz.md). Fala natural em português de Portugal, como com uma pessoa: o RIC interpreta a intenção e não depende de uma lista de comandos. Protótipo: chat local; TTS Windows SAPI; STT no browser. Ainda frágeis |
| Lembretes | Ficha: [`docs/metas/lembretes.md`](docs/metas/lembretes.md). Ideal (não feito): na entrega já vêm os lembretes importantes, personalizados à pessoa; os auxiliares de saúde alteram-nos pelo BackOffice. Protótipo: criar, disparar, confirmar e adiar. Não dependem da LLM nem da Internet |
| Gestão de agenda | Ficha: [`docs/metas/gestao-de-agenda.md`](docs/metas/gestao-de-agenda.md). Ideal (não feito): o RIC tem acesso ao tempo e à agenda da pessoa, anota o que ela quiser (consultas, compromissos) e lembra. Hoje só há lembretes com hora, não uma agenda |
| Reprodução de músicas | Cantar música é o nome desta meta: reproduzir da biblioteca local. Ficha: [`docs/metas/reproducao-e-canto.md`](docs/metas/reproducao-e-canto.md). Ideal (nuvem não feita): grande biblioteca local de vários géneros, gerida e atualizada pela nuvem, baseada no gosto do utente. Protótipo: biblioteca offline por géneros em `ric/musica/` (pausa, continua, recomeço, volume). A busca automática no BackOffice é ideia por avaliar, não está feita |
| Canto de músicas | O mesmo que reproduzir da biblioteca local. Não é uma função à parte. Ficha: [`docs/metas/reproducao-e-canto.md`](docs/metas/reproducao-e-canto.md). Nuvem e busca automática não estão feitas |
| Contar histórias | Ficha: [`docs/metas/contar-historias.md`](docs/metas/contar-historias.md). Ideal (biblioteca não feita): algumas histórias simples guardadas localmente. Criar na hora é a explorar; se forem criadas, guardam-se. Protótipo: história curta via LLM local. Não há biblioteca nem armazenamento de histórias novas |
| Leitura de livros | Ficha: [`docs/metas/leitura-de-livros.md`](docs/metas/leitura-de-livros.md). Ideal (não feito): alguns livros digitais armazenados; o RIC lê em voz, de forma interessante, com música de ambiente. Vozes diferentes são ideia a explorar. O Senhor dos Anéis ainda está protegido e não entra no protótipo; só domínio público ou textos com autorização |
| Recomendações de entretenimento | Ficha: [`docs/metas/recomendacoes-de-entretenimento.md`](docs/metas/recomendacoes-de-entretenimento.md). Ideal (não feito): recomendar um filme, série, jogo ou outro entretenimento a partir dos gostos e do estado de espírito dessa hora. Offline ou online ainda por descrever pelo Pedro |

### 4.2 Online (só com Internet; opcionais)

| Meta | Estado no protótipo |
|---|---|
| Meteorologia | Ficha: [`docs/metas/meteorologia-e-noticias.md`](docs/metas/meteorologia-e-noticias.md). Ideal (não feito): ver e dizer a meteorologia do dia, da semana, etc. Guardar a previsão da semana e dizer a precisão é ideia a explorar, não está feita |
| Notícias | Ficha: [`docs/metas/meteorologia-e-noticias.md`](docs/metas/meteorologia-e-noticias.md). Ideal (não feito): ler e dizer notícias atuais |
| Atualizações | Ficha: [`docs/metas/atualizacoes-e-backoffice.md`](docs/metas/atualizacoes-e-backoffice.md). É a comunicação e o envio de dados do RIC para o BackOffice da escola. Não é atualização de software. Não está feito. O foco da PAP é o RIC |
| Receção e envio de dados pelo BackOffice | Ficha: [`docs/metas/atualizacoes-e-backoffice.md`](docs/metas/atualizacoes-e-backoffice.md). Ideal (não feito): o RIC comunica com o sistema da escola, a que os auxiliares de saúde e os informáticos (TAS e TIS) hão de ter acesso. O processo escolar ainda não existe. O protótipo de BackOffice é posterior e só se possível. A estrutura detalhada fica para depois. O foco da PAP é o RIC |

Cloud e BackOffice não são obrigatórios. Dados sensíveis não saem para a nuvem por defeito.

---

## 5. Objetivos específicos (oficiais)

### 5.1 Interação e companhia
- Conversar como com uma pessoa, em português de Portugal. A voz (TTS e STT) é a forma principal, por literacia digital. O RIC interpreta o que é dito, sem lista de comandos. Botões grandes e texto são apoio. Ficha: [`docs/metas/conversacao-e-voz.md`](docs/metas/conversacao-e-voz.md)
- Contar histórias. Ficha: [`docs/metas/contar-historias.md`](docs/metas/contar-historias.md). Ideal: histórias simples locais. Criar na hora é a explorar; as novas guardam-se. A biblioteca e esse armazenamento não estão feitos
- Cantar música, que é reproduzir da biblioteca local. Ficha: [`docs/metas/reproducao-e-canto.md`](docs/metas/reproducao-e-canto.md). Nuvem e busca automática não estão feitas
- Responder perguntas do dia a dia

### 5.2 Apoio a rotinas
- Agendar lembretes (medicamentos, consultas, tarefas). Ficha: [`docs/metas/lembretes.md`](docs/metas/lembretes.md). O ideal de entrega personalizada e de alteração pelos auxiliares via BackOffice ainda não está feito
- Alertar à hora certa (som + ecrã)
- Registar confirmação (“já tomei” / “adiar”)
- Consultar histórico simples de lembretes

### 5.3 Memória e personalização
- Guardar preferências (nome, rotinas, gostos)
- Manter memória de conversas (resumo + histórico recente)
- Usar essa memória em interações futuras

### 5.4 Privacidade e autonomia
- Funcionar offline nas funções essenciais (lembretes + conversa básica)
- Processar o máximo possível com LLM local
- Não enviar dados sensíveis para a cloud por defeito
- Modo cloud apenas opcional, explícito e desligável

### 5.5 Reaproveitamento de hardware
- Priorizar equipamentos velhos/parados (PC, tablet, NUC, áudio, câmara, etc.)
- Só comprar hardware novo quando o reaproveitado não cumprir o requisito
- Documentar inventário e justificar cada compra
- Dar nova função ao equipamento que não aguente a LLM (UI, backend leve, etc.)

### 5.6 Investigação (LLMs locais)
- Comparar abordagens (só local vs híbrido)
- Avaliar qualidade, latência, consumo, privacidade e gestão
- Extrair conclusões para uso doméstico e empresarial

### 5.7 Documentação PAP
- Arquitetura, implementação, testes, ética/privacidade, custos, limitações e melhorias futuras

---

## 6. Metas mensuráveis do protótipo atual

Critérios do que já se consegue demonstrar. As metas da secção 4 que estão “por definir” **não** entram aqui até serem escolhidas e implementadas.

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

## 7. Fora de âmbito (por agora)

- Diagnosticar doenças / substituir médico
- Medir pressão automaticamente (no MVP: só **lembrar** e eventualmente registar valor dito pela pessoa)
- Prescrever medicação
- Sistema de recolha de equipamentos na escola, parceria com o Ponto Eletrão, avaliação de utentes pelo TAS e gestão escolar de equipamentos pelo TIS (visão futura, secção 2.2)
- Utentes reais integrados no projeto
- Locomoção (fase extra)
- Braços / garra
- LLM enorme tipo ChatGPT completo 100% local em PC muito fraco

---

## 8. Arquitetura atual (direção)

```
Pessoa  ↔  Tablet/ecrã (rosto, chat, botões)
                 ↕
        Cérebro local (PC / NUC / Pi)
        - Backend de lembretes + memória (SQLite)
        - Watchdog de lembretes (thread no servidor UI)
        - LLM local (Ollama)
        - TTS (Windows SAPI) + STT no browser (forma principal de uso; protótipo ainda frágil)
                 ↕ (opcional, desligado por defeito)
        LLM cloud (perguntas complexas)
                 ↕ (fase extra)
        Arduino (motores/sensores)
```

### Divisão de responsabilidades
| Camada | Função |
|---|---|
| **Backend** | Lembretes, horários, confirmações, memória estruturada, watchdog |
| **LLM local** | Conversa, histórias, companhia, tools (agendar/música/perfil) |
| **LLM cloud** | Só suplente opcional para perguntas difíceis |
| **Tablet** | Rosto / interface (cliente fino) |
| **Arduino** | Locomoção/sensores depois — não é obrigatório no MVP de interação |

**Regra de ouro:** segurança e lembretes **não dependem** da LLM nem da internet.

---

## 9. Decisões já tomadas

| Decisão | Estado |
|---|---|
| Nome oficial | **RIC** — Robô Interativo Companheiro |
| Prioridade | Interação primeiro; locomoção depois |
| Foco desta PAP | Protótipo do RIC e funcionalidades testáveis. Recolha escolar, TAS/TIS e utentes ficam como visão futura |
| LLM local principal a testar/usar | **`qwen2.5:3b` via Ollama** (Pedro já testou e achou suficientemente boa) |
| Comparação opcional | `llama3.2:3b` / `qwen2.5:1.5b` se PC fraco / `qwen2.5:7b` se PC forte |
| Cloud | Opcional, não obrigatória |
| Servidor UI | **stdlib** `http.server` (sem FastAPI/Docker nesta fase) |
| Memória | SQLite: tabelas `perfil` + `conversas` (+ `confirmacoes`) |
| Voz | Forma principal de uso (TTS e STT), por literacia digital. Fala natural em português de Portugal: o RIC interpreta a intenção, sem lista de comandos. Protótipo: TTS Windows SAPI; STT via Web Speech API no browser. Botões e texto são apoio. Ficha: `docs/metas/conversacao-e-voz.md` |
| SO preferido em PC reciclado | Linux (quando for formatar) |
| Braço/garra | Futuro; se existir, via Arduino (não precisa Raspberry só por isso) |
| Medir pressão | Lembrete/registo — não diagnóstico médico |

---

## 10. Hardware a explorar

Ordem de interesse para LLM local + autonomia:

1. **Raspberry Pi 5 + AI HAT+ 2** (Hailo-10H) — forte para GenAI local  
2. **Intel NUC / mini-PC usado** (ideal 16 GB RAM)  
3. **PC reaproveitado** — usar o máximo possível; se for fraco demais para LLM, reutilizar como UI/backend/apoio  
4. **Tablet antigo** — rosto/interface  
5. **Arduino** — fase extra (motores/sensores/garra)  

Inventário a preencher: `docs/INVENTARIO-HARDWARE.md`

Orçamento e ligação do tablet sem Internet: `docs/ORCAMENTO.md`

O inventário deste projeto regista o hardware do protótipo. Não é o registo escolar de equipamentos recolhidos (esse processo ainda não existe).

---

## 11. Software / stack atual

### Já existente no repositório
- `ric/` — lembretes + chat + música + memória + UI companheiro
- Comandos (neste Windows: usar `py`, não `python`):
  - `py -m ric demo`
  - `py -m ric run`
  - `py -m ric ui` ← interface web local (`http://127.0.0.1:8787/`)
  - `py -m ric add "Tomar medicamento" 18:00 --tipo medicamento`
  - `py -m ric list`
  - `py -m ric ok ID`
  - `py -m ric adiar ID`
- Dados em `ric/data/ric.db` (local, privado)
- Guias: `docs/GUIA-LEMBRETES-WINDOWS.md`, `docs/CHECKLIST-REGRESSAO.md`, `docs/GUIAO-DEMO.md`
- Inventário: `docs/INVENTARIO-HARDWARE.md`
- Estudo LLM: `docs/TABELA-LLMS.md`
- Explicações de código: `docs/codigo/`

### Ferramentas em uso / a usar
- Python 3 + SQLite + stdlib HTTP
- Ollama + Qwen2.5 3B
- TTS local (SAPI no Windows); STT no browser
- Git para versões
- **Não** nesta fase: FastAPI/Docker/cloud obrigatória

### Modelos LLM (referência)
**Locais grátis (Ollama):** Qwen2.5, Llama 3.2, Gemma 2, Phi-3.5, Mistral, SmolLM  
**Cloud (freemium/pago):** GPT, Claude, Gemini, Groq — só suplente

---

## 12. Calendário provisório 2026/27

O processo, as etapas e o tempo estão em [`docs/PLANEAMENTO.md`](docs/PLANEAMENTO.md). As fichas em [`docs/metas/`](docs/metas/README.md) dizem o quê; o planeamento diz como e quando.

| Prazo | O que entregar |
|---|---|
| 23/10/2026 | Planificação do projeto (Anexo I) ao orientador. Até esta data só se planifica |
| 27/11/2026 | Aceitação dos projetos pelo Conselho Pedagógico |
| 08/01/2027 | 1.º relatório intercalar (Anexo II) + autoavaliação (Anexo IV) — fim da etapa 1 |
| 26/03/2027 | 2.º relatório intercalar + autoavaliação — fim da etapa 2 |
| 21/05/2027 | 3.º relatório intercalar + autoavaliação — fim da etapa 3 |
| 18/06/2027 | Relatório final e entrega do trabalho (impresso + digital) |
| até 09/07/2027 | Apresentação e defesa perante o júri (30 min) |

Quando o regulamento 2026/27 for aprovado, estas datas podem mudar.

### Etapas

| Até | Foco |
|---|---|
| 23/10/2026 | Só a planificação para aprovarem o projeto. Não se implementa funcionalidade nova |
| Etapa 1 (08/01/2027) | Voz estável. Conversação por voz, lembretes pedidos em fala livre e avisados em voz, cantar música da biblioteca local, história curta já existente mais um pequeno conjunto de histórias guardadas. Pormenor em [`docs/PLANEAMENTO-ETAPA-1.md`](docs/PLANEAMENTO-ETAPA-1.md) |
| Etapa 2 (26/03/2027) | Agenda (dia, consulta, compromisso, e a lembrança sai daí) e leitura de livros em voz, com música de ambiente. Livros de domínio público ou com autorização. Vozes diferentes por personagem só se a leitura simples já estiver estável |
| Etapa 3 (21/05/2027) | Recomendações a partir dos gostos e do que está no robô; meteorologia do dia e da semana; notícias atuais. A previsão guardada para quando cai a Internet fica se a meteorologia em direto já funcionar. Testes, privacidade e limites |
| 18/06/2027 | Relatório |
| 09/07/2027 | Defesa |

O BackOffice não entra nestas etapas. O foco é o RIC. Um protótipo de envio de dados, se sobrar tempo depois de maio, fica como extra. A estrutura do BackOffice não se desenha agora. Criar histórias novas na hora e a busca automática de músicas no BackOffice são ideias a explorar, não trabalho calendarizado.

### Fases técnicas (conteúdo, não datas fixas de funcionalidade)

A ordem com datas é a tabela de etapas acima e [`docs/PLANEAMENTO.md`](docs/PLANEAMENTO.md).

**Fase A — Núcleo**  
Lembretes + LLM local + privacidade local-first + watchdog UI  

**Fase B — Companhia**  
Histórias, músicas, memória de conversas, UI/rosto, TTS  

**Fase C — Investigação**  
Comparar LLMs / local vs híbrido; documentar conclusões  

**Fase D — Extra**  
Locomoção, sensores, cloud opcional e braço. Meteorologia e notícias entram na etapa 3. Atualizações e BackOffice não entram nas etapas; o foco da PAP é o RIC

---

## 13. Estado atual (2026-10-09)

- [x] Conceito e objetivos definidos
- [x] Nome RIC — Robô Interativo Companheiro
- [x] Visão futura (recolha, Ponto Eletrão, TAS/TIS) separada do âmbito desta PAP
- [x] Privacidade e reaproveitamento como pilares
- [x] Ollama instalado no PC do Pedro
- [x] `qwen2.5:3b` testado — considerado suficientemente bom
- [x] MVP de lembretes em Python (`ric/`)
- [x] Interface web local (`py -m ric ui`) — agendar + aviso à hora
- [x] Chat com Ollama + tools (lembretes + música + perfil)
- [x] Player offline (pausa / continua / do começo / volume)
- [x] Watchdog de lembretes no servidor (beep/TTS + log)
- [x] Perfil + histórico de chat em SQLite
- [x] UI companheiro (rosto simples, botões grandes, a11y)
- [x] TTS nos avisos + STT no browser (ainda frágeis; a voz é a forma principal de uso)
- [x] Docs: checklist, tabela LLM, inventário, guião demo
- [ ] Preencher medições reais na tabela LLM
- [ ] Escolher hardware final do cérebro (Pi+HAT / NUC / PC reaproveitado)
- [ ] Inventário físico preenchido com o que existe em casa
- [ ] Anexo I (planificação) — texto-base neste ficheiro; formulário da escola ainda por preencher

---

## 14. Próximo passo

1. Transcrever o rascunho [`docs/ANEXO-I-RASCUNHO.md`](docs/ANEXO-I-RASCUNHO.md) para o formulário oficial do Anexo I (prazo 23/10/2026). O planeamento está em [`docs/PLANEAMENTO.md`](docs/PLANEAMENTO.md)  
2. Descrever cada meta em `docs/metas/`, com o que o Pedro disser (a conversação e voz já tem ficha)  
3. Correr `docs/CHECKLIST-REGRESSAO.md` e ensaiar `docs/GUIAO-DEMO.md`  
4. Preencher `docs/TABELA-LLMS.md` e `docs/INVENTARIO-HARDWARE.md` com dados reais  
5. Relatório PAP (ética, custos, limitações, melhorias)

---

## 15. Regras para qualquer IA que ajudar neste projeto

- Escrever em **português de Portugal**
- Manter âmbito realista para PAP
- Priorizar **interação + privacidade + reaproveitamento**
- Não empurrar locomoção/braços como caminho crítico
- Não tratar recolha escolar, Ponto Eletrão, TAS/TIS ou utentes como funcionalidades já existentes
- Lembretes = backend fiável; LLM = conversa
- Não permitir que o sistema “prescreva” medicamentos ou diagnostique
- Não marcar como feitas as metas da secção 4 que estão “por definir”
- Documentar decisões neste ficheiro
- Manter `docs/codigo/` alinhado com o código

---

## 16. Frase-guia

> O RIC é um companheiro interativo, centrado na pessoa e na privacidade. Nesta PAP desenvolve-se e testa-se o protótipo: ajuda a lembrar o essencial, faz companhia com IA local e reaproveita equipamento sempre que possível. A recolha de equipamentos na escola, a colaboração entre TAS e TIS e o uso por utentes são uma aplicação futura possível.

---

## 17. Pasta local do aluno

`C:\Users\pedro\OneDrive\Documentos\PAP`

Ficheiros importantes:
- `CONTEXTO-PAP.md` ← este ficheiro
- código `ric/`
- `docs/` (guias, checklist, demo, inventário, tabela LLM, fichas em `docs/metas/`, explicações de código)
- diário semanal da PAP
