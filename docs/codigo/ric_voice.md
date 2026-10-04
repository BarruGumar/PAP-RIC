# Explicação: `ric/voice.py`

## Para que serve

Camada de **voz local** do RIC:

- `beep()` — som curto de alerta (Windows `winsound` ou bell)
- `falar(texto)` — TTS sem cloud (SAPI via PowerShell; opcional `pyttsx3`)
- `estado()` — o que está disponível neste PC

## Onde é usada

1. **Watchdog** em `ric/web_server.py` — quando um lembrete vence, faz beep + fala mesmo se o browser falhar  
2. **UI** — `POST /api/voz/falar` quando o overlay mostra a frase do aviso  
3. **STT** — não está em Python; o botão **Falar** usa Web Speech API no browser (`app.js`)

## Degradação

Se TTS falhar, o RIC continua: overlay visual + beep/lista. A voz é atalho, não requisito.
