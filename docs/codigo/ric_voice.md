# `ric/voice/`

## TTS (`tts.py` + `chatterbox_engine.py`)

**Default estável: Piper.** Chatterbox é **experimental** e fica separado.

Ordem Piper: **Piper** (modelo PT tugão) → **SAPI** (Windows) → **espeak** (Linux).  
Síntese Piper: API `PiperVoice` → WAV PCM em `ric-data/tts/`.

**Reprodução na UI:** o browser toca o WAV (`audio_url` no evento WS `/ws` ou `GET /api/v1/tts/….wav`).

Alertas: `Atenção, é a hora de {título}.` · `length_scale` default **1.35**.  
Respostas (`stem="reply"`): ritmo **1.20** via `length_scale_for_stem`.

```text
py -m pip install piper-tts
```

**Default guardado:** `ric-data/vozes/pt_PT-tugao-medium.onnx` (não substituir por agora).

### Chatterbox experimental (pt-PT)

Pacote opcional — **não** entra no `requirements.txt` principal:

```text
python -m pip install -r requirements-chatterbox.txt
py -m ric tts-compare --play
py -m ric say "Olá, eu sou o RIC." --engine chatterbox
```

- Objectivo: português de **Portugal** (não BR). O modelo genérico com `language_id=pt` tende a sotaque brasileiro.
- Por defeito usa referência oficial pt-PT (`ric-data/vozes/extras/pt_pt_ref.wav`, descarregada à primeira).
- Pack dedicado `ResembleAI/Chatterbox-Multilingual-pt-pt` quando estiver no cache HF; senão fallback: base + referência Portugal.
- UI experimental: `RIC_TTS_ENGINE=chatterbox` no `.env` (volta a `piper` para o default).
- Clonagem zero-shot (opção escolhida): `py -m ric record-ref` ou `RIC_CHATTERBOX_AUDIO_PROMPT=…wav`.
- Fine-tune/LoRA: possível mas fora do caminho crítico da PAP.
- 1.ª corrida descarrega pesos HF (~GB); GPU ajuda; CPU é lenta.
- Se aparecer `LlamaModel` / `torchvision::nms`: reinstalar trio alinhado (ver `requirements-chatterbox.txt`).

### Comparar Piper vs Chatterbox

```text
py -m ric tts-compare "Atenção, é a hora de beber água." --play
```

WAV em `ric-data/tts/compare/`. Critérios: naturalidade pt-PT, clareza, latência.

**Backlog Piper:** tugão quality em `extras/` (ver [`PLANEAMENTO.md`](../PLANEAMENTO.md)).

```text
py -m ric voices
py -m ric say "…" --model extras/OUTRA.onnx
```

Health: `/api/v1/health` → `voice.engine` / `voice.engine_requested` / `voice.chatterbox`.

## Wake (`wake.py`)

- `WakeWordService`: callback `on_detect`.
- **Sempre** disponível: `trigger_manual()` (botão «Falar» / `POST /api/v1/voice/wake`).
- openWakeWord contínuo: só quando houver detector injectado com modelo «RIC» (`ric-data/wake/` — ainda por treinar/ligar).

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
Microfone abre **antes** do wake; PCM a 16 kHz com silêncio cortado **antes** da normalização (senão o ruído amplificado estraga o endpointing).

## Sessão (`session.py`)

Fluxo: **wake → listening → STT → LLM → TTS → idle**.

Publica o texto da resposta **antes** do TTS; o browser toca o áudio via WS.  
Timings no terminal: `[RIC] voz: stt=…s llm=…s tts=…s total=…s`.

Eventos WS: `wake_detected`, `stt_started`, `transcript`, `assistant_reply`, `stt_error`, `listen_cancelled`.
