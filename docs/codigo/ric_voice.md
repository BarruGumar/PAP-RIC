# `ric/voice/`

## TTS (`tts.py`)

Ordem: **Piper** (modelo PT tugão) → **SAPI** (Windows) → **espeak** (Linux).

Síntese: API `PiperVoice` → WAV PCM em `ric-data/tts/alert.wav`.

**Reprodução na UI:** o browser toca o WAV (`audio_base64` no evento WS `/ws` ou `GET /api/v1/tts/alert.wav`). Evita o áudio partido/ininteligível do playback nativo no Windows.

CLI/`speak()` ainda pode tocar localmente (SoundPlayer / SAPI) como fallback.

Alertas: `Atenção. {título}.` · fala ~15% mais lenta · noise do JSON do modelo.

```text
py -m pip install piper-tts
# ou: .\testar-voz.ps1  (cria voz-teste\.venv com Piper + modelo)
```

**Default guardado:** `ric-data/vozes/pt_PT-tugao-medium.onnx` (não substituir).  
**Testar outras:** meter `.onnx` em `ric-data/vozes/extras/` e:

```text
py -m ric voices
py -m ric say "Atenção, é a hora de beber água." --model extras/OUTRA.onnx
```

Para a UI usar outra voz só temporariamente: `RIC_PIPER_MODEL=...` no `.env`; para voltar, remove essa linha.

Reinicia `py -m ric ui` depois de instalar. Confirma em `/api/v1/health` → `voice.engine` deve ser `"piper"`.

## Stubs

- `wake.py` — openWakeWord «RIC» (próxima fatia)
- `stt.py` — Whisper local (próxima fatia)
