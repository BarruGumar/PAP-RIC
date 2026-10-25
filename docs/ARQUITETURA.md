# Arquitetura do RIC (PAP)

**Data das decisões:** 2026-10-25 (níveis 0–5)  
**Âmbito:** entregável da PAP (até defesa ~julho 2027).  
**Fonte:** planeamento grelhado com o Pedro; resumo também em [`CONTEXTO-PAP.md`](../CONTEXTO-PAP.md) e [`PLANEAMENTO.md`](PLANEAMENTO.md).

O código legado em `ric/` será **arquivado** (`archive/legacy/`) e o sistema **reescrito** segundo este documento. Reutilizam-se conteúdos (música, vozes, ideias), não a estrutura antiga.

---

## 1. Nível 0 — Propósito

| Decisão | Escolha |
|---|---|
| Horizonte deste plano | Só a **PAP** (opção B) |
| Utilizador principal | Idoso: companhia + rotina |
| Utilizador secundário | Cuidador: configura e é avisado em falhas críticas |
| Sucesso da defesa | Experiência de **companheiro** (voz, memória, música, histórias) |
| Visão completa (BackOffice, canal próprio, recolha escolar) | Fora da implementação desta PAP |

---

## 2. Nível 1 — Experiência e restrições

| Decisão | Escolha |
|---|---|
| Interação | **Voz primeiro**; ecrã = rosto/estados; texto e botões só quando necessário |
| Ativação | Palavra-chave **«RIC»** + janela de comando; botão como fallback |
| Hardware | PC/laptop reciclado + **ecrã tactile** (HDMI/DP + USB) no mesmo PC + microfone/colunas |
| SO alvo (demo / protótipo) | **Linux Mint XFCE** |
| SO de desenvolvimento | Windows (ou outro) **opcional** no PC de trabalho do aluno; o código deve correr no Linux do RIC |
| Ligação rosto ↔ cérebro | Browser kiosk em `http://127.0.0.1:8787` — **sem Internet e sem Wi‑Fi no núcleo** |
| Rede | Offline-first: núcleo local; Internet só para funções **opcionais** acordadas |
| Privacidade | LLM e dados no dispositivo; sem diagnóstico nem prescrição |

**Porquê Mint XFCE:** leve, amigável, boa para tactile e drivers em PC antigo; arranque com `systemd` + Chromium/Firefox em kiosk. Validar o ecrã tactile com live USB antes de formatar.

**Internet (só o acordado):**

- **Must híbrido:** aviso ao cuidador via Telegram se lembrete **crítico** não for confirmado após N avisos (e houver net; senão fila/log).
- **Outras metas online** (meteo, notícias, BackOffice, cloud LLM, sync cloud): só se explícitas e opcionais; **nunca** no caminho crítico.
- **Projeto final (fora PAP):** canal de comunicação **próprio** (sem Telegram como produto).

---

## 3. Nível 2 — Catálogo P1

| Must (defesa) | Stretch | Fora desta PAP |
|---|---|---|
| Conversa por voz + rosto | Agenda rica | Notícias completas |
| Lembretes (aviso em voz, confirmar/adiar) | Leitura de livros | BackOffice |
| Música local | Meteorologia | Locomoção / braços |
| Histórias (biblioteca + TTS; áudio opcional) | História inventada por LLM | Diagnóstico médico |
| Perfil / memória (gostos + 80 msgs + resumo) | | Canal próprio (só visão) |
| Modo cuidador local (PIN + bloqueio) | | |
| Medicação crítica só criada pelo cuidador | | |
| Notificador Telegram (D1+D3) | | |

---

## 4. Nível 3 — Comportamentos

### 4.1 Máquina de estados

Estados principais: `Idle` (wake-word) → `Listening` → `Thinking` (LLM/tools) → `Speaking` → `Idle`.

Prioridade de eventos: **alerta de lembrete > fala > música**.

O rosto no ecrã **só espelha** o estado atual (ver §6.2).

### 4.2 Lembretes

1. À hora: **pausa música** → rosto `alert` → TTS → **Já fiz** / **Adiar** (voz ou toque).
2. Se o idoso responder no ciclo do alerta → processa → **retoma música**.
3. Repete **N vezes** (default **3**, intervalo **~2 min**); cuidador pode alterar N/intervalo no PIN.
4. Se for **crítico** e continuar sem confirmação → `notify` tenta Telegram; estado `expirado`.
5. Modo suave «aviso por cima da música» é opcional; na dúvida e na demo, **interrompe** (pausa/retoma).

### 4.3 Ética

- Lembretes e registo apenas; o LLM **recusa** aconselhar doses ou diagnosticar.
- Lembretes de **medicação / críticos**: só o **cuidador** (após PIN).
- Idoso pode criar lembretes **não médicos** (água, passeio, etc.), se a UI o permitir.

### 4.4 Histórias

- Base: `historias/*.txt` + opcional `.meta.json` (título, tags, duração).
- Se existir áudio correspondente → toca o áudio; senão → TTS do texto.
- Stretch: geração pelo LLM se o modelo aguentar.

### 4.5 Música e voz

- Música: pastas por género em `musica/`; `catalogo.json` gerado ao arrancar; player `audio` no browser via API.
- TTS: **Piper PT** (voz fixa); fallback TTS de sistema se Piper falhar (lembretes nunca mudos).
- STT: Whisper local (small/base ou faster-whisper).
- Wake-word: openWakeWord (modelo «RIC») + botão fallback.

### 4.6 Perfis

Um perfil de idoso por instalação. Cuidador = PIN + contactos, não segundo utente.

---

## 5. Nível 4 — Sistema informático

### 5.1 Topologia

**Um único processo** Python («RIC») no **Mint XFCE** do PC do protótipo. O browser em ecrã cheio (kiosk) é só cliente localhost.

- Backend: `systemd` **user** service `ric.service` (reinicia se crashar).
- Kiosk: **autostart XFCE separado** (Chromium/Firefox `--kiosk http://127.0.0.1:8787`).
- O idoso **não sai** da UI; saída só com PIN / atalho de cuidador.

```
[Ecrã tactile + browser kiosk]
        ↕  REST /api/v1 + WebSocket /ws  (127.0.0.1:8787)
[Processo RIC — ric.service]
  core | db | reminders | voice | llm | music | stories | notify | caregiver | web
        ↕                    ↕
   SQLite + pastas      Ollama (qwen2.5:3b + tools)
        ⇣ (opcional, se net)
   Telegram (críticos D1+D3)
```

### 5.2 Layout em disco (máquina RIC)

| Caminho | Conteúdo |
|---|---|
| `/home/ric/ric-app/` | Código da aplicação |
| `/home/ric/ric-data/` | `ric.db`, `musica/`, `historias/`, `vozes/`, logs, `backups/` |
| Utilizador de sistema | `ric` (sem sudo no dia a dia) |

No repositório GitHub (dev): app nova em `ric/`; legado em `archive/legacy/`; UI estática servida pelo mesmo processo Python; `config.example.env` no repo; `.env` fora do git.

### 5.3 Porque Python + Linux

O gargalo é o modelo LLM e o STT, não a linguagem do servidor. Python encaixa Ollama, Whisper, Piper e openWakeWord. «Otimizado» = fiabilidade + prazo + PC reciclado.

### 5.4 Módulos (domínio)

| Módulo | Responsabilidade |
|---|---|
| `core` | Máquina de estados, fila de eventos, prioridades |
| `db` | SQLite: lembretes, perfil, gostos, conversas, confirmações, hash do PIN |
| `reminders` | Agendar, disparar, confirmar, adiar, crítico, N retries |
| `voice` | Wake-word, STT, TTS; abstrai motores concretos |
| `llm` | Cliente Ollama + tools P1 (ver §6.5); timeout e resiliência |
| `music` | Pastas + `catalogo.json` + comandos ao player no browser |
| `stories` | Biblioteca txt/meta (+ áudio opcional) + TTS |
| `notify` | Interface `enviar_aviso`; impl. Telegram agora; canal próprio depois |
| `caregiver` | PIN (hash + tentativas), sessão com timeout, config |
| `web` | Estáticos do rosto + REST + WebSocket |

### 5.5 Dados (SQLite)

| Área | Decisão |
|---|---|
| Lembretes | Schema A: tipos, crítico, estados, diário, `criado_por`; **sem** dose estruturada |
| Gostos | Tabelas `gostos` estruturadas (música, temas de histórias, …) |
| Conversas | **80** mensagens + **1** resumo; o LLM só recebe ~últimas **20** + resumo no prompt |
| Confirmações | Histórico leve «já fiz» / adiar |
| PIN | Hash no SQLite (nunca texto claro) |
| Música / histórias | Ficheiros em disco, não blobs na BD |

### 5.6 API

- Base: `http://127.0.0.1:8787`
- REST versionado: `/api/v1/reminders`, `/api/v1/profile`, `/api/v1/music`, `/api/v1/caregiver/...`
- WebSocket: `/ws` — eventos `state`, `alert`, `tts`, `music`, …

### 5.7 UI

HTML/CSS/JS simples servido pelo processo RIC. Sem React/Next nesta PAP.  
Idle: rosto calmo + relógio + **próximo lembrete**; mais botões/info **sob procura** (não dashboard permanente).

### 5.8 Config e segredos

- `.env` + `config.example.env`: token Telegram, `RIC_DEBUG`, paths, porta se necessário.
- PIN hash e dados de negócio → SQLite.
- Segredos **nunca** no git.

### 5.9 Legado

Arquivar o `ric/` atual em `archive/legacy/`. Implementação nova alinhada a esta arquitetura. Não manter dois sistemas a correr em paralelo na demo.

---

## 6. Nível 5 — Detalhe operacional (grelha 2026-10-25)

### 6.1 Voz — janela e barge-in

| Tema | Decisão |
|---|---|
| Após «RIC» | ~**6–8 s** de escuta; ~**1,5 s** de silêncio fecha o turno; se vazio → pedido para repetir + botão |
| Barge-in (must) | Em conversa, «RIC» **corta** TTS → `Listening` |
| Barge-in vs alerta | Wake-word **não** cancela lembrete/alerta (só Já fiz / Adiar / fim dos retries) |
| Barge-in (stretch) | Em fala não crítica, **duck** do TTS + escuta em paralelo — só se o corte seco já estiver estável |

### 6.2 Rosto (estados visuais)

`idle`, `listening`, `thinking`, `speaking`, `alert`, **`music`**, **`story`** (+ ecrã cuidador / erro STT quando preciso).

### 6.3 Telegram (conteúdo)

Mínimo: título do lembrete + «sem confirmação» + hora local.  
**Sem** conversas, áudio ou localização.

### 6.4 LLM — timeout e disponibilidade

| Tema | Decisão |
|---|---|
| Timeout | ~**8–12 s** → frase de fallback → Idle; cancelável com barge-in / novo wake |
| Ollama em baixo | Core (lembretes, música, histórias, UI) **sobe na mesma**; conversa desliga até Ollama ok |
| Restart | 1–2 tentativas de restart do serviço Ollama |

### 6.5 Tools do LLM (P1)

Permitidas: ler lembretes / próximo lembrete, `tocar_musica` / parar, `contar_historia`, `guardar_gosto`.  
**Proibido:** criar/editar medicamentos.  
Telegram **não** é tool livre do LLM — dispara no **scheduler** de lembretes (D1+D3). «Avisar cuidador» por voz = fase posterior com confirmação no ecrã.

### 6.6 Cuidador (PIN e sessão)

- PIN numérico 4–6 dígitos, hash no SQLite.
- Após ~**5** falhas → bloqueio temporário.
- Sessão: timeout **~2–5 min** sem toque + aviso **~30 s** antes de fechar.
- Desbloqueia: config, medicamentos, **sair do kiosk**.

### 6.7 Kiosk

Fullscreen; sem barra/tabs fáceis; idoso não abandona a UI. Saída só cuidador (PIN).

### 6.8 Logs e privacidade

- Default: logs **técnicos** (erros, estados SM, «lembrete disparou») — **sem** texto completo de conversas.
- Áudio **nunca** gravado por defeito.
- `RIC_DEBUG=1`: pode guardar últimas N frases (só dev).

### 6.9 Backup

- Timer diário → `/home/ric/ric-data/backups/` com retenção ~**7 dias**.
- Sync cloud (**só mais tarde**, explícito, com consentimento) — nunca por defeito.

### 6.10 Áudio (música ∩ lembrete)

Pausa música → TTS alerta → resposta («já tomei» etc.) → retoma música.

### 6.11 Ordem de implementação (primeira fatia)

1. API + SQLite lembretes + UI mínima (sem voz)  
2. Voz (wake → STT → LLM → TTS)  
3. Telegram / música / histórias  

Alinhado ao P1-crono: fiabilidade → companhia → extras.

---

## 7. Cronograma técnico (P1-crono)

| Etapa | Até | Foco |
|---|---|---|
| 1 | 08/01/2027 | Arquitetura nova + Mint XFCE no PC do RIC (quando possível) + estados + rosto + wake-word + STT/TTS + lembretes fiáveis + Ollama tools básicos |
| 2 | 26/03/2027 | Música (`catalogo.json`) + histórias (txt/meta ± áudio) + perfil/gostos/memória + modo cuidador PIN + medicação só cuidador |
| 3 | 21/05/2027 | Notificador Telegram (D1+D3) + polish voz/rosto + testes + docs/ética; stretch se sobrar |
| Final | 18/06–09/07/2027 | Relatório e defesa |

Detalhe de calendário escolar: [`PLANEAMENTO.md`](PLANEAMENTO.md).

---

## 8. Critério de demo (alvo)

Sem Internet (Telegram pode falhar na demo):

1. «RIC» → pedido → resposta em voz com rosto a mudar de estado.
2. Lembrete → pausa música se houver → alerta → Já fiz / Adiar → retoma.
3. Música local; prioridade alerta > fala > música.
4. História da biblioteca (TTS ou áudio se existir).
5. Cuidador com PIN cria lembrete crítico; sessão com timeout.

Com net (opcional na demo): falhanço de confirmação crítica gera aviso Telegram (conteúdo mínimo).
