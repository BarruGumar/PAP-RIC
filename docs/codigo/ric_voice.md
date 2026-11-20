# `ric/voice/`

## TTS (`tts.py`)

**Motor do projeto: Piper** (`pt_PT-tugão-medium`).

Ordem: **Piper** → **SAPI** (Windows) → **espeak** (Linux).  
Síntese Piper: API `PiperVoice` → WAV PCM em `ric-data/tts/`.

**Reprodução na UI:** o browser toca o WAV (`audio_url` no evento WS `/ws` ou `GET /api/v1/tts/….wav`).

Alertas: `Atenção, é a hora de {título}.` · `length_scale` default **1.35**.  
Respostas (`stem="reply"`): ritmo **1.20** via `length_scale_for_stem`.

```text
py -m pip install piper-tts
```

**Default guardado:** `ric-data/vozes/pt_PT-tugao-medium.onnx` (**Piper 1.5.0**, retrain HF 2026-11-13).  
Backup: `ric-data/vozes/extras/pt_PT-tugao-medium-v1.0.onnx`.

**Nota:** Chatterbox (Resemble AI) foi testado e **descartado** na PAP — demasiado pesado/lento para o hardware alvo.

```text
py -m ric voices
py -m ric say "…" --model extras/OUTRA.onnx
```

Health: `/api/v1/health` → `voice.engine` / `voice.piper`.

## Wake (`wake.py` + `oww_detector.py`)

- `WakeWordService`: callback `on_detect`.
- **Sempre** disponível: `trigger_manual()` (botão «Falar» / `POST /api/v1/voice/wake`).
- **Contínuo:** `OpenWakeWordDetector` (`sounddevice` 16 kHz + openWakeWord).
  - Frase alvo: **«ei RIC»** (`ric-data/wake/ric.onnx` quando instalado).
  - Modelo: `RIC_WAKE_MODEL` → `ric-data/wake/ric.onnx` → fallback temporário **`hey_jarvis`**.
  - Pausa em `listening` / `thinking` / `speaking` / `alert` (anti-eco).
  - Debounce ~1,5 s; limiar `RIC_WAKE_THRESHOLD` (default 0,5).
  - Desligar: `RIC_WAKE_ENABLED=0`. Sem deps → modo `manual`.
- Setup base (1×): `py -m pip install openwakeword sounddevice numpy` → `py -m ric wake-setup`.
- Treino «ei RIC»: roteiro Colab [`docs/ROTEIRO-WAKE-EI-RIC.md`](../ROTEIRO-WAKE-EI-RIC.md) → `py -m ric wake-install CAMINHO\ei_ric.onnx`.
- Health: `voice.wake.mode` (`openwakeword`|`manual`), `phrase`, `model`.

## STT (`stt.py`)

- `SpeechToText` com backend injectável (testes) ou **faster-whisper** se instalado.
- `RIC_WHISPER_MODEL` (default **`small`** — melhor PT que `base`), `RIC_STT_LANGUAGE` (default `pt`).
- Decode: `beam_size=3` (e `best_of=3`; com `temperature=0` o best_of não entra em jogo).
- `vad_filter=False` (o browser corta silêncio).
- `join_transcript_segments`: rejeita segmentos com `no_speech_prob ≥ 0.6` ou `avg_logprob < -1.2`.
- `initial_prompt` curto (PT-PT). Prompt longo + beam baixo fazia o Whisper inventar frases.
- Warm-up: carrega o modelo e corre uma transcrição de WAV silencioso curto (aquece CTranslate2).
- Último áudio guardado em `ric-data/stt/last.wav` para debug.
- Sem pacote: `available=False` → API devolve 503 com mensagem clara.

```text
py -m pip install faster-whisper
```

UI: **tocar** Falar → falar ≥ ~0,35 s → **envia sozinho** após ~0,9 s de silêncio (ou toca **Parar**); máximo ~15 s.  
Microfone abre **antes** do wake; PCM a 16 kHz com silêncio cortado **antes** da normalização.

## Sessão (`session.py`)

Fluxo: **wake → listening → STT → LLM → TTS → idle**.

Publica o texto da resposta **antes** do TTS; o browser toca o áudio via WS.  
Timings no terminal: `[RIC] voz: stt=…s llm=…s tts=…s total=…s`.

Eventos WS: `wake_detected`, `stt_started`, `transcript`, `assistant_reply`, `stt_error`, `listen_cancelled`.
