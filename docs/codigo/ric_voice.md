# `ric/voice/`

## TTS (`tts.py`)

Ordem: **Piper** (modelo PT tugão) → **SAPI** (Windows) → **espeak** (Linux).

Síntese: API `PiperVoice` → WAV PCM em `ric-data/tts/alert.wav`.

**Reprodução na UI:** o browser toca o WAV (`audio_url` no evento WS `/ws` ou `GET /api/v1/tts/….wav`). Evita o áudio partido/ininteligível do playback nativo no Windows.

CLI/`speak()` ainda pode tocar localmente (SoundPlayer / SAPI) como fallback.

Alertas: `Atenção, é a hora de {título}.` (vírgula, **sem** ponto a meio — evita travadinha) · `length_scale` default **1.35**.

```text
py -m pip install piper-tts
# ou: .\testar-voz.ps1  (cria voz-teste\.venv com Piper + modelo)
```

**Default guardado:** `ric-data/vozes/pt_PT-tugao-medium.onnx` (não substituir por agora).  

**Backlog (em casa):** o Pedro encontrou **tugão quality** (qualidade superior) na página do Piper. Descarregar para `extras/`, comparar com medium via `say`, e só então decidir se muda o default. Ver [`docs/PLANEAMENTO.md`](../PLANEAMENTO.md).

**Testar outras:** meter `.onnx` em `ric-data/vozes/extras/` e:

```text
py -m ric voices
py -m ric say "Atenção, é a hora de beber água." --model extras/OUTRA.onnx
```

Para a UI usar outra voz só temporariamente: `RIC_PIPER_MODEL=...` no `.env`; para voltar, remove essa linha.

Reinicia `py -m ric ui` depois de instalar. Confirma em `/api/v1/health` → `voice.engine` deve ser `"piper"`.

## Wake (`wake.py`)

- `WakeWordService`: callback `on_detect`.
- **Sempre** disponível: `trigger_manual()` (botão «Falar» / `POST /api/v1/voice/wake`).
- openWakeWord contínuo: só quando houver detector injectado com modelo «RIC» (`ric-data/wake/` — ainda por treinar/ligar).

## STT (`stt.py`)

- `SpeechToText` com backend injectável (testes) ou **faster-whisper** se instalado.
- `RIC_WHISPER_MODEL` (default **`small`** — melhor PT que `base`), `RIC_STT_LANGUAGE` (default `pt`).
- Clips do botão: sem VAD agressivo; `beam_size=5`; `initial_prompt` com vocabulário RIC.
- Último áudio guardado em `ric-data/stt/last.wav` para debug.
- Sem pacote: `available=False` → API devolve 503 com mensagem clara.

```text
py -m pip install faster-whisper
```

UI: **tocar** Falar → falar ≥1 s → **tocar** outra vez (não é «segurar»). Áudio normalizado e reamostrado a 16 kHz no browser.

## Sessão (`session.py`)

Fluxo: **wake → listening → STT → LLM → TTS → idle**.

Eventos WS: `wake_detected`, `stt_started`, `transcript`, `assistant_reply`, `stt_error`, `listen_cancelled`.

