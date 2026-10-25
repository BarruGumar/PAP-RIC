# Planeamento do RIC

**Aluno:** Pedro Albuquerque  
**Turma:** 3-TIS  
**Orientador:** Gil Ribeiro  
**Trabalho:** RIC — Robô Interativo Companheiro  
**Atualizado:** 2026-10-25

Um aluno, fora das aulas. A voz é a forma principal de uso; o ecrã mostra o rosto e só revela texto/botões quando necessário.

As fichas em [`docs/metas/`](metas/README.md) dizem o que cada função é. A arquitetura acordada está em [`docs/ARQUITETURA.md`](ARQUITETURA.md). Este ficheiro diz **como e quando**.

## Processo

O mesmo processo vale para cada meta, quando chegar a vez dela.

1. Fechar só os pontos «ainda por descrever» dessa meta.
2. Definir o mínimo que se demonstra nessa etapa.
3. Fazer a função a falar e a ouvir, em português de Portugal. Rosto no ecrã tactile; botões/texto como apoio.
4. O núcleo (lembretes, voz, música local, histórias guardadas, perfil) **não depende da Internet**.
5. Registar o que ficou de fora e o que o protótipo já faz, na ficha e no [`CONTEXTO-PAP.md`](../CONTEXTO-PAP.md).

## Tempo (P1-crono)

| Até | O que se faz |
|---|---|
| 23/10/2026 | Planificação (Anexo I). Datas escolares provisórias — ver contexto |
| 08/01/2027 (etapa 1) | **Reescrita da arquitetura** + preparar/instalar **Linux leve** no PC do RIC (quando o hardware estiver disponível) + máquina de estados + rosto (HTML/JS localhost) + wake-word («RIC») + STT/TTS locais (Whisper + Piper) + lembretes fiáveis (interrupção, confirmar/adiar) + Ollama tools básicos. Ver também [`PLANEAMENTO-ETAPA-1.md`](PLANEAMENTO-ETAPA-1.md) (atualizar face às decisões de 2026-10-25) |
| 26/03/2027 (etapa 2) | Música local (browser + API) + histórias (biblioteca + TTS) + perfil/memória SQLite + modo cuidador (PIN) + lembretes de medicação só pelo cuidador |
| 21/05/2027 (etapa 3) | Notificador Telegram para críticos sem confirmação (D1+D3) + polimento voz/rosto + testes + docs/ética. **Stretch se sobrar:** agenda rica, livros, meteo, história gerada por LLM |
| 18/06/2027 | Relatório final |
| 09/07/2027 | Defesa |

### Must / stretch / fora (resumo)

Ver tabela completa em [`ARQUITETURA.md`](ARQUITETURA.md) secção 3.

- **Must:** companheiro por voz (rosto, wake-word, STT/TTS), lembretes, música, histórias locais, memória mínima, cuidador local, aviso Telegram em falha de crítico.
- **Stretch:** agenda rica, livros, meteo, história LLM.
- **Fora desta PAP:** BackOffice, notícias completas, locomoção, diagnóstico; canal de comunicação próprio = visão do projeto final (módulo `notify` preparado para trocar a implementação).

### O que fica de fora do calendário obrigatório

O BackOffice e o canal próprio de monitorização remota **não** entram nestas etapas como produto. O Telegram na PAP é o aviso mínimo de falha crítica; a arquitetura isola `notify` para substituir depois.

## Estrutura do trabalho

| Onde | Para quê |
|---|---|
| [`docs/metas/`](metas/README.md) | O que cada função é |
| [`docs/ARQUITETURA.md`](ARQUITETURA.md) | Sistema informático acordado |
| `docs/PLANEAMENTO.md` | Como e quando (este ficheiro) |
| `arquivo/` (a criar) + novo `ric/` | Legado arquivado; código novo |
| [`CONTEXTO-PAP.md`](../CONTEXTO-PAP.md) | Fonte de verdade do projeto |
