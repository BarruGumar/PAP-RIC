# Roteiro — audição da voz

**Data do roteiro:** 2026-10-18  
**Onde corre:** no PC do Pedro, em Windows. Neste repositório não se liga ainda o Piper nem o Whisper ao RIC.  
**Resultado:** por medir. As tabelas no fim ficam vazias até esta audição.

No PC a pasta do projeto é `C:\Users\pedro\Desktop\PAP`. Aí está o atalho `testar-voz.bat`. Um duplo clique cria a pasta `voz-teste` (não entra no git), descarrega o Piper tugão e abre dois wav. O resto deste roteiro é o mesmo teste, comando a comando, mais o Kokoro e o faster-whisper.

A primeira descarga precisa de Internet. A audição e o reconhecimento fazem-se depois com a rede desligada. O `qwen2.5:3b` fica aberto no Ollama durante o reconhecimento, para ver se os dois cabem.

Frase igual nas duas vozes:

`são dezasseis horas, hora do comprimido`

Segunda frase, para ver se a hora é lida à portuguesa:

`A consulta é às 16:54.`

## 1. Preparar a pasta

Na pasta `C:\Users\pedro\Desktop\PAP`, no PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path .\voz-teste | Out-Null
Set-Location .\voz-teste
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -U pip
py -m pip install piper-tts
```

Se `py -3.11` não existir, usa `py -3.12` ou o `py` que já corre o RIC. O `tts-eu-pt` pede Python 3.10 ou mais recente.

## 2. Piper, voz tugão

O nome oficial tem «ã» e o comando curto do Piper pode falhar. Descarrega os dois ficheiros com um nome simples. O `.json` tem de ficar ao lado do `.onnx`, com o mesmo nome mais `.json`.

```powershell
New-Item -ItemType Directory -Force -Path .\vozes | Out-Null
curl.exe -L -o .\vozes\pt_PT-tugao-medium.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_PT/tug%C3%A3o/medium/pt_PT-tug%C3%A3o-medium.onnx"
curl.exe -L -o .\vozes\pt_PT-tugao-medium.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_PT/tug%C3%A3o/medium/pt_PT-tug%C3%A3o-medium.onnx.json"
"são dezasseis horas, hora do comprimido" | py -m piper -m .\vozes\pt_PT-tugao-medium.onnx -f .\aviso-piper.wav
"A consulta é às 16:54." | py -m piper -m .\vozes\pt_PT-tugao-medium.onnx -f .\hora-piper.wav
Start-Process .\aviso-piper.wav
Start-Process .\hora-piper.wav
```

Ouve cada ficheiro uma vez, do princípio ao fim, sem repetir logo de seguida. Anota na tabela do fim.

## 3. Kokoro afinado para português de Portugal

O Kokoro oficial fala português do Brasil e não entra neste teste. Este pacote é o afinamento `tts-eu-pt`. A primeira execução descarrega cerca de 313 MB e instala o PyTorch. Faz isto no mesmo ambiente, depois do Piper.

```powershell
py -m pip install tts-eu-pt
tts-eu-pt "são dezasseis horas, hora do comprimido" aviso-eu-pt.wav
tts-eu-pt "A consulta é às 16:54." hora-eu-pt.wav
Start-Process .\aviso-eu-pt.wav
Start-Process .\hora-eu-pt.wav
```

Ouve outra vez a frase do comprimido, agora neste ficheiro, e a frase das 16:54. A pergunta da hora é se ouves «dezasseis e cinquenta e quatro» e não uma leitura algarismo a algarismo.

Fica a voz em que um aviso curto se percebe melhor. Se empatam, fica o Piper: o orientador já o testou e o ficheiro é pequeno.

## 4. faster-whisper

Desliga a rede só depois do modelo estar no disco. Antes disso, com Internet:

```powershell
py -m pip install faster-whisper
```

Abre o Ollama e carrega o modelo que já usas:

```powershell
ollama run qwen2.5:3b
```

Podes sair do chat com `/bye`. O processo do Ollama fica. Confirma no gestor de tarefas que ele está aberto. Desliga a rede.

Grava as dez frases, uma por ficheiro, com a Gravador de Voz do Windows. Fala como falarias com o RIC, uma vez, sem soletrar. Guarda em `frases\01.wav` até `frases\10.wav`.

| Ficheiro | Frase a dizer |
|---|---|
| 01.wav | lembra-me da consulta na terça às 10 |
| 02.wav | são dezasseis horas, hora do comprimido |
| 03.wav | lembra-me de beber água daqui a cinco minutos |
| 04.wav | toma o comprimido às dezasseis |
| 05.wav | adia o lembrete |
| 06.wav | já tomei |
| 07.wav | toca uma música calma |
| 08.wav | conta-me uma história curta |
| 09.wav | o meu nome é Pedro |
| 10.wav | que horas são |

Cria `transcrever.py` nesta pasta:

```python
from pathlib import Path

from faster_whisper import WhisperModel

modelo = WhisperModel("small", device="cpu", compute_type="int8")
pasta = Path("frases")

for wav in sorted(pasta.glob("*.wav")):
    segmentos, info = modelo.transcribe(str(wav), language="pt", beam_size=5)
    texto = "".join(s.text for s in segmentos).strip()
    print(f"{wav.name}\t{texto}")
```

Corre:

```powershell
py transcrever.py
```

A primeira vez o `small` descarrega-se. Se isso acontecer, volta a ligar a rede só para a descarga, corre uma vez, desliga a rede e corre outra vez. Essa segunda corrida é a que conta.

Se o PC não aguentar (fica sem memória, o comando não termina, ou o Ollama cai), troca na linha do `WhisperModel` o `"small"` por `"base"` e repete. Anota qual dos dois correu.

Copia as dez linhas para a tabela do fim. Uma frase conta como certa quando o sentido chega inteiro: dia, hora, remédio, música ou história. Um acento trocado não a invalida. «Terça» ou «10» perdidos invalidam a frase 01.

## 5. O que anotar

Preenche as três tabelas. Não ligues nada ao `ric/` com base neste roteiro. Quando as tabelas tiverem respostas, passam para [`TABELA-LLMS.md`](TABELA-LLMS.md) e para a nota em [`FEEDBACK-ORIENTADOR.md`](FEEDBACK-ORIENTADOR.md).

### Voz escolhida

| | Piper tugão | tts-eu-pt |
|---|---|---|
| A hora do comprimido percebe-se? | | |
| «16:54» soa a português de Portugal? | | |
| Notas (cortes, sotaque, velocidade) | | |
| Fico com esta voz? | | |

Voz escolhida: _______________  
Data: _______________  
PC e RAM: _______________

### Reconhecimento

Ollama aberto durante o teste: sim / não  
Modelo Whisper: small / base  
Rede desligada na corrida que conta: sim / não

| Ficheiro | Texto que o Whisper escreveu | Certo? |
|---|---|---|
| 01.wav | | |
| 02.wav | | |
| 03.wav | | |
| 04.wav | | |
| 05.wav | | |
| 06.wav | | |
| 07.wav | | |
| 08.wav | | |
| 09.wav | | |
| 10.wav | | |

Frases certas: ____ / 10

### Estado

Por medir no PC do Pedro. Sem estas linhas preenchidas, o RIC continua a falar pelo SAPI e a ouvir pelo navegador.
