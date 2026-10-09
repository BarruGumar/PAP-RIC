# Anexo I — rascunho para transcrição

Este texto é um rascunho para transcrever para o formulário de aprovação de 23/10/2026. Não é o formulário oficial.

O planeamento que o sustenta está em [`docs/PLANEAMENTO.md`](PLANEAMENTO.md).

## Identificação

Pedro Albuquerque, turma 3-TIS, orientador Gil Ribeiro.

## O que é o RIC

O RIC (Robô Interativo Companheiro) é um protótipo de companheiro digital de apoio, sobretudo a idosos: ajuda a lembrar o essencial e faz companhia. Nesta PAP desenvolve-se e testa-se o próprio robô, com interação, privacidade e hardware reaproveitado.

A voz (TTS e STT) é a forma principal de uso, porque falar e ouvir é a forma mais acessível. Botões grandes e texto são apoio.

## Visão futura

A recolha de equipamentos na escola e a colaboração entre TAS e TIS, para mais tarde apoiar utentes, são uma aplicação possível; esse processo ainda não existe e não entra nesta PAP.

## Metas

Conversação e voz, lembretes, gestão de agenda, cantar música da biblioteca local, contar histórias, leitura de livros, recomendações de entretenimento, e meteorologia e notícias. O detalhe de cada uma está em `docs/metas/`.

## Etapas

| Até | O que se faz |
|---|---|
| 23/10/2026 | Só a planificação. Não se implementa funcionalidade nova |
| 08/01/2027 | Voz, conversação, lembretes em fala livre, cantar música da biblioteca local, história curta mais um pequeno conjunto guardado |
| 26/03/2027 | Agenda e leitura de livros em voz, com música de ambiente. Domínio público ou autorização. Vozes por personagem só se a leitura simples estiver estável |
| 21/05/2027 | Recomendações a partir dos gostos e do que está no robô; meteorologia do dia e da semana; notícias. Previsão guardada só se a meteorologia em direto já funcionar. Testes, privacidade e limites |
| 18/06/2027 | Relatório |
| 09/07/2027 | Defesa |

## Recursos

Hardware reaproveitado, Python, Ollama e SQLite. As funções essenciais (lembretes, agenda, música local, histórias guardadas e leitura do que está no robô) funcionam sem Internet.

## O que não entra

- Diagnóstico de doenças e prescrição de medicação
- O Senhor dos Anéis, por direitos de autor
- Recolha escolar de equipamentos e utentes reais
- Locomoção e braços
- BackOffice como produto. O foco é o RIC. Um protótipo de envio de dados só se sobrar tempo depois de maio; a estrutura do BackOffice não se desenha agora
