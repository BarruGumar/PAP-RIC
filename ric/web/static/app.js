(() => {
  const clockEl = document.getElementById("clock")
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

  const setFace = (state) => {
    const safe = stateLabels[state] ? state : "idle"
    faceEl.className = `face state-${safe}`
    faceEl.setAttribute("aria-label", `Estado: ${safe}`)
    stateLabelEl.textContent = stateLabels[safe] || safe
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
      nextEl.textContent = "Nenhum lembrete"
      return
    }
    nextEl.textContent = `${reminder.hora} — ${reminder.titulo}`
  }

  const showAlert = (reminder) => {
    activeAlertId = reminder.id
    alertTitle.textContent = reminder.titulo
    alertPanel.classList.remove("hidden")
    setFace("alert")
  }

  const hideAlert = () => {
    activeAlertId = null
    stopAlertAudio()
    alertPanel.classList.add("hidden")
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
        heardEl.textContent = msg.text
          ? `Ouvi: ${msg.text}`
          : "Não percebi. Tenta outra vez."
      }
      if (msg.type === "assistant_reply" && typeof msg.text === "string") {
        heardEl.textContent = msg.text ? `Ric: ${msg.text}` : heardEl.textContent
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
    if (!chunks.length) {
      await api("/api/v1/voice/cancel", { method: "POST", body: "{}" }).catch(() => {})
      heardEl.textContent = "Não gravei áudio."
      return
    }
    let samples = mergeChunks(chunks)
    samples = resampleTo16k(samples, sampleRate)
    samples = normalizePcm(samples)
    const durationSec = samples.length / 16000
    if (durationSec < 0.7) {
      await api("/api/v1/voice/cancel", { method: "POST", body: "{}" }).catch(() => {})
      heardEl.textContent = "Fala um pouco mais (cerca de 1 segundo)."
      setFace("idle")
      return
    }
    heardEl.textContent = "A reconhecer…"
    try {
      const wav = encodeWav(samples, 16000)
      const audio_base64 = bytesToBase64(wav)
      const data = await api("/api/v1/voice/utterance", {
        method: "POST",
        body: JSON.stringify({ audio_base64, content_type: "audio/wav" }),
      })
      if (data.reply) {
        heardEl.textContent = `Ric: ${data.reply}`
        if (data.audio_url) {
          playAlertAudio({
            audio_url: data.audio_url,
            play_id: `reply-${Date.now()}`,
          })
        }
      } else {
        heardEl.textContent = data.text
          ? `Ouvi: ${data.text}`
          : "Não percebi. Tenta outra vez."
      }
    } catch (err) {
      heardEl.textContent = err.message || "Erro ao reconhecer a voz."
      setFace("idle")
    }
  }

  const startRecording = async () => {
    if (recording || activeAlertId) return
    recording = true
    heardEl.textContent = "A ouvir… toca outra vez para enviar"
    btnTalk.classList.add("recording")
    btnTalk.textContent = "Parar"
    btnTalk.setAttribute("aria-label", "Parar e enviar")
    try {
      await api("/api/v1/voice/wake", { method: "POST", body: "{}" })
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })
      // Não forçar 16 kHz no AudioContext (muitos browsers ignoram / distorcem).
      audioContext = new (window.AudioContext || window.webkitAudioContext)()
      sampleRate = audioContext.sampleRate
      const source = audioContext.createMediaStreamSource(mediaStream)
      processor = audioContext.createScriptProcessor(4096, 1, 1)
      pcmChunks = []
      processor.onaudioprocess = (ev) => {
        const input = ev.inputBuffer.getChannelData(0)
        pcmChunks.push(new Float32Array(input))
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

  tickClock()
  setInterval(tickClock, 1000)
  setFace("idle")
  refreshNext().catch(() => {})
  connectWs()
})()
