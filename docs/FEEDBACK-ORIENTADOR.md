# Feedback do orientador — análise

**Data:** 2026-10-18  
**Orientador:** Gil Ribeiro  
**Estado:** estudo. Ainda não há código novo. As escolhas abaixo são a resposta proposta, à espera de confirmação na aula.

O pré-projeto descreve o protótipo de hoje. Vários pontos do feedback já estavam no plano da etapa 1 e faltava dizê-los com esta clareza.

## 1. Reconhecimento de fala no navegador

O orientador tem razão. No Chrome, a Web Speech API envia o áudio para a Google. Isso falha sem Internet e sai do pilar da privacidade.

O que o protótipo faz hoje é isso. A etapa 1 já o marca como caminho a abandonar (`docs/PLANEAMENTO-ETAPA-1.md`). A frase do pré-projeto tem de passar a dizer: o navegador é o estado atual. O reconhecimento da PAP é local.

## 2. Voz (TTS)

Duas candidatas, com papéis diferentes.

**Piper, voz `pt_PT-tugão-medium`.** É a primeira a ligar ao RIC. Português de Portugal, uma voz, qualidade medium, 22 050 Hz, ficheiro de cerca de 63 MB, licença CC0. O orientador já a ouviu e considera-a boa. Corre no PC, sem nuvem. O nome tem «ã»: o comando `piper --model pt_PT-tugão-medium` pode falhar. Descarrega-se o `.onnx` e o `.json` do Hugging Face (`rhasspy/piper-voices`).

**Kokoro-82M.** O modelo oficial é leve (82 milhões de parâmetros, licença Apache-2.0) e rápido em CPU. O português que traz é do Brasil (`lang_code='p'`, vozes `pf_dora`, `pm_alex`, `pm_santa`). Para o RIC, que fala português de Portugal, essa voz fica de fora.

Existe um afinamento de 2026 para português europeu, o pacote `tts-eu-pt` (Apache-2.0, CPU, cerca de 82 milhões de parâmetros). Lê horas e números à portuguesa: `16:54` sai «dezasseis e cinquenta e quatro». Isso interessa aos lembretes. É uma voz só, de comunidade, e ainda não tem teste formal de audição. Ouve-se ao lado do tugão. Fica a que se perceber melhor numa frase de aviso («são dezasseis horas, hora do comprimido»).

O passo a passo está em [`ROTEIRO-VOZ.md`](ROTEIRO-VOZ.md). Resultado da audição, em 2026-10-18: por medir no PC do Pedro. Sem essa audição, o RIC continua a falar pelo SAPI.

## 3. Reconhecimento (STT)

O `faster-whisper` é a via Whisper que a etapa 1 já previa, na implementação mais leve (CTranslate2, `pip install faster-whisper`). O modelo `small` em int8 usa cerca de 1,5 GB de RAM. Não distingue por si português de Portugal de português do Brasil: o teste é que o faz.

Teste combinado, com o Ollama ligado e a rede desligada na corrida que conta. A descarga do modelo faz-se antes, com Internet. As dez frases estão em [`ROTEIRO-VOZ.md`](ROTEIRO-VOZ.md).

Resultado em 2026-10-18: por medir. Modelo usado: _______________. Frases certas: ____ / 10. O texto transcrito cola-se na tabela do roteiro e resume-se em [`TABELA-LLMS.md`](TABELA-LLMS.md). Se o `small` não couber com o `qwen2.5:3b` aberto, o teste repete-se com `base`.

O Qwen com entrada de áudio continua de fora. A nota está em `docs/TABELA-LLMS.md`.

## 4. AI HAT+ 2 e mini-PC de 16 GB

Concordo com o orientador para esta PAP.

No lançamento, os modelos que a Hailo publica para o AI HAT+ 2 vão de 1B a 1,5B: Qwen2.5-Instruct 1.5B, Qwen2.5-Coder 1.5B, Llama 3.2 1B, DeepSeek-R1-Distill 1.5B. O `qwen2.5:3b` que já corre no PC do Pedro não está nessa lista.

A ficha da Raspberry Pi diz que os 8 GB da placa chegam, em teoria, a modelos até cerca de 6B. Isso é o teto do hardware. O que se instala e conversa hoje são os modelos de 1B a 1,5B. Um modelo de 1,5B já foi a opção «PC fraco» na tabela, e é mais fraco do que o 3B que o Pedro achou suficiente.

Um mini-PC usado com 16 GB corre ao mesmo tempo o `qwen2.5:3b` (cerca de 3 a 4 GB), o Piper (dezenas de MB) e o faster-whisper `small` (cerca de 1,5 GB). Sobra margem para o sistema. O HAT+ 2 só volta a entrar se o cérebro passar a ser um Raspberry Pi, e nesse caso o modelo desce para 1,5B, com essa perda escrita no relatório.

## 5. Lembretes e o modelo

O orientador descreve o sistema como ele é. A frase «crio lembretes sem o modelo» estava curta demais.

| Momento | Precisa do modelo? |
|---|---|
| Perceber «lembra-me da consulta na terça às 10h» | Sim. O modelo chama a ferramenta `agendar_lembrete`. Se o modelo falhar, o código tenta um fallback com horas do tipo «às 18:00» ou «daqui 5 minutos». «Terça» ainda não é um dia da semana nesse fallback. |
| Guardar na base SQLite | Não. |
| Disparar à hora, com a rede desligada e o Ollama parado | Não. É o relógio local. |
| Confirmar («já tomei») e adiar | Não, no fluxo do relógio. Por voz, perceber a frase usa o reconhecimento e, se a frase for livre, o modelo. |

O que tem de funcionar sem modelo e sem Internet é o disparo. O pedido em fala livre usa o modelo. Os botões e o formulário cobrem o caso em que o modelo está parado.

## 6. A fase 1 está carregada

Concordo. A etapa 1 junta voz estável, lembrete diário, música por fala, história do modelo e ainda 3 a 5 histórias guardadas. É demais para o primeiro relatório.

Proposta para discutir com o orientador. Entra na etapa 1:

- Piper tugão a dizer o aviso e a resposta.
- Teste do faster-whisper `small`, com botão e texto se o microfone falhar.
- Conversa curta em português de Portugal.
- Criar um lembrete por fala com hora («às 10», «daqui 5 minutos») e dispará-lo em voz, com a rede desligada.
- Tocar uma música da biblioteca, por fala ou por botão. O leitor já existe.
- Uma história curta do modelo. Já existe.

Passa para a etapa 2:

- Lembrete que volta a armar-se todos os dias.
- As 3 a 5 histórias guardadas.
- A agenda com dia da semana («terça») e a leitura de livros, que já estavam na etapa 2.

Assim o primeiro relatório mostra os dois pilares, offline e privacidade, com uma demonstração que cabe no prazo.

## 7. AMALIA

Vale a pena testar nesta fase, como o orientador pede. Ainda não substitui o `qwen2.5:3b`.

A AMALIA-9B (publicada a 1 de julho de 2026, consórcio com NOVA, IST e FCT, licença Apache-2.0) é um modelo de texto feito para português de Portugal. Não ouve nem fala: a voz continua a ser Piper e faster-whisper. Há uma variante com imagem (AMALIA-VL). O RIC não precisa dela nesta PAP.

No Ollama corre como `teex/amalia`. O Q4 (`q4_K_M`) ocupa 5,6 GB. O Q8 ocupa 9,7 GB. Num mini-PC de 16 GB o Q4 cabe ao lado do Whisper `small`. O Q8 deixa pouca RAM para o resto. No AI HAT+ 2 não cabe.

O RIC precisa que o modelo chame ferramentas (agendar, música, perfil). A ficha da AMALIA não documenta isso. Sem um prompt de sistema, o modelo inventa uma identidade. O pacote `teex` traz um prompt factual. O RIC já tem o seu e passa por cima.

O teste é o da `docs/TABELA-LLMS.md`, no mesmo PC, três vezes: conversa, «Lembra-me de beber água às HH:MM», música, história curta. A AMALIA fica como modelo principal só se responder em português de Portugal de forma mais clara do que o `qwen2.5:3b` e a ferramenta de agendar for chamada. Se falar melhor e falhar a ferramenta, mantém-se o Qwen, porque o pedido falado de lembrete é critério da etapa 1.

## Resposta curta para o orientador

Professor, obrigado pelo feedback. Concordo com os pontos.

O reconhecimento no navegador é só o que o protótipo faz hoje. Na etapa 1 o áudio fica no PC: vou testar o faster-whisper, modelo small, com o Ollama ligado e sem Internet. Se não couber, desço de modelo ou uso o Vosk.

Para falar, começo pelo Piper com a voz tugão, que o professor já testou. O Kokoro oficial é português do Brasil. Há um afinamento recente para português de Portugal. Ouço os dois numa frase de lembrete com hora e fico com o que se perceber melhor.

Sobre o hardware, concordo: um mini-PC usado com 16 GB serve melhor do que o AI HAT+ 2. Os modelos prontos dessa placa vão até 1,5B, e o qwen2.5:3b que já uso não corre lá. O HAT fica como hipótese futura, com essa limitação escrita.

No lembrete, separo as duas coisas. Perceber «lembra-me da consulta na terça às 10h» usa o modelo. Disparar à hora, confirmar e adiar não usam o modelo nem a Internet.

A fase 1 fica mais curta: voz local, um lembrete criado por fala e disparado offline, uma música e uma história curta. A repetição diária e o conjunto de histórias guardadas passam para a etapa 2.

A AMALIA entra já na comparação, em Q4 no Ollama, ao lado do qwen2.5:3b. Só a troco se, no mesmo PC, falar melhor em português de Portugal e conseguir chamar a ferramenta de agendar.
