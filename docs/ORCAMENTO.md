# Orçamento — RIC (PAP)

**Aluno:** Pedro Albuquerque  
**Data:** 2026-10-09  
**Inventário:** [`docs/INVENTARIO-HARDWARE.md`](INVENTARIO-HARDWARE.md)

## 1. Princípio

Reaproveitar primeiro. Não há compras decididas. O inventário ainda não lista o que existe em casa: a tabela está por preencher. Os valores abaixo são ordens de grandeza de material usado. O Pedro corrige-os quando disser o que já tem.

## 2. Ligação PC–tablet sem Internet

A interface é uma página web. O servidor, em `ric/web_server.py`, escuta em `127.0.0.1` na porta `8787`. Essa morada é só o próprio PC: um tablet na rede não a alcança.

Processo necessário, ainda por fazer no código:

1. O PC e o tablet ficam na mesma rede local, sem Internet: ponto de acesso do Windows, ou um router sem ligação WAN.
2. O tablet abre `http://IP-do-PC:8787` no browser.
3. Para isso o servidor terá de escutar na rede local, e não só em `127.0.0.1`.

Este passo fica descrito. O código não se altera aqui.

## 3. O que dá para usar do tablet nesta etapa

| Parte do tablet | Nesta etapa | Notas |
|---|---|---|
| Ecrã | Sim | O browser mostra o rosto, o texto e os botões |
| Altifalantes, para a música | Sim | A página pede o áudio ao PC e o tablet reproduz |
| Voz do RIC (TTS) | Continua no PC | Como em [`docs/PLANEAMENTO-ETAPA-1.md`](PLANEAMENTO-ETAPA-1.md). Passar a fala para as colunas do tablet é outro estudo |
| Microfone | O do PC | O reconhecimento offline (Vosk ou Whisper) corre no PC. O microfone do tablet não chega lá sozinho. Enviar o áudio do tablet pela rede local fica como possibilidade depois, fora do custo e do trabalho de janeiro |
| Câmara | Fora | O tablet pode tê-la. A etapa 1 não a usa e não entra no orçamento |

## 4. Três cenários

Euros aproximados de material usado.

| Cenário | O que entra | Ordem de grandeza |
|---|---|---|
| Zero euros | PC que já corre o Ollama, tablet antigo com browser, microfone e colunas que já existam. Software sem licença: Python, Ollama, SQLite e voz local | 0 € |
| Só o que faltar | Tablet usado simples, se não houver nenhum; microfone USB, se o PC não tiver. Teto desta PAP enquanto o reaproveitado chegar | Tablet 40–80 €; microfone 10–20 €; total abaixo de 100 € |
| Não comprar agora | Raspberry Pi 5 e AI HAT. Só se o PC não aguentar a voz e o modelo ao mesmo tempo, e com justificação no inventário | Fora deste orçamento |

## 5. Pré-projeto

O campo de orçamento do pré-projeto Word fica por preencher até o Pedro confirmar o que já tem.
