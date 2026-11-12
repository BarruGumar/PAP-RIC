(() => {
  const appEl = document.getElementById("app")
  const controlsEl = document.getElementById("controls")
  const clockEl = document.getElementById("clock")
  const CONTROLS_IDLE_MS = 8000
  let controlsTimer = null
  const faceEl = document.getElementById("face")
  const stateLabelEl = document.getElementById("state-label")
  const nextEl = document.getElementById("next-reminder")
  const alertPanel = document.getElementById("alert-panel")
  const alertTitle = document.getElementById("alert-title")
  const btnConfirm = document.getElementById("btn-confirm")
  const btnSnooze = document.getElementById("btn-snooze")
  const form = document.getElementById("form-create")
  const formMsg = document.getElementById("form-msg")
  const btnTalk = document.getElementById("btn-talk")
  const btnPreview = document.getElementById("btn-preview")
  const heardEl = document.getElementById("heard")
  const previewPhrases = [
    "Atenção, é a hora de beber água.",
    "Olá, eu sou o RIC.",
    "Não te esqueças do teu lembrete.",
    "Boa noite, descansa bem.",
  ]
  let previewIndex = 0

  let activeAlertId = null
  let ws = null
  let lastPlayedKey = null
  let pendingAudioMsg = null
  let recording = false
  let mediaStream = null
  let audioContext = null
  let processor = null
  let pcmChunks = []
  let sampleRate = 16000
  let speechHeard = false
  let silenceSamples = 0
  let speechSamples = 0
  const AUTO_SILENCE_SEC = 0.9
  const MIN_SPEECH_SEC = 0.35
  const AUTO_MIN_SPEECH_SEC = 0.35
  const MAX_RECORD_SEC = 15
  const SILENCE_RMS = 0.012
  const TRIM_PAD_SEC = 0.16
  const ttsPlayer = document.getElementById("tts-player")
  ttsPlayer.volume = 0.85

  const stopAlertAudio = () => {
    pendingAudioMsg = null
    try {
      ttsPlayer.pause()
      ttsPlayer.removeAttribute("src")
      ttsPlayer.load()
    } catch {
      /* ignore */
    }
  }

  const startTts = (msg) => {
    if (!msg.audio_url) return
    const key = msg.play_id || `${msg.reminder && msg.reminder.id}-${msg.reminder && msg.reminder.avisos_feitos}`
    lastPlayedKey = key
    ttsPlayer.src = `${msg.audio_url}?t=${Date.now()}`
    ttsPlayer.currentTime = 0
    ttsPlayer.play().catch(() => {})
  }

  const playAlertAudio = (msg) => {
    try {
      const key = msg.play_id || `${msg.reminder && msg.reminder.id}-${msg.reminder && msg.reminder.avisos_feitos}`
      if (key === lastPlayedKey) return
      const busy = !ttsPlayer.paused && !ttsPlayer.ended && ttsPlayer.currentTime > 0
      if (busy) {
        // Guardar o mais recente — nunca dois ao mesmo tempo (eco)
        pendingAudioMsg = msg
        return
      }
      startTts(msg)
    } catch {
      /* ignore */
    }
  }

  ttsPlayer.addEventListener("ended", () => {
    if (!pendingAudioMsg) return
    const next = pendingAudioMsg
    pendingAudioMsg = null
    startTts(next)
  })

  const stateLabels = {
    idle: "À espera",
    listening: "A ouvir",
    thinking: "A pensar",
    speaking: "A falar",
    alert: "Aviso",
    music: "Música",
    story: "História",
  }

  const stateToExpression = {
    idle: "calm",
    listening: "curious",
    thinking: "think",
    speaking: "talk",
    alert: "alert",
    music: "happy",
    story: "sleepy",
  }

  const expressionLabels = {
    calm: "Calmo",
    curious: "Curioso",
    think: "A pensar",
    talk: "A falar",
    alert: "Alerta",
    focus: "Focado",
    happy: "Contente",
    sad: "Triste",
    surprised: "Surpreso",
    sleepy: "Sonolento",
    confused: "Confuso",
    wink: "Pisca",
    blink: "Piscar",
  }

  const exprButtons = Array.from(document.querySelectorAll(".btn-expr"))
  const eyeStyleButtons = Array.from(document.querySelectorAll(".btn-eye-style"))
  const EYE_STYLE_KEY = "ric-eye-style"

  const applyEyeStyle = (style) => {
    const safe = style === "pupil" ? "pupil" : "ring"
    faceEl.dataset.eyeStyle = safe
    try {
      localStorage.setItem(EYE_STYLE_KEY, safe)
    } catch (_) {
      /* ignore quota / private mode */
    }
    for (const btn of eyeStyleButtons) {
      const active = btn.dataset.eyeStyle === safe
      btn.classList.toggle("is-active", active)
      btn.setAttribute("aria-pressed", active ? "true" : "false")
    }
  }

  const readEyeStyle = () => {
    try {
      const saved = localStorage.getItem(EYE_STYLE_KEY)
      if (saved === "pupil" || saved === "ring") return saved
    } catch (_) {
      /* ignore */
    }
    return faceEl.dataset.eyeStyle || "ring"
  }

  let currentState = "idle"
  let labPreview = null
  let blinkTimer = null
  let lifeBlinkTimer = null
  let lifeGazeTimer = null
  let lifeIdleTimer = null
  let reduceMotion = false
  try {
    reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches
  } catch {
    reduceMotion = false
  }

  // Expressões base enquanto não há interação (idle)
  const IDLE_MOODS = [
    { expr: "calm", weight: 42, holdMin: 7000, holdMax: 14000 },
    { expr: "curious", weight: 18, holdMin: 2800, holdMax: 4800 },
    { expr: "happy", weight: 12, holdMin: 2200, holdMax: 3800 },
    { expr: "think", weight: 12, holdMin: 2800, holdMax: 4500 },
    { expr: "sleepy", weight: 10, holdMin: 3500, holdMax: 6000 },
    { expr: "confused", weight: 6, holdMin: 2200, holdMax: 3400 },
  ]

  const currentExpression = () => faceEl.dataset.expression || "calm"

  const canRunIdleMoods = () =>
    currentState === "idle" &&
    !labPreview &&
    !activeAlertId &&
    !recording &&
    !reduceMotion

  const pickIdleMood = () => {
    const total = IDLE_MOODS.reduce((sum, m) => sum + m.weight, 0)
    let roll = Math.random() * total
    for (const mood of IDLE_MOODS) {
      roll -= mood.weight
      if (roll <= 0) return mood
    }
    return IDLE_MOODS[0]
  }

  const setGaze = (x, y) => {
    faceEl.style.setProperty("--gaze-x", `${x}px`)
    faceEl.style.setProperty("--gaze-y", `${y}px`)
  }

  const clearLifeTimers = () => {
    if (lifeBlinkTimer) {
      clearTimeout(lifeBlinkTimer)
      lifeBlinkTimer = null
    }
    if (lifeGazeTimer) {
      clearTimeout(lifeGazeTimer)
      lifeGazeTimer = null
    }
    if (lifeIdleTimer) {
      clearTimeout(lifeIdleTimer)
      lifeIdleTimer = null
    }
  }

  const doBlink = (then) => {
    if (faceEl.classList.contains("is-blinking")) {
      if (then) then()
      return
    }
    // Fecha o path (círculo → linha) e reabre
    faceEl.classList.add("is-blinking")
    setTimeout(() => {
      faceEl.classList.remove("is-blinking")
      if (then) then()
    }, 200)
  }

  const scheduleLifeBlink = () => {
    if (reduceMotion) return
    // De vez em quando: ~3–8 s entre piscadelas
    const wait = 3000 + Math.random() * 5000
    lifeBlinkTimer = setTimeout(() => {
      lifeBlinkTimer = null
      if (reduceMotion) return
      const expr = currentExpression()
      if (expr === "alert" || expr === "focus" || labPreview === "blink") {
        scheduleLifeBlink()
        return
      }
      if (recording || activeAlertId) {
        scheduleLifeBlink()
        return
      }
      const double = Math.random() < 0.15
      doBlink(() => {
        if (double) {
          setTimeout(() => doBlink(() => scheduleLifeBlink()), 180)
        } else {
          scheduleLifeBlink()
        }
      })
    }, wait)
  }

  const scheduleLifeGaze = () => {
    if (reduceMotion) return
    const wait = 3500 + Math.random() * 5000
    lifeGazeTimer = setTimeout(() => {
      lifeGazeTimer = null
      const expr = currentExpression()
      if (expr === "alert" || expr === "talk" || labPreview === "blink") {
        setGaze(0, 0)
        scheduleLifeGaze()
        return
      }
      if (expr === "think") {
        setGaze(4 + Math.random() * 3, 1 + Math.random() * 2)
      } else if (expr === "curious") {
        setGaze((Math.random() < 0.5 ? -1 : 1) * (2 + Math.random() * 3), -1)
      } else {
        const dirs = [
          [0, 0],
          [0, 0],
          [0, 0],
          [-3, 0],
          [3, 0],
          [-2, 1],
          [2, -1],
        ]
        const pick = dirs[Math.floor(Math.random() * dirs.length)]
        setGaze(pick[0], pick[1])
      }
      scheduleLifeGaze()
    }, wait)
  }

  const setExpressionPose = (expression, { markLab = true, restartLife = false } = {}) => {
    const safe = expressionLabels[expression] ? expression : "calm"
    faceEl.dataset.expression = safe
    if (markLab) markExprButtons(safe)
    if (safe === "alert" || safe === "talk") setGaze(0, 0)
    if (restartLife) restartFaceLife()
  }

  const scheduleIdleMood = () => {
    if (lifeIdleTimer) {
      clearTimeout(lifeIdleTimer)
      lifeIdleTimer = null
    }
    if (!canRunIdleMoods()) return
    // Pausa entre mudanças — não ficar a trocar sem parar
    const gap = 4000 + Math.random() * 7000
    lifeIdleTimer = setTimeout(() => {
      lifeIdleTimer = null
      if (!canRunIdleMoods()) return
      const mood = pickIdleMood()
      setExpressionPose(mood.expr, { markLab: false, restartLife: false })
      const hold =
        mood.holdMin + Math.random() * Math.max(0, mood.holdMax - mood.holdMin)
      lifeIdleTimer = setTimeout(() => {
        lifeIdleTimer = null
        if (!canRunIdleMoods()) return
        // Voltar quase sempre ao calmo antes da próxima
        if (mood.expr !== "calm") {
          setExpressionPose("calm", { markLab: false, restartLife: false })
          lifeIdleTimer = setTimeout(() => {
            lifeIdleTimer = null
            scheduleIdleMood()
          }, 2500 + Math.random() * 3500)
        } else {
          scheduleIdleMood()
        }
      }, hold)
    }, gap)
  }

  const restartFaceLife = () => {
    clearLifeTimers()
    faceEl.classList.remove("is-blinking")
    if (reduceMotion) {
      setGaze(0, 0)
      return
    }
    scheduleLifeBlink()
    scheduleLifeGaze()
    scheduleIdleMood()
  }

  const markExprButtons = (expression) => {
    for (const btn of exprButtons) {
      btn.classList.toggle("is-active", btn.dataset.expression === expression)
    }
  }

  const applyExpression = (expression) => {
    setExpressionPose(expression, { markLab: true, restartLife: true })
  }

  const setFace = (state) => {
    const safe = stateLabels[state] ? state : "idle"
    currentState = safe
    labPreview = null
    if (blinkTimer) {
      clearTimeout(blinkTimer)
      blinkTimer = null
    }
    faceEl.className = `face theme-eve state-${safe}`
    applyExpression(stateToExpression[safe] || "calm")
    faceEl.setAttribute("aria-label", `Estado: ${safe}`)
    stateLabelEl.textContent = stateLabels[safe] || safe
  }

  const restoreAfterOneShot = (token) => {
    if (labPreview !== token) return
    labPreview = null
    applyExpression(stateToExpression[currentState] || "calm")
    stateLabelEl.textContent = stateLabels[currentState] || currentState
    markExprButtons(stateToExpression[currentState] || "calm")
  }

  const previewExpression = (expression) => {
    const safe = expressionLabels[expression] ? expression : "calm"
    if (safe === "blink") {
      labPreview = "blink"
      stateLabelEl.textContent = "Piscar"
      markExprButtons("blink")
      doBlink(() => restoreAfterOneShot("blink"))
      return
    }
    if (safe === "wink") {
      labPreview = "wink"
      applyExpression("wink")
      stateLabelEl.textContent = "Pisca"
      markExprButtons("wink")
      if (blinkTimer) clearTimeout(blinkTimer)
      blinkTimer = setTimeout(() => {
        blinkTimer = null
        restoreAfterOneShot("wink")
      }, 700)
      return
    }
    // Em idle, «Calmo» liberta o laboratório e volta às expressões base
    labPreview = safe === "calm" && currentState === "idle" ? null : safe
    applyExpression(safe)
    stateLabelEl.textContent =
      labPreview === null ? stateLabels.idle : expressionLabels[safe]
    faceEl.setAttribute(
      "aria-label",
      labPreview === null ? "Estado: idle" : `Expressão: ${safe}`
    )
  }

  const tickClock = () => {
    const now = new Date()
    clockEl.textContent = now.toLocaleTimeString("pt-PT", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const showNext = (reminder) => {
    if (!reminder) {
      nextEl.textContent = "Próximo"
      return
    }
    nextEl.textContent = `Próximo: ${reminder.hora}`
  }

  const closeControls = () => {
    window.clearTimeout(controlsTimer)
    controlsTimer = null
    controlsEl.hidden = true
    appEl.classList.remove("is-open")
    const panel = document.getElementById("create-panel")
    if (panel) panel.hidden = true
  }

  const armControlsIdle = () => {
    window.clearTimeout(controlsTimer)
    controlsTimer = window.setTimeout(closeControls, CONTROLS_IDLE_MS)
  }

  const openControls = () => {
    if (activeAlertId) return
    controlsEl.hidden = false
    appEl.classList.add("is-open")
    armControlsIdle()
  }

  const showAlert = (reminder) => {
    activeAlertId = reminder.id
    alertTitle.textContent = reminder.titulo
    const alertTime = document.getElementById("alert-time")
    if (alertTime) alertTime.textContent = reminder.hora || ""
    alertPanel.classList.remove("hidden")
    appEl.classList.add("is-alert")
    closeControls()
    setFace("alert")
  }

  const hideAlert = () => {
    activeAlertId = null
    stopAlertAudio()
    alertPanel.classList.add("hidden")
    appEl.classList.remove("is-alert")
    closeControls()
    setFace("idle")
  }

  const api = async (path, options) => {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    })
    const payload = await res.json()
    if (!payload.ok) {
      throw new Error(payload.error || "Erro")
    }
    return payload.data
  }

  const refreshNext = async () => {
    const data = await api("/api/v1/reminders/next")
    showNext(data)
  }

  const connectWs = () => {
    const proto = location.protocol === "https:" ? "wss" : "ws"
    ws = new WebSocket(`${proto}://${location.host}/ws`)
    ws.addEventListener("message", (ev) => {
      let msg
      try {
        msg = JSON.parse(ev.data)
      } catch {
        return
      }
      if (msg.type === "state" && msg.state) {
        if (msg.state !== "alert" || !activeAlertId) {
          setFace(msg.state)
        }
        if (msg.state === "thinking") {
          const heard = String(heardEl.textContent || "")
          if (!heard.startsWith("Ouvi:") && !heard.startsWith("Ric:")) {
            heardEl.textContent = "A reconhecer"
          }
        }
      }
      if (msg.type === "next_reminder") {
        showNext(msg.reminder)
      }
      if (msg.type === "alert" && msg.reminder) {
        showAlert(msg.reminder)
        playAlertAudio(msg)
      }
      if (msg.type === "reminder_confirmed" || msg.type === "reminder_snoozed") {
        hideAlert()
        refreshNext()
      }
      if (msg.type === "reminders_changed") {
        refreshNext()
      }
      if (msg.type === "transcript" && typeof msg.text === "string") {
        heardEl.textContent = msg.text ? msg.text : "Não percebi"
      }
      if (msg.type === "assistant_reply" && typeof msg.text === "string") {
        heardEl.textContent = msg.text || heardEl.textContent
        if (msg.audio_url) {
          playAlertAudio({
            audio_url: msg.audio_url,
            play_id: msg.play_id || `reply-${Date.now()}`,
          })
        }
      }
      if (msg.type === "stt_error" && msg.error) {
        heardEl.textContent = msg.error
      }
      if (msg.type === "tts_preview" && msg.audio_url) {
        playAlertAudio(msg)
        if (msg.text) heardEl.textContent = `A dizer: ${msg.text}`
      }
    })
    ws.addEventListener("close", () => {
      setTimeout(connectWs, 2000)
    })
  }

  const mergeChunks = (floatChunks) => {
    let length = 0
    for (const chunk of floatChunks) length += chunk.length
    const samples = new Float32Array(length)
    let offset = 0
    for (const chunk of floatChunks) {
      samples.set(chunk, offset)
      offset += chunk.length
    }
    return samples
  }

  const resampleTo16k = (samples, fromRate) => {
    if (!fromRate || Math.abs(fromRate - 16000) < 1) return samples
    const ratio = fromRate / 16000
    const newLen = Math.max(1, Math.round(samples.length / ratio))
    const out = new Float32Array(newLen)
    for (let i = 0; i < newLen; i += 1) {
      const src = i * ratio
      const i0 = Math.floor(src)
      const i1 = Math.min(i0 + 1, samples.length - 1)
      const t = src - i0
      out[i] = samples[i0] * (1 - t) + samples[i1] * t
    }
    return out
  }

  const normalizePcm = (samples) => {
    let peak = 0
    for (let i = 0; i < samples.length; i += 1) {
      const a = Math.abs(samples[i])
      if (a > peak) peak = a
    }
    if (peak < 0.01) return samples
    const gain = Math.min(0.92 / peak, 8)
    if (gain < 1.05) return samples
    const out = new Float32Array(samples.length)
    for (let i = 0; i < samples.length; i += 1) out[i] = samples[i] * gain
    return out
  }

  const rmsOf = (samples) => {
    if (!samples.length) return 0
    let sum = 0
    for (let i = 0; i < samples.length; i += 1) {
      const v = samples[i]
      sum += v * v
    }
    return Math.sqrt(sum / samples.length)
  }

  const trimSilence = (samples, rate) => {
    if (!samples.length) return samples
    const pad = Math.floor(rate * TRIM_PAD_SEC)
    const frame = Math.max(1, Math.floor(rate * 0.02))
    let first = -1
    let last = -1
    for (let i = 0; i + frame <= samples.length; i += frame) {
      const slice = samples.subarray(i, i + frame)
      if (rmsOf(slice) >= SILENCE_RMS) {
        if (first < 0) first = i
        last = i + frame
      }
    }
    if (first < 0) return samples
    const start = Math.max(0, first - pad)
    const end = Math.min(samples.length, last + pad)
    return samples.subarray(start, end)
  }

  const encodeWav = (samples, rate) => {
    const buffer = new ArrayBuffer(44 + samples.length * 2)
    const view = new DataView(buffer)
    const writeStr = (pos, str) => {
      for (let i = 0; i < str.length; i += 1) view.setUint8(pos + i, str.charCodeAt(i))
    }
    writeStr(0, "RIFF")
    view.setUint32(4, 36 + samples.length * 2, true)
    writeStr(8, "WAVE")
    writeStr(12, "fmt ")
    view.setUint32(16, 16, true)
    view.setUint16(20, 1, true)
    view.setUint16(22, 1, true)
    view.setUint32(24, rate, true)
    view.setUint32(28, rate * 2, true)
    view.setUint16(32, 2, true)
    view.setUint16(34, 16, true)
    writeStr(36, "data")
    view.setUint32(40, samples.length * 2, true)
    let pos = 44
    for (let i = 0; i < samples.length; i += 1) {
      const s = Math.max(-1, Math.min(1, samples[i]))
      view.setInt16(pos, s < 0 ? s * 0x8000 : s * 0x7fff, true)
      pos += 2
    }
    return buffer
  }

  const bytesToBase64 = (buffer) => {
    const bytes = new Uint8Array(buffer)
    let binary = ""
    const chunk = 0x8000
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode(...bytes.subarray(i, i + chunk))
    }
    return btoa(binary)
  }

  const stopMicHardware = () => {
    if (processor) {
      try {
        processor.disconnect()
      } catch {
        /* ignore */
      }
      processor.onaudioprocess = null
      processor = null
    }
    if (audioContext) {
      audioContext.close().catch(() => {})
      audioContext = null
    }
    if (mediaStream) {
      mediaStream.getTracks().forEach((t) => t.stop())
      mediaStream = null
    }
  }

  const resetTalkButton = () => {
    btnTalk.classList.remove("recording")
    btnTalk.textContent = "Falar"
    btnTalk.setAttribute("aria-label", "Carregar para falar")
  }

  const finishRecording = async () => {
    if (!recording) return
    recording = false
    resetTalkButton()
    stopMicHardware()
    const chunks = pcmChunks
    pcmChunks = []
    speechHeard = false
    silenceSamples = 0
    speechSamples = 0
    if (!chunks.length) {
      await api("/api/v1/voice/cancel", { method: "POST", body: "{}" }).catch(() => {})
      heardEl.textContent = "Não gravei áudio."
      return
    }
    let samples = mergeChunks(chunks)
    samples = resampleTo16k(samples, sampleRate)
    // Trim antes de normalizar — senão o ganho reergue o ruído de fundo.
    samples = trimSilence(samples, 16000)
    samples = normalizePcm(samples)
    const durationSec = samples.length / 16000
    if (durationSec < MIN_SPEECH_SEC) {
      await api("/api/v1/voice/cancel", { method: "POST", body: "{}" }).catch(() => {})
      heardEl.textContent = "Fala um pouco mais."
      setFace("idle")
      return
    }
    heardEl.textContent = "A reconhecer…"
    try {
      const wav = encodeWav(samples, 16000)
      const audio_base64 = bytesToBase64(wav)
      // Texto e TTS chegam pelo WebSocket (mais cedo). Este POST só confirma o ciclo.
      const data = await api("/api/v1/voice/utterance", {
        method: "POST",
        body: JSON.stringify({ audio_base64, content_type: "audio/wav" }),
      })
      if (data.reply) {
        if (!String(heardEl.textContent || "").startsWith("Ric:")) {
          heardEl.textContent = `Ric: ${data.reply}`
        }
      } else if (!String(heardEl.textContent || "").startsWith("Ouvi:")) {
        heardEl.textContent = data.text
          ? `Ouvi: ${data.text}`
          : "Não percebi. Tenta outra vez."
      }
      // Fallback se o WS falhar a meio do turno (play_id estável evita eco).
      if (data.audio_url) {
        playAlertAudio({
          audio_url: data.audio_url,
          play_id: data.play_id || `reply-http-${Date.now()}`,
        })
      }
    } catch (err) {
      heardEl.textContent = err.message || "Erro ao reconhecer a voz."
      setFace("idle")
    }
  }

  const maybeAutoFinish = (chunk) => {
    if (!recording) return
    const energy = rmsOf(chunk)
    const n = chunk.length
    let recorded = 0
    for (let i = 0; i < pcmChunks.length; i += 1) recorded += pcmChunks[i].length
    if (recorded / sampleRate >= MAX_RECORD_SEC) {
      finishRecording()
      return
    }
    if (energy >= SILENCE_RMS) {
      speechHeard = true
      speechSamples += n
      silenceSamples = 0
      return
    }
    if (!speechHeard) return
    silenceSamples += n
    const speechSec = speechSamples / sampleRate
    const silenceSec = silenceSamples / sampleRate
    if (speechSec >= AUTO_MIN_SPEECH_SEC && silenceSec >= AUTO_SILENCE_SEC) {
      finishRecording()
    }
  }

  const startRecording = async () => {
    if (recording || activeAlertId) return
    recording = true
    speechHeard = false
    silenceSamples = 0
    speechSamples = 0
    heardEl.textContent = "A ouvir… paro sozinho quando acabares (ou toca em Parar)"
    btnTalk.classList.add("recording")
    btnTalk.textContent = "Parar"
    btnTalk.setAttribute("aria-label", "Parar e enviar")
    try {
      // Microfone primeiro — não esperar pelo wake (corta menos o início da fala).
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })
      if (!recording) {
        stopMicHardware()
        return
      }
      api("/api/v1/voice/wake", { method: "POST", body: "{}" }).catch(() => {})
      // Não forçar 16 kHz no AudioContext (muitos browsers ignoram / distorcem).
      audioContext = new (window.AudioContext || window.webkitAudioContext)()
      sampleRate = audioContext.sampleRate
      const source = audioContext.createMediaStreamSource(mediaStream)
      processor = audioContext.createScriptProcessor(4096, 1, 1)
      pcmChunks = []
      processor.onaudioprocess = (ev) => {
        if (!recording) return
        const input = ev.inputBuffer.getChannelData(0)
        const copy = new Float32Array(input)
        pcmChunks.push(copy)
        maybeAutoFinish(copy)
      }
      const mute = audioContext.createGain()
      mute.gain.value = 0
      source.connect(processor)
      processor.connect(mute)
      mute.connect(audioContext.destination)
      setFace("listening")
    } catch (err) {
      stopMicHardware()
      recording = false
      resetTalkButton()
      await api("/api/v1/voice/cancel", { method: "POST", body: "{}" }).catch(() => {})
      heardEl.textContent =
        err && err.message
          ? err.message
          : "Microfone indisponível. Permite o acesso ao microfone."
      setFace("idle")
    }
  }

  const handleTalkClick = (ev) => {
    ev.preventDefault()
    if (recording) finishRecording()
    else startRecording()
  }

  btnTalk.addEventListener("click", handleTalkClick)
  btnTalk.addEventListener("keydown", (ev) => {
    if (ev.key === " " || ev.key === "Enter") {
      ev.preventDefault()
      handleTalkClick(ev)
    }
  })

  btnPreview.addEventListener("click", async () => {
    if (activeAlertId || recording) return
    const text = previewPhrases[previewIndex % previewPhrases.length]
    previewIndex += 1
    heardEl.textContent = `A dizer: ${text}`
    try {
      const data = await api("/api/v1/voice/preview", {
        method: "POST",
        body: JSON.stringify({ text }),
      })
      if (data.audio_url) {
        playAlertAudio({
          audio_url: data.audio_url,
          play_id: `preview-${Date.now()}`,
        })
      }
    } catch (err) {
      heardEl.textContent = err.message || "Não consegui gerar a voz."
    }
  })

  btnConfirm.addEventListener("click", async () => {
    if (!activeAlertId) return
    try {
      await api(`/api/v1/reminders/${activeAlertId}/confirm`, { method: "POST", body: "{}" })
      hideAlert()
      await refreshNext()
    } catch (err) {
      formMsg.textContent = err.message
    }
  })

  btnSnooze.addEventListener("click", async () => {
    if (!activeAlertId) return
    try {
      await api(`/api/v1/reminders/${activeAlertId}/snooze`, {
        method: "POST",
        body: JSON.stringify({ minutes: 10 }),
      })
      hideAlert()
      await refreshNext()
    } catch (err) {
      formMsg.textContent = err.message
    }
  })

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault()
    formMsg.textContent = ""
    const titulo = document.getElementById("input-titulo").value
    const hora = document.getElementById("input-hora").value
    try {
      await api("/api/v1/reminders", {
        method: "POST",
        body: JSON.stringify({ titulo, hora, tipo: "tarefa", critico: false }),
      })
      form.reset()
      formMsg.textContent = "Lembrete guardado."
      await refreshNext()
    } catch (err) {
      formMsg.textContent = err.message
    }
  })

  for (const btn of exprButtons) {
    btn.addEventListener("click", () => {
      previewExpression(btn.dataset.expression || "calm")
    })
  }

  for (const btn of eyeStyleButtons) {
    btn.addEventListener("click", () => {
      applyEyeStyle(btn.dataset.eyeStyle || "ring")
    })
  }

  document.getElementById("btn-add").addEventListener("click", () => {
    const panel = document.getElementById("create-panel")
    panel.hidden = !panel.hidden
    if (!panel.hidden) document.getElementById("input-titulo").focus()
  })

  appEl.addEventListener("click", (event) => {
    if (activeAlertId) return
    if (event.target.closest("#controls")) {
      armControlsIdle()
      return
    }
    if (controlsEl.hidden) openControls()
    else closeControls()
  })

  applyEyeStyle(readEyeStyle())
  tickClock()
  setInterval(tickClock, 1000)
  setFace("idle")
  refreshNext().catch(() => {})
  connectWs()
})()
