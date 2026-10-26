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

  let activeAlertId = null
  let ws = null
  let lastPlayedKey = null
  let pendingAudioMsg = null
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
    })
    ws.addEventListener("close", () => {
      setTimeout(connectWs, 2000)
    })
  }

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
