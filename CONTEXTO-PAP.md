# CONTEXTO DO PROJETO — RIC (PAP)

> Ficheiro de contexto para qualquer modelo de IA (Cursor, ChatGPT, Claude, etc.).
> No PC do Pedro a pasta do projeto é `C:\Users\pedro\Desktop\PAP`.
> Atualizar sempre que houver decisões importantes.

**Última atualização:** 2026-11-20 (hardware fechado: NUC5i3RYH; MVP + correções pré-projeto Gil; Chatterbox removido)
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

O trabalho desta PAP é **fazer o próprio RIC**: protótipo e funções que caibam no prazo. Vêm primeiro a interação, a privacidade e o hardware reaproveitado do projeto. Locomoção fica para depois.

### 2.2 Aplicação futura (ainda não existe na escola)

A escola poderá, mais tarde, recolher equipamentos eletrónicos e periféricos que já não sejam utilizados, em pontos de recolha ou através de uma possível parceria com o **Ponto Eletrão** (recolha e encaminhamento deste tipo de equipamentos).

Dois cursos podem ter um papel nesse processo:

| Curso | Papel possível |
|---|---|
| **TAS** (Técnico Auxiliar de Saúde) | Identificar um utente, avaliar necessidades e indicar soluções ou funcionalidades úteis para esse caso |
| **TIS** (Técnico de Informática — Sistemas) | Analisar os equipamentos recolhidos, avaliar o estado e decidir o que se reutiliza ou adapta. Os dados dos equipamentos poderão ser registados para facilitar a gestão e a reutilização |

Com necessidades reais e equipamento disponível, podem aparecer várias soluções. O RIC é **uma** delas.

Este processo **ainda não existe** na escola: sem recolha com este fim, sem utentes no projeto. TAS/TIS e utentes reais são visão futura, não entregáveis desta PAP.

---

## 3. Objetivo geral

Construir e testar o RIC como protótipo de apoio à pessoa, com privacidade e uso offline sempre que der. A prioridade é interação (companhia, lembretes, memória) e documentação séria para a PAP.

Cada função aprofunda-se à vez: o que faz, o que precisa, o que cabe no prazo. A lista completa de metas não é promessa de entrega.

### 3.1 Skills no Cursor (workflow)

- **Código** (features, bugs, refactors, reviews): usar **Ponytail** (`/ponytail`) — quase sempre. Exceção rara: spike exploratório ou pedido explícito em contrário.
- **Aprender enquanto faz** (defesa / entender o código): **Learning** (`/learning`) — estilo professor: boilerplate pela IA, decisões e núcleo com `TODO(human)` para o Pedro; uma pergunta de cada vez. Combinar com Ponytail. Desligar com “faz tu” quando quiser velocidade.
- **Figuras de sistema**: Diagram Design — ver `docs/design/arquitetura-ric.html`.
- **Prosa** (Anexo, relatório, texto para o orientador): Humanizer. Não reescrever specs técnicas densas (`ARQUITETURA`, tabelas de estado) só por estilo.

---

## 4. Metas de funcionalidades

Cada meta regista-se em [`docs/metas/`](docs/metas/README.md). A ficha diz o que é, como a pessoa a usa, como o Pedro a idealiza e o que não faz. Conversação e voz, lembretes, gestão de agenda, cantar música (reprodução da biblioteca), contar histórias, leitura de livros, recomendações de entretenimento, meteorologia e notícias, e atualizações e BackOffice já têm ficha. O foco desta PAP é o RIC.

Muitos utentes têm pouca literacia digital, por isso a forma principal é falar e ouvir (TTS e STT). Botões grandes e texto são apoio — quem ouve mal, ou quando o reconhecimento falha — e não substituem a voz.

Cantar música (reproduzir da biblioteca local), leitura de livros e recomendações de entretenimento entram nesta PAP até à entrega (18/06/2027). Recolha escolar, Ponto Eletrão, TAS/TIS, utentes, diagnóstico, prescrição, locomoção e braços continuam fora (secção 7). O estado na tabela descreve o protótipo em 2026-10-09.

### 4.1 Offline (sem Internet)

| Meta | Estado no protótipo |
|---|---|
| Conversação e voz | Ficha: [`docs/metas/conversacao-e-voz.md`](docs/metas/conversacao-e-voz.md). Fala natural em português de Portugal, como com uma pessoa: o RIC interpreta a intenção e não depende de uma lista de comandos. Protótipo novo (`ric/`): Piper TTS; botão **Falar** + wake contínuo openWakeWord (alvo **«ei RIC»**; agora temporário `hey_jarvis`); STT faster-whisper; LLM Ollama |
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

## 8. Arquitetura (acordada 2026-10-25)

Documento completo: [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

```
Pessoa  ↔  Ecrã tactile kiosk (rosto SVG estilo EVE + lab de expressões; texto/botões quando necessário)
                 ↕  http://127.0.0.1:8787  REST /api/v1 + WS /ws
        Um processo RIC (Python) — systemd ric.service
        /home/ric/ric-app  +  /home/ric/ric-data
        - core + reminders + db (SQLite: lembretes, gostos, 80 msgs+resumo, PIN hash)
        - voice: openWakeWord («ei RIC») + Whisper + Piper PT (+ fallback TTS)
        - llm: Ollama qwen2.5:3b + tools P1 (ler lembretes, música, história, gosto)
        - music (pastas + catalogo.json) + stories (txt/meta ± áudio)
        - caregiver (PIN + sessão timeout) + notify (Telegram D1+D3)
                 ⇣ (só críticos sem confirmação, se houver net)
        Telegram → cuidador (conteúdo mínimo)
```

### Divisão de responsabilidades
| Camada | Função |
|---|---|
| **core + reminders** | Estados, prioridades, lembretes fiáveis (sem LLM) |
| **LLM local** | Conversa + tools P1; meds só cuidador; histórias geradas = stretch |
| **voice** | Wake-word, STT, TTS locais; barge-in em conversa |
| **web** | Rosto (incl. music/story) + UI kiosk bloqueada |
| **notify** | Telegram na PAP (scheduler, não tool livre do LLM); canal próprio depois |
| **Arduino / locomoção** | Fora desta PAP |

**Regra de ouro:** lembretes e o núcleo offline **não dependem** da LLM nem da Internet. Legado → `archive/legacy/`; código novo em `ric/` segundo `docs/ARQUITETURA.md`.

---

## 9. Decisões já tomadas

| Decisão | Estado |
|---|---|
| Nome oficial | **RIC** — Robô Interativo Companheiro |
| Horizonte do plano 2026-10-25 | Só entregável da **PAP**; visão completa documentada à parte |
| Sucesso da defesa | Companheiro: voz + memória + música + histórias (critério C) |
| Utilizadores | Idoso (principal); cuidador (PIN local + aviso em falha crítica) |
| Prioridade | Interação primeiro; locomoção depois |
| Foco desta PAP | Protótipo do RIC. Recolha escolar, TAS/TIS e utentes = visão futura |
| Hardware cérebro | **Intel NUC5i3RYH** (i3-5010U) reaproveitado → **16 GB** DDR3L; DN2820FYK só reserva |
| Hardware UI | Ecrã **tactile** HDMI/DP no mesmo NUC (sem tablet à parte) |
| Função única júri | **Lembretes offline** (criar → disparar → Já fiz / Adiar) |
| MVP desta PAP | Voz offline PT + lembretes (sem LLM) + memória mínima + UI kiosk; resto = extra |
| Pré-projeto (correções Gil) | Textos em [`docs/CORRECOES-PRE-PROJETO.md`](docs/CORRECOES-PRE-PROJETO.md) |
| SO do protótipo / demo | **Linux Mint XFCE**; validar tactile em live USB |
| SO de desenvolvimento | Windows (ou outro) opcional; alvo de execução = Linux do RIC |
| Disco na máquina RIC | `/home/ric/ric-app/` + `/home/ric/ric-data/` |
| Rede UI↔cérebro | `http://127.0.0.1:8787` — REST `/api/v1` + WS `/ws` |
| Arranque | `ric.service` (systemd user) + kiosk XFCE **separado**; saída só com PIN |
| Offline-first | Núcleo local; Internet só funções opcionais (Telegram críticos, meteo, …) |
| LLM local | **`qwen2.5:3b` via Ollama**; timeout 8–12 s; core sobe sem Ollama |
| Qwen com entrada de áudio | Investigado em 2026-10-16. Fica de fora: não corre no Ollama, pede GPU. Nota em `docs/TABELA-LLMS.md` |
| Comparação opcional | `qwen2.5:7b` se a RAM chegar; `llama3.2:3b` / `qwen2.5:1.5b` se o 3B for fraco. A AMALIA-9B entra no teste a pedido do orientador. Só substitui o Qwen se agendar e couber. Ver `docs/FEEDBACK-ORIENTADOR.md` |
| Tools LLM P1 | Ler + **criar/apagar** lembretes não médicos; música, história, guardar gosto; **não** meds/críticos; Telegram ≠ tool |
| Cloud LLM | Não no núcleo |
| Processo | Um processo Python; UI estática servida pelo mesmo processo |
| UI Idle | Rosto + relógio + próximo lembrete; mais info sob procura |
| Rosto no código | Cara **EVE** no ecrã inteiro. Em repouso: RIC, horas e **próximo lembrete**. Botões ao toque, ou quando um lembrete dispara |
| Corpo físico (2026-11-12) | Gato de cabeça grande e tronco pequeno, parado, sem copiar uma personagem. Detalhe em `docs/estudos/VISUAL-E-CORPO.md` |
| Memória | SQLite: lembretes (schema A) + gostos + 80 msgs + 1 resumo + confirmações |
| Voz | Botão Falar + wake contínuo (openWakeWord; alvo **«ei RIC»**; temporário `hey jarvis`) + endpointing ~0,9 s; Whisper + Piper tugão medium **1.5.0**. Chatterbox descartado |
| Música | Pastas por género + `catalogo.json` ao arrancar |
| Histórias | `historias/*.txt` + meta; áudio opcional se existir |
| Lembretes | Default 3× ~2 min (cuidador altera); pausa/retoma música; críticos → Telegram |
| Cuidador | PIN 4–6 + hash + bloqueio após ~5 falhas; sessão 2–5 min + aviso 30 s |
| Telegram | Título + sem confirmação + hora; sem chat/áudio/GPS |
| Logs | Técnicos por defeito; `RIC_DEBUG=1` para frases; áudio não gravado |
| Backup | Diário local ~7 dias; cloud só depois com consentimento |
| Config | `.env` + `config.example.env`; PIN hash no SQLite |
| Ética | Não diagnostica nem aconselha doses |
| Código | Legado → `archive/legacy/`; app nova `ric/`; 1.º fatia = lembretes+API+UI |
| Braço/garra / locomoção | Fora desta PAP |
| Medir pressão | Lembrete/registo — não diagnóstico médico |

Detalhe completo nível 5: [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) secção 6.

---

## 10. Hardware (fechado 2026-11-20)

**Cérebro:** Intel **NUC5i3RYH** (Core i3-5010U), reaproveitado, expansão a **16 GB** DDR3L-1600 SO-DIMM.  
**Reserva:** NUC **DN2820FYK** (Celeron N2820) — não sustenta LLM + STT juntos; não é a demo.  
**UI / áudio:** ecrã **tactile** no mesmo NUC + microfone e colunas (emprestar ou comprar).  
**SO:** **Linux Mint XFCE**; UI em `127.0.0.1:8787`. Windows só no PC de desenvolvimento.  
**Corpo mínimo:** estrutura parada tipo gato — [`docs/estudos/VISUAL-E-CORPO.md`](docs/estudos/VISUAL-E-CORPO.md).  
**Fora:** Raspberry Pi / AI HAT (só se o NUC falhar, com justificação); Arduino / locomoção.

Inventário + comparação dos NUCs: [`docs/INVENTARIO-HARDWARE.md`](docs/INVENTARIO-HARDWARE.md) · Orçamento C3: [`docs/ORCAMENTO.md`](docs/ORCAMENTO.md) · Correções pré-projeto: [`docs/CORRECOES-PRE-PROJETO.md`](docs/CORRECOES-PRE-PROJETO.md)

---

## 11. Software / stack

### Direção (reescrita)
- **Linux Mint XFCE** (`ric.service` + kiosk XFCE separado)
- Python 3 + SQLite + HTTP em `:8787` (rosto + REST + WS) — um processo
- Ollama + Qwen2.5 3B + tools P1
- openWakeWord + Whisper + Piper PT (+ fallback TTS sistema)
- UI: HTML/CSS/JS kiosk bloqueado
- `notify` Telegram (scheduler D1+D3)
- Arquitetura: [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md)

### Legado no repositório (a arquivar)
- `ric/` atual → `archive/legacy/` (referência)
- `voz-teste/` — experiências Piper
- Docs de código em `docs/codigo/` — atualizar quando o código novo existir

### Não nesta PAP
- React/Next como UI principal, Docker obrigatório, cloud LLM no núcleo, microsserviços, ROS

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

### Etapas (P1-crono, 2026-10-25)

| Até | Foco |
|---|---|
| 23/10/2026 | Planificação (Anexo I) |
| Etapa 1 (08/01/2027) | Reescrita + Mint XFCE + 1.ª fatia lembretes/API/UI → voz + Ollama tools |
| Etapa 2 (26/03/2027) | Música + histórias + gostos/memória + PIN cuidador + meds só cuidador |
| Etapa 3 (21/05/2027) | Telegram D1+D3 + polish + testes + docs/ética; stretch se sobrar |
| 18/06/2027 | Relatório |
| 09/07/2027 | Defesa |

Detalhe: [`docs/PLANEAMENTO.md`](docs/PLANEAMENTO.md) · Arquitetura: [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).  
Nota: [`docs/PLANEAMENTO-ETAPA-1.md`](docs/PLANEAMENTO-ETAPA-1.md) ainda descreve o protótipo antigo (2026-10-09); prevalece o P1-crono e a arquitetura de 2026-10-25.

BackOffice e canal próprio de monitorização **não** entram como produto nestas etapas. O módulo `notify` fica preparado para os substituir no projeto final.

---

## 13. Estado atual (2026-10-25)

- [x] Conceito, nome, visão futura vs PAP
- [x] Arquitetura níveis 0–5 acordada (`docs/ARQUITETURA.md`)
- [x] Planeamento P1-crono (`docs/PLANEAMENTO.md`)
- [x] SO alvo: **Mint XFCE**; Windows só desenvolvimento opcional
- [x] Detalhe ops: API 8787, schema, voz, kiosk, PIN, tools, backup, ordem de fatias
- [x] Ollama + `qwen2.5:3b` testados
- [x] Protótipo legado em `ric/` (a arquivar; não é a base final)
- [x] Experiências de voz Piper em `voz-teste/`
- [ ] Instalar/validar Mint XFCE + tactile no PC do protótipo
- [x] Arquivar legado (`archive/legacy/`) e reescrita iniciada
- [x] 1.ª fatia: API `:8787` + WS `/ws` + SQLite lembretes + UI Idle (regra 2A)
- [x] Voz TTS: Piper tugão **medium 1.5.0** (+ SAPI/espeak fallback) nos alertas
- [x] Voz wake→STT: botão Falar + `VoiceSession` + API `/voice/*` + faster-whisper
- [x] LLM Ollama `qwen2.5:3b` na conversa por voz (tools: listar/criar/apagar lembretes não médicos)
- [x] Chatterbox testado e **descartado** (CPU lento / deps pesadas); Piper é o TTS do projeto
- [x] Promovido tugão 1.5.0 a default (A/B vs 1.0.0); sem rotina de updates (cadência irregular)
- [x] Wake contínuo openWakeWord + sounddevice (loop provado com `hey_jarvis`; botão Falar fallback)
- [x] Roteiro Colab + `py -m ric wake-install` para «ei RIC» ([`docs/ROTEIRO-WAKE-EI-RIC.md`](docs/ROTEIRO-WAKE-EI-RIC.md))
- [ ] Correr Colab, instalar `ric.onnx` e validar «ei RIC» no microfone
- [ ] PIN cuidador → Telegram/música/histórias
- [ ] Inventário físico + medições LLM reais
- [ ] Anexo I no formulário da escola (se ainda pendente)

---

## 14. Próximo passo

1. Seguir [`docs/ROTEIRO-WAKE-EI-RIC.md`](docs/ROTEIRO-WAKE-EI-RIC.md) (Colab → `wake-install` → testar «ei RIC»)
2. Tools P1 em falta (música/história/gosto) e PIN cuidador
3. Atualizar fichas em `docs/metas/` quando o comportamento real mudar
4. Relatório PAP (ética, custos, limitações, melhorias)

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

## 17. Pasta do projeto

No PC do Pedro a pasta do projeto é `C:\Users\pedro\Desktop\PAP`. Aí estão `CONTEXTO-PAP.md`, `ric/`, `docs/` e `testar-voz.bat`. Os comandos correm nessa pasta.  
Remoto GitHub: `https://github.com/BarruGumar/PAP-RIC.git`

Ficheiros importantes:
- `CONTEXTO-PAP.md` ← este ficheiro
- `docs/ARQUITETURA.md` ← sistema informático acordado
- `docs/PLANEAMENTO.md` ← calendário P1-crono
- `ric/` ← legado a mover para `archive/legacy/`; código novo segundo a arquitetura
- `docs/` (metas, guias, checklist, demo, inventário, tabela LLM, `docs/codigo/`)
