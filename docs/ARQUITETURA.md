# Arquitetura do RIC (PAP)

**Data das decisões:** 2026-10-25  
**Âmbito:** entregável da PAP (até defesa ~julho 2027).  
**Fonte:** planeamento grelhado com o Pedro; resumo também em [`CONTEXTO-PAP.md`](../CONTEXTO-PAP.md) e [`PLANEAMENTO.md`](PLANEAMENTO.md).

O código legado em `ric/` será **arquivado** e o sistema **reescrito** segundo este documento. Reutilizam-se conteúdos (música, vozes, ideias), não a estrutura antiga.

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
| Hardware | PC/laptop reciclado + **ecrã tactile** ligado ao PC + microfone/colunas |
| SO alvo (demo / protótipo) | **Linux leve** (ex. Linux Mint XFCE, Lubuntu ou Debian + ambiente leve) |
| SO de desenvolvimento | Windows (ou outro) **opcional** no PC de trabalho do aluno; o código deve correr no Linux do RIC |
| Ligação rosto ↔ cérebro | Browser em kiosk em `http://127.0.0.1:…` — **sem Internet e sem Wi‑Fi** |
| Rede | Offline-first: núcleo local; Internet só para extras acordados |
| Privacidade | LLM e dados no dispositivo; sem diagnóstico nem prescrição |

**Porquê Linux no equipamento do RIC:** menos overhead de RAM/CPU no PC reciclado; melhor encaixe com Ollama, Whisper, Piper e openWakeWord; arranque automático simples (`systemd` + Chromium/Firefox em kiosk). Validar o ecrã tactile com live USB antes de formatar.

**Internet (só o acordado):**

- **Must híbrido:** aviso ao cuidador via Telegram se lembrete **crítico** não for confirmado após N avisos (e houver net; senão fila/log).
- **Stretch:** meteorologia.
- **Projeto final (fora PAP):** canal de comunicação **próprio** (sem Telegram como produto).

---

## 3. Nível 2 — Catálogo P1

| Must (defesa) | Stretch | Fora desta PAP |
|---|---|---|
| Conversa por voz + rosto | Agenda rica | Notícias completas |
| Lembretes (aviso em voz, confirmar/adiar) | Leitura de livros | BackOffice |
| Música local | Meteorologia | Locomoção / braços |
| Histórias (biblioteca + TTS) | História inventada por LLM | Diagnóstico médico |
| Perfil / memória mínima | | Canal próprio (só visão) |
| Modo cuidador local (PIN) | | |
| Medicação crítica só criada pelo cuidador | | |
| Notificador Telegram (D1+D3) | | |

---

## 4. Nível 3 — Comportamentos

### 4.1 Máquina de estados

Estados principais: `Idle` (wake-word) → `Listening` → `Thinking` (LLM/tools) → `Speaking` → `Idle`.

Prioridade de eventos: **alerta de lembrete > fala > música**.

O rosto no ecrã **só espelha** o estado atual.

### 4.2 Lembretes

1. À hora: pausa/baixa música → rosto «a avisar» → TTS → **Já fiz** / **Adiar** (também por voz).
2. Repete N vezes se não houver resposta.
3. Se for **crítico** (ex. medicação) e continuar sem confirmação → `notify` tenta Telegram.
4. Modo suave «aviso por cima da música» é opcional; na dúvida e na demo, **interrompe**.

### 4.3 Ética

- Lembretes e registo apenas; o LLM **recusa** aconselhar doses ou diagnosticar.
- Lembretes de **medicação / críticos**: só o **cuidador** (após PIN).
- Idoso pode criar lembretes **não médicos** (água, passeio, etc.), se a UI o permitir.

### 4.4 Histórias

- Base: biblioteca local de textos + TTS.
- Stretch: geração pelo LLM se o modelo aguentar.

### 4.5 Música e voz

- Música: elemento `audio` no browser, controlado pela API do RIC.
- TTS / avisos: motor no processo Python (Piper).
- STT: Whisper local (small/base ou faster-whisper).
- Wake-word: openWakeWord (modelo «RIC») + botão fallback.

### 4.6 Perfis

Um perfil de idoso por instalação. Cuidador = PIN + contactos, não segundo utente.

---

## 5. Nível 4 — Sistema informático

### 5.1 Topologia

**Um único processo** Python («RIC») no **Linux** do PC do protótipo. O browser em ecrã cheio (kiosk) é só cliente localhost. No arranque: serviço `systemd` sobe o RIC e o browser em `http://127.0.0.1:…`.

```
[Ecrã tactile + browser kiosk]
        ↕  REST + WebSocket/SSE  (127.0.0.1)
[Processo RIC]
  core | db | reminders | voice | llm | music | stories | notify | caregiver | web
        ↕                    ↕
   SQLite + pastas      Ollama (qwen2.5:3b + tools)
        ⇣ (opcional, se net)
   Telegram (críticos D1+D3)
```

### 5.2 Porque Python + Linux

O gargalo é o modelo LLM e o STT, não a linguagem do servidor. Python encaixa Ollama, Whisper, Piper e openWakeWord com menos tempo de aluno até julho. O Linux leve no PC do RIC maximiza RAM/CPU para esses motores. «Otimizado» = fiabilidade + prazo + PC reciclado. Windows não é o SO da demo; pode usar-se só para editar código e documentar.

### 5.3 Módulos (domínio)

| Módulo | Responsabilidade |
|---|---|
| `core` | Máquina de estados, fila de eventos, prioridades |
| `db` | SQLite: lembretes, perfil, conversas, confirmações, hash do PIN |
| `reminders` | Agendar, disparar, confirmar, adiar, marcar crítico, N retries |
| `voice` | Wake-word, STT, TTS; abstrai motores concretos |
| `llm` | Cliente Ollama + tools (agendar, música, preferências, …) |
| `music` | Catálogo em pasta + comandos para o player no browser |
| `stories` | Biblioteca local + leitura TTS; gancho stretch para LLM |
| `notify` | Interface `enviar_aviso`; impl. Telegram agora; canal próprio depois |
| `caregiver` | PIN, ecrã/API de configuração, contactos |
| `web` | Estáticos do rosto + REST + WebSocket/SSE |

### 5.4 Dados (SQLite)

Obrigatório P1: `lembretes`, `perfil`, `conversas` (últimas N + resumo), `confirmacoes`.  
Música e histórias = ficheiros em disco, não blobs na BD.

### 5.5 UI

HTML/CSS/JS simples servido pelo processo RIC. Sem React/Next nesta PAP.  
Toque: botões grandes só em alertas, falha de voz e modo cuidador.

### 5.6 Legado

Arquivar o `ric/` atual (ex. `arquivo/ric-legado` ou branch). Implementação nova alinhada a esta arquitetura. Não manter dois sistemas a correr em paralelo na demo.

---

## 6. Cronograma técnico (P1-crono)

| Etapa | Até | Foco |
|---|---|---|
| 1 | 08/01/2027 | Arquitetura nova + (quando possível) Linux no PC do RIC + estados + rosto + wake-word + STT/TTS + lembretes fiáveis + Ollama tools básicos |
| 2 | 26/03/2027 | Música + histórias (biblioteca) + perfil/memória + modo cuidador PIN + medicação só cuidador |
| 3 | 21/05/2027 | Notificador Telegram (D1+D3) + polish voz/rosto + testes + docs/ética; stretch se sobrar |
| Final | 18/06–09/07/2027 | Relatório e defesa |

Detalhe de calendário escolar: [`PLANEAMENTO.md`](PLANEAMENTO.md).

---

## 7. Critério de demo (alvo)

Sem Internet (Telegram pode falhar na demo):

1. «RIC» → pedido → resposta em voz com rosto a mudar de estado.
2. Lembrete → alerta com interrupção → Já fiz / Adiar.
3. Música local; chat/voz não a «matam» sem regra de prioridade.
4. História da biblioteca em TTS.
5. Cuidador com PIN cria lembrete crítico.

Com net (opcional na demo): falhanço de confirmação crítica gera aviso Telegram.
