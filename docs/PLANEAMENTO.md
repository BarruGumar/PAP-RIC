# Planeamento do RIC

**Aluno:** Pedro Albuquerque  
**Turma:** 3-TIS  
**Orientador:** Gil Ribeiro  
**Trabalho:** RIC — Robô Interativo Companheiro  
**Data:** 2026-10-09

Um aluno, fora das aulas. A voz (TTS e STT) é a forma principal de uso. Botões grandes e texto ficam como apoio.

As fichas em [`docs/metas/`](metas/README.md) dizem o que cada função é. Este ficheiro diz como e quando. O código fica em `ric/`.

## Processo

O mesmo processo vale para cada meta, quando chegar a vez dela.

1. Fechar só os pontos «ainda por descrever» dessa meta.
2. Definir o mínimo que se demonstra nessa etapa.
3. Fazer a função a falar e a ouvir, em português de Portugal. Botões e texto ficam como apoio.
4. O que tem de funcionar sem Internet (lembretes, agenda, música local, histórias guardadas, leitura do que está no robô) não depende da nuvem.
5. Registar o que ficou de fora e o que o protótipo já faz, na ficha e no contexto.

## Tempo

Hoje é 9 de outubro de 2026. Até 23/10/2026 só há planificação: não se implementa funcionalidade nova.

| Até | O que se faz |
|---|---|
| 23/10/2026 | Só a planificação, para aprovarem o projeto |
| 08/01/2027 (etapa 1) | Voz estável e o que já existe: conversação por voz; lembretes pedidos em fala livre e avisados em voz; cantar música da biblioteca local; a história curta já existente mais um pequeno conjunto de histórias guardadas. O pormenor está em [`docs/PLANEAMENTO-ETAPA-1.md`](PLANEAMENTO-ETAPA-1.md) |
| 26/03/2027 (etapa 2) | Agenda (dia, consulta, compromisso, e a lembrança sai daí) e leitura de livros em voz, com música de ambiente. Livros de domínio público ou com autorização. Vozes diferentes por personagem só se a leitura simples já estiver estável |
| 21/05/2027 (etapa 3) | Recomendações a partir dos gostos e do que está no robô; meteorologia do dia e da semana; notícias atuais. A previsão guardada para quando cai a Internet fica se a meteorologia em direto já funcionar. Testes, privacidade e limites |
| 18/06/2027 | Relatório |
| 09/07/2027 | Defesa |

### O que fica de fora destas etapas

O BackOffice não entra nestas etapas. O foco é o RIC. Um protótipo de envio de dados, se sobrar tempo depois de maio, fica como extra. A estrutura do BackOffice não se desenha agora.

Criar histórias novas na hora e a busca automática de músicas no BackOffice são ideias a explorar, não trabalho calendarizado.

## Estrutura do trabalho

| Onde | Para quê |
|---|---|
| [`docs/metas/`](metas/README.md) | O que cada função é |
| `docs/PLANEAMENTO.md` | Como e quando (este ficheiro) |
| `ric/` | Código do protótipo |
