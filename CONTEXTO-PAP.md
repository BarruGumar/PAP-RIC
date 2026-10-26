# CONTEXTO DO PROJETO — RIC (PAP)

> Ficheiro de contexto para qualquer modelo de IA (Cursor, ChatGPT, Claude, etc.).
> **Colocar em:** `C:\Users\pedro\Desktop\PAP\CONTEXTO-PAP.md`
> Atualizar sempre que houver decisões importantes.

**Última atualização:** 2026-10-25 (arquitetura níveis 0–5; Mint XFCE; detalhe ops em `docs/ARQUITETURA.md`)  
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

## 8. Arquitetura (acordada 2026-10-25)

Documento completo: [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md).

```
Pessoa  ↔  Ecrã tactile kiosk (rosto; texto/botões só quando necessário)
                 ↕  http://127.0.0.1:8787  REST /api/v1 + WS /ws
        Um processo RIC (Python) — systemd ric.service
        /home/ric/ric-app  +  /home/ric/ric-data
        - core + reminders + db (SQLite: lembretes, gostos, 80 msgs+resumo, PIN hash)
        - voice: openWakeWord («RIC») + Whisper + Piper PT (+ fallback TTS)
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
| Hardware UI | PC reciclado + **ecrã tactile** HDMI/DP no mesmo PC |
| SO do protótipo / demo | **Linux Mint XFCE**; validar tactile em live USB |
| SO de desenvolvimento | Windows (ou outro) opcional; alvo de execução = Linux do RIC |
| Disco na máquina RIC | `/home/ric/ric-app/` + `/home/ric/ric-data/` |
| Rede UI↔cérebro | `http://127.0.0.1:8787` — REST `/api/v1` + WS `/ws` |
| Arranque | `ric.service` (systemd user) + kiosk XFCE **separado**; saída só com PIN |
| Offline-first | Núcleo local; Internet só funções opcionais (Telegram críticos, meteo, …) |
| LLM local | **`qwen2.5:3b` via Ollama**; timeout 8–12 s; core sobe sem Ollama |
| Tools LLM P1 | Ler lembretes, música, história, guardar gosto; **não** meds; Telegram ≠ tool |
| Cloud LLM | Não no núcleo |
| Processo | Um processo Python; UI estática servida pelo mesmo processo |
| UI Idle | Rosto + relógio + próximo lembrete; mais info sob procura |
| Rosto | idle, listening, thinking, speaking, alert, music, story |
| Memória | SQLite: lembretes (schema A) + gostos + 80 msgs + 1 resumo + confirmações |
| Voz | openWakeWord «RIC»; janela 6–8 s; barge-in corta TTS (não alertas); Whisper + Piper PT |
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

## 10. Hardware a explorar

**Padrão PAP (2026-10-25):** PC/laptop reciclado com **Linux Mint XFCE** + ecrã **tactile** (HDMI/DP) + microfone/colunas. Tudo no mesmo equipamento; UI em `127.0.0.1:8787`. Windows não é o SO da demonstração.

Ordem de interesse para o «cérebro» (LLM local):

1. **PC reaproveitado** com Linux leve e RAM suficiente para Ollama 3B + Whisper pequeno  
2. **Intel NUC / mini-PC usado** (ideal ≥ 16 GB RAM)  
3. **Raspberry Pi 5 + AI HAT** — só se o PC falhar e houver justificação  
4. **Arduino** — fora desta PAP (locomoção)  

Tablet separado **não** é o ecrã principal desta PAP (evita depender de Wi‑Fi local).

Inventário: `docs/INVENTARIO-HARDWARE.md` · Orçamento: `docs/ORCAMENTO.md` · Arquitetura/SO: `docs/ARQUITETURA.md`

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
- [x] Voz TTS: Piper (+ SAPI/espeak fallback) nos alertas; wake/STT ainda stub
- [ ] Wake-word + Whisper + Ollama tools
- [ ] PIN cuidador → Telegram/música/histórias
- [ ] Inventário físico + medições LLM reais
- [ ] Anexo I no formulário da escola (se ainda pendente)

---

## 14. Próximo passo

1. Seguir [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) (§6) e [`docs/PLANEAMENTO.md`](docs/PLANEAMENTO.md)  
2. Arquivar `ric/` → `archive/legacy/` e criar esqueleto novo  
3. 1.ª fatia: lembretes + API `:8787` + UI mínima; depois voz; depois extras  
4. Atualizar fichas em `docs/metas/` quando o comportamento real mudar  
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

`C:\Users\pedro\Desktop\PAP`  
Remoto GitHub: `https://github.com/BarruGumar/PAP-RIC.git`

Ficheiros importantes:
- `CONTEXTO-PAP.md` ← este ficheiro
- `docs/ARQUITETURA.md` ← sistema informático acordado
- `docs/PLANEAMENTO.md` ← calendário P1-crono
- `ric/` ← legado a mover para `archive/legacy/`; código novo segundo a arquitetura
- `docs/` (metas, guias, checklist, demo, inventário, tabela LLM, `docs/codigo/`)
