(() => {
  const formChat = document.getElementById("form-chat")
  const chatInput = document.getElementById("chat-input")
  const chatLog = document.getElementById("chat-log")
  const chatMsg = document.getElementById("chat-msg")
  const btnEnviar = document.getElementById("btn-enviar")
  const btnFalar = document.getElementById("btn-falar")
  const sttLang = document.getElementById("stt-lang")
  const sttNota = document.getElementById("stt-nota")
  const llmEstado = document.getElementById("llm-estado")
  const perfilLinha = document.getElementById("perfil-linha")
  const ricFace = document.getElementById("ric-face")
  const lista = document.getElementById("lembretes")
  const listaVazia = document.getElementById("lista-vazia")
  const generosEl = document.getElementById("generos")
  const musicasEl = document.getElementById("musicas")
  const musicaVazia = document.getElementById("musica-vazia")
  const nowPlaying = document.getElementById("now-playing")
  const playerPos = document.getElementById("player-pos")
  const audio = document.getElementById("audio")
  const btnPausar = document.getElementById("btn-pausar")
  const btnContinuar = document.getElementById("btn-continuar")
  const btnReiniciar = document.getElementById("btn-reiniciar")
  const volumeInput = document.getElementById("volume")
  const volumeLabel = document.getElementById("volume-label")
  const relogio = document.getElementById("relogio")
  const overlay = document.getElementById("overlay")
  const alertaTitulo = document.getElementById("alerta-titulo")
  const alertaFrase = document.getElementById("alerta-frase")
  const alertaMeta = document.getElementById("alerta-meta")
  const btnOk = document.getElementById("btn-ok")
  const btnAdiar = document.getElementById("btn-adiar")

  let alertaAtual = null
  let generoAtivo = null
  let faixaAtual = null
  let audioCtx = null
  let recognition = null
  let aOuvir = false
  let sttBuffer = ""
  let sttEnviarAoFim = false
  let sttSilenceTimer = null
  let sttMaxTimer = null
  const STT_LANG_KEY = "ric_stt_lang"
  const STT_SILENCE_MS = 1600
  const STT_MAX_MS = 12000
  const STORAGE_KEY = "ric_player_state"
  const VOLUME_KEY = "ric_player_volume"
  const jaAlertados = new Set()
  const historico = []

  const handleApi = async (path, options = {}) => {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) throw new Error(data.erro || "Pedido falhou.")
    return data
  }

  const setFace = (state) => {
    if (!ricFace) return
    ricFace.classList.remove("listening", "thinking", "alerting")
    ricFace.classList.add(state)
    ricFace.dataset.state = state
  }

  const mostrarChatMsg = (texto) => {
    chatMsg.hidden = !texto
    chatMsg.textContent = texto || ""
  }

  const addBubble = (role, texto, extraClass = "") => {
    const div = document.createElement("div")
    div.className = `bubble ${role}` + (extraClass ? ` ${extraClass}` : "")
    div.textContent = texto
    chatLog.appendChild(div)
    chatLog.scrollTop = chatLog.scrollHeight
    return div
  }

  const atualizarRelogio = () => {
    relogio.textContent = new Date().toLocaleTimeString("pt-PT", {
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const fmtTempo = (seg) => {
    if (!Number.isFinite(seg) || seg < 0) return "00:00"
    const m = Math.floor(seg / 60)
    const s = Math.floor(seg % 60)
    return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
  }

  const atualizarPosicao = () => {
    playerPos.textContent = `${fmtTempo(audio.currentTime)} / ${fmtTempo(audio.duration)}`
  }

  const guardarEstado = () => {
    if (!faixaAtual) return
    const estado = {
      id: faixaAtual.id,
      titulo: faixaAtual.titulo,
      genero: faixaAtual.genero,
      url: faixaAtual.url,
      currentTime: audio.currentTime || 0,
      paused: audio.paused,
    }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(estado))
    } catch (_) {}
  }

  const lerEstado = () => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? JSON.parse(raw) : null
    } catch (_) {
      return null
    }
  }

  const desbloquearAudio = () => {
    try {
      const AC = window.AudioContext || window.webkitAudioContext
      if (!AC) return
      if (!audioCtx) audioCtx = new AC()
      if (audioCtx.state === "suspended") audioCtx.resume()
    } catch (_) {}
  }

  const atualizarNowPlaying = (extra = "") => {
    if (!faixaAtual) {
      nowPlaying.textContent = "Nada a tocar"
      return
    }
    const base = `${faixaAtual.titulo} · ${faixaAtual.genero}`
    nowPlaying.textContent = extra ? `${base} · ${extra}` : base
  }

  const atualizarPerfilLinha = (perfil) => {
    if (!perfil || !Object.keys(perfil).length) {
      perfilLinha.hidden = true
      perfilLinha.textContent = ""
      return
    }
    const nome = perfil.nome
    perfilLinha.hidden = false
    perfilLinha.textContent = nome ? `Olá, ${nome}` : "Preferências guardadas"
  }

  const pausarMusica = () => {
    if (!faixaAtual) {
      nowPlaying.textContent = "Nenhuma música a decorrer"
      return
    }
    audio.pause()
    guardarEstado()
    atualizarNowPlaying("em pausa")
    atualizarPosicao()
  }

  const continuarMusica = () => {
    if (!faixaAtual && !audio.src) {
      const salvo = lerEstado()
      if (salvo && salvo.url) {
        restaurarEstado(salvo, true)
        return
      }
      nowPlaying.textContent = "Nenhuma música para continuar"
      return
    }
    const p = audio.play()
    if (p && typeof p.then === "function") {
      p.then(() => {
        atualizarNowPlaying("a tocar")
        guardarEstado()
      }).catch(() => {
        atualizarNowPlaying("clica ▶ no leitor")
      })
    } else {
      atualizarNowPlaying("a tocar")
      guardarEstado()
    }
  }

  const reiniciarMusica = () => {
    if (!faixaAtual) {
      const salvo = lerEstado()
      if (salvo && salvo.url) {
        restaurarEstado({ ...salvo, currentTime: 0, paused: false }, true)
        return
      }
      nowPlaying.textContent = "Nenhuma música para reiniciar"
      return
    }
    try {
      audio.currentTime = 0
    } catch (_) {}
    const p = audio.play()
    if (p && typeof p.then === "function") {
      p.then(() => {
        atualizarNowPlaying("do começo")
        guardarEstado()
        atualizarPosicao()
      }).catch(() => {
        atualizarNowPlaying("clica ▶ no leitor")
        guardarEstado()
      })
    } else {
      atualizarNowPlaying("do começo")
      guardarEstado()
      atualizarPosicao()
    }
  }

  const aplicarVolume = (nivel) => {
    const v = Math.max(0, Math.min(1, Number(nivel)))
    audio.volume = v
    volumeInput.value = String(Math.round(v * 100))
    volumeLabel.textContent = `${Math.round(v * 100)}%`
    volumeInput.setAttribute("aria-valuenow", String(Math.round(v * 100)))
    try {
      localStorage.setItem(VOLUME_KEY, String(v))
    } catch (_) {}
  }

  const ajustarVolume = (delta) => {
    aplicarVolume((audio.volume || 0.7) + Number(delta || 0))
  }

  const tocarMusica = (musica, opts = {}) => {
    if (!musica || !musica.url) return
    const mesma = faixaAtual && faixaAtual.id === musica.id
    const fromTime = opts.fromTime
    const forcarInicio = opts.restart === true

    if (mesma && !forcarInicio && audio.readyState > 0 && !audio.ended) {
      faixaAtual = {
        id: musica.id,
        titulo: musica.titulo,
        genero: musica.genero,
        url: musica.url,
      }
      continuarMusica()
      return
    }

    try {
      audio.pause()
    } catch (_) {}

    faixaAtual = {
      id: musica.id,
      titulo: musica.titulo,
      genero: musica.genero,
      url: musica.url,
    }

    const alvo = forcarInicio ? 0 : fromTime || 0
    const onReady = () => {
      try {
        audio.currentTime = alvo > 0 && Number.isFinite(audio.duration) && alvo < audio.duration
          ? alvo
          : 0
      } catch (_) {}
      const p = audio.play()
      if (p && typeof p.then === "function") {
        p.then(() => {
          atualizarNowPlaying("a tocar")
          guardarEstado()
          atualizarPosicao()
        }).catch(() => {
          atualizarNowPlaying("clica ▶ no leitor")
          guardarEstado()
        })
      }
      audio.removeEventListener("loadedmetadata", onReady)
    }

    atualizarNowPlaying("a carregar…")
    audio.addEventListener("loadedmetadata", onReady)
    audio.src = musica.url
    audio.load()
  }

  const restaurarEstado = (estado, autoPlay) => {
    if (!estado || !estado.url) return
    faixaAtual = {
      id: estado.id,
      titulo: estado.titulo,
      genero: estado.genero,
      url: estado.url,
    }
    const onReady = () => {
      try {
        if (estado.currentTime > 0) audio.currentTime = estado.currentTime
      } catch (_) {}
      atualizarPosicao()
      if (autoPlay) {
        continuarMusica()
      } else {
        atualizarNowPlaying(estado.paused === false ? "pronta" : "em pausa")
      }
      audio.removeEventListener("loadedmetadata", onReady)
    }
    audio.addEventListener("loadedmetadata", onReady)
    audio.src = estado.url
    audio.load()
  }

  const playerDasAcoes = (data) => {
    if (data.player) return data.player
    const acoes = data.acoes || []
    for (const a of acoes) {
      if (a && a.ok && a.acao === "tocar" && a.musica) return a.musica
    }
    return null
  }

  const controloDasAcoes = (data) => {
    if (
      data.player_control === "pausar" ||
      data.player_control === "continuar" ||
      data.player_control === "reiniciar"
    ) {
      return data.player_control
    }
    const acoes = data.acoes || []
    for (const a of acoes) {
      if (
        a &&
        a.ok &&
        (a.acao === "pausar" || a.acao === "continuar" || a.acao === "reiniciar")
      ) {
        return a.acao
      }
    }
    return null
  }

  const mensagemPedeControloMusica = (msg) => {
    const t = (msg || "").toLowerCase()
    return /(?:\bpausa\b|\bpausar\b|\bpause\b|\bcontinua\b|\bcontinuar\b|\bretoma\b|\bretomar\b|\btoca\b|\btocar\b|\btroca\b|\btrocar\b|\bmuda\b|\bmudar\b|\bpassa(?:r)?\s+para\b|\bquero\s+ouvir\b|\bouvir\b|\bouve\b|\bplay\b|\breproduz\b|\bpara a m[uú]sica\b|\bpara de tocar\b|\bmete m[uú]sica\b|\bcome[cç]o\b|\bin[ií]cio\b|\breinicia|\brecome[cç]a|\bvolume\b|\bmais baixo\b|\bmais alto\b|\babaixa|\baumenta|\bmudo\b)/i.test(
      t
    )
  }

  const aplicarPlayerDaResposta = (data, mensagemUtilizador) => {
    const faixa = playerDasAcoes(data)
    const ctrl = controloDasAcoes(data)
    const pedeControlo = mensagemPedeControloMusica(mensagemUtilizador)
    const temVolumeResp =
      typeof data.volume_nivel === "number" || typeof data.volume_delta === "number"
    const acoes = data.acoes || []
    const temVolumeAcao = acoes.some(
      (a) => a && a.ok && (a.acao === "volume" || a.acao === "volume_delta")
    )

    // Se o servidor pediu tocar uma faixa, aplicar SEMPRE (mesmo com "troca para jazz").
    // Controlo/volume só se a mensagem ou a resposta o pedirem — evita parar música no "olá".
    if (!faixa && !ctrl && !temVolumeResp && !temVolumeAcao && !pedeControlo) {
      return
    }

    if (typeof data.volume_nivel === "number") {
      aplicarVolume(data.volume_nivel)
    } else if (typeof data.volume_delta === "number") {
      ajustarVolume(data.volume_delta)
    } else {
      for (const a of acoes) {
        if (!a || !a.ok) continue
        if (a.acao === "volume" && typeof a.nivel === "number") {
          aplicarVolume(a.nivel)
          break
        }
        if (a.acao === "volume_delta" && typeof a.delta === "number") {
          ajustarVolume(a.delta)
          break
        }
      }
    }

    if (ctrl === "reiniciar") {
      reiniciarMusica()
      return
    }
    if (ctrl === "pausar") {
      pausarMusica()
      return
    }
    if (ctrl === "continuar") {
      continuarMusica()
      return
    }

    if (!faixa) return

    if (faixaAtual && faixaAtual.id === faixa.id && !audio.paused && !audio.ended) {
      return
    }

    if (faixaAtual && faixaAtual.id === faixa.id && audio.paused && !audio.ended) {
      continuarMusica()
      return
    }

    tocarMusica(faixa, { restart: true })
  }

  const renderLembretes = (lembretes) => {
    lista.innerHTML = ""
    const ativos = lembretes.filter((l) => l.estado !== "confirmado")
    listaVazia.hidden = ativos.length > 0
    for (const item of ativos) {
      const li = document.createElement("li")
      li.className = "side-item"
      const strong = document.createElement("strong")
      strong.textContent = item.titulo
      const small = document.createElement("small")
      small.textContent = `${item.hora} · ${item.tipo} · ${item.estado}`
      const acoes = document.createElement("div")
      acoes.className = "side-actions"
      const ok = document.createElement("button")
      ok.type = "button"
      ok.className = "btn-mini primary"
      ok.textContent = "Já fiz"
      ok.setAttribute("aria-label", `Confirmar lembrete ${item.titulo}`)
      ok.addEventListener("click", () => handleConfirmar(item.id))
      const adiar = document.createElement("button")
      adiar.type = "button"
      adiar.className = "btn-mini"
      adiar.textContent = "Adiar"
      adiar.setAttribute("aria-label", `Adiar lembrete ${item.titulo}`)
      adiar.addEventListener("click", () => handleAdiarLembrete(item.id))
      acoes.append(ok, adiar)
      li.append(strong, small, acoes)
      lista.append(li)
    }
  }

  const renderMusicas = (data) => {
    const generos = data.generos || []
    const musicas = data.musicas || []
    generosEl.innerHTML = ""
    const todos = document.createElement("button")
    todos.type = "button"
    todos.className = "chip" + (generoAtivo ? "" : " active")
    todos.textContent = "Todos"
    todos.setAttribute("aria-pressed", generoAtivo ? "false" : "true")
    todos.addEventListener("click", () => {
      generoAtivo = null
      carregarMusicas()
    })
    generosEl.append(todos)
    for (const g of generos) {
      const chip = document.createElement("button")
      chip.type = "button"
      chip.className = "chip" + (generoAtivo === g.genero ? " active" : "")
      chip.textContent = `${g.nome || g.genero} (${g.quantidade})`
      chip.setAttribute("aria-pressed", generoAtivo === g.genero ? "true" : "false")
      chip.addEventListener("click", () => {
        generoAtivo = g.genero
        carregarMusicas()
      })
      generosEl.append(chip)
    }

    musicasEl.innerHTML = ""
    musicaVazia.hidden = musicas.length > 0
    for (const m of musicas) {
      const li = document.createElement("li")
      li.className = "side-item"
      const strong = document.createElement("strong")
      strong.textContent = m.titulo
      const small = document.createElement("small")
      small.textContent = m.genero
      const btn = document.createElement("button")
      btn.type = "button"
      btn.className = "btn-mini primary"
      btn.textContent = "Tocar"
      btn.setAttribute("aria-label", `Tocar ${m.titulo}`)
      btn.style.marginTop = "0.45rem"
      btn.addEventListener("click", () => {
        desbloquearAudio()
        tocarMusica(m)
      })
      li.append(strong, small, btn)
      musicasEl.append(li)
    }
  }

  const carregarLista = async () => {
    const data = await handleApi("/api/lembretes")
    renderLembretes(data.lembretes || [])
  }

  const carregarMusicas = async () => {
    const q = generoAtivo ? `?genero=${encodeURIComponent(generoAtivo)}` : ""
    const data = await handleApi(`/api/musica${q}`)
    renderMusicas(data)
  }

  const carregarPerfil = async () => {
    try {
      const data = await handleApi("/api/perfil")
      atualizarPerfilLinha(data.perfil || {})
    } catch (_) {}
  }

  const carregarHistorico = async () => {
    try {
      const data = await handleApi("/api/conversas?limite=40")
      const msgs = data.mensagens || []
      chatLog.innerHTML = ""
      historico.length = 0
      if (!msgs.length) {
        addBubble(
          "assistant",
          "Olá. Podes dizer: “Lembra-me de beber água às 16:30”, “Conta-me uma história” ou “Que músicas tens?”."
        )
        return
      }
      for (const m of msgs) {
        if (m.role !== "user" && m.role !== "assistant") continue
        addBubble(m.role, m.conteudo)
        historico.push({ role: m.role, content: m.conteudo })
      }
    } catch (_) {
      addBubble(
        "assistant",
        "Olá. Podes dizer: “Lembra-me de beber água às 16:30” ou “Que músicas tens?”."
      )
    }
  }

  const atualizarEstadoLlm = async () => {
    try {
      const st = await handleApi("/api/llm")
      if (st.ok && st.modelo_disponivel) {
        llmEstado.textContent = `LLM pronta · ${st.modelo}`
        llmEstado.className = "llm-estado ok"
      } else {
        llmEstado.textContent = "LLM indisponível — lembretes e música OK"
        llmEstado.className = "llm-estado bad"
      }
    } catch (_) {
      llmEstado.textContent = "LLM indisponível — lembretes e música OK"
      llmEstado.className = "llm-estado bad"
    }
  }

  const tocarAvisoBrowser = () => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)()
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      osc.frequency.value = 880
      gain.gain.value = 0.08
      osc.connect(gain)
      gain.connect(ctx.destination)
      osc.start()
      setTimeout(() => {
        osc.stop()
        ctx.close()
      }, 350)
    } catch (_) {}
  }

  const pedirTtsServidor = (texto) => {
    handleApi("/api/voz/falar", {
      method: "POST",
      body: JSON.stringify({ texto }),
    }).catch(() => {})
  }

  const mostrarOverlay = (item) => {
    alertaAtual = item
    setFace("alerting")
    alertaTitulo.textContent = item.titulo
    alertaFrase.textContent = "A preparar o aviso…"
    alertaMeta.textContent = `Tipo: ${item.tipo} · Hora: ${item.hora}`
    overlay.hidden = false
    tocarAvisoBrowser()
    pedirTtsServidor(`É a hora: ${item.titulo}`)
    handleApi(`/api/lembretes/${item.id}/frase`, { method: "POST", body: "{}" })
      .then((data) => {
        if (alertaAtual && alertaAtual.id === item.id) {
          const frase = data.frase || `É a hora: ${item.titulo}`
          alertaFrase.textContent = frase
        }
      })
      .catch(() => {
        if (alertaAtual && alertaAtual.id === item.id) {
          alertaFrase.textContent = `É a hora: ${item.titulo}`
        }
      })
  }

  const handleConfirmar = async (id) => {
    await handleApi(`/api/lembretes/${id}/ok`, { method: "POST", body: "{}" })
    jaAlertados.delete(id)
    if (alertaAtual && alertaAtual.id === id) {
      overlay.hidden = true
      alertaAtual = null
      setFace("listening")
    }
    await carregarLista()
  }

  const handleAdiarLembrete = async (id) => {
    await handleApi(`/api/lembretes/${id}/adiar`, {
      method: "POST",
      body: JSON.stringify({ minutos: 10 }),
    })
    jaAlertados.delete(id)
    if (alertaAtual && alertaAtual.id === id) {
      overlay.hidden = true
      alertaAtual = null
      setFace("listening")
    }
    await carregarLista()
  }

  const verificarDevidos = async () => {
    const data = await handleApi("/api/devidos")
    const devidos = data.devidos || []
    for (const item of devidos) {
      if (jaAlertados.has(item.id)) continue
      jaAlertados.add(item.id)
      await handleApi(`/api/lembretes/${item.id}/disparar`, { method: "POST", body: "{}" })
      if (!alertaAtual) mostrarOverlay(item)
      break
    }
    if (!alertaAtual && !devidos.length) {
      if (ricFace.dataset.state === "alerting") setFace("listening")
    }
  }

  const autoResize = () => {
    chatInput.style.height = "auto"
    chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + "px"
  }

  const limparTimersStt = () => {
    if (sttSilenceTimer) {
      clearTimeout(sttSilenceTimer)
      sttSilenceTimer = null
    }
    if (sttMaxTimer) {
      clearTimeout(sttMaxTimer)
      sttMaxTimer = null
    }
  }

  const resetSttUi = () => {
    limparTimersStt()
    aOuvir = false
    btnFalar.classList.remove("listening-stt")
    btnFalar.textContent = "Falar"
    btnFalar.setAttribute("aria-pressed", "false")
  }

  const palavrasRic = [
    "lembra",
    "lembrar",
    "lembrete",
    "avisa",
    "daqui",
    "minuto",
    "minutos",
    "hora",
    "horas",
    "água",
    "agua",
    "pausa",
    "pausar",
    "continua",
    "continuar",
    "toca",
    "tocar",
    "música",
    "musica",
    "volume",
    "jazz",
    "metal",
    "história",
    "historia",
  ]

  const pontuarTranscricao = (texto, confidence) => {
    const low = (texto || "").toLowerCase()
    let pontos = typeof confidence === "number" ? confidence : 0
    for (const palavra of palavrasRic) {
      if (low.includes(palavra)) pontos += 0.35
    }
    if (/\b\d{1,2}:\d{2}\b/.test(low) || /\b\d+\s*min/.test(low)) pontos += 0.4
    return pontos
  }

  const melhorAlternativa = (result) => {
    let melhor = ""
    let melhorPontos = -1
    const n = result.length || 0
    for (let j = 0; j < n; j += 1) {
      const alt = result[j]
      const texto = (alt && alt.transcript) || ""
      if (!texto) continue
      const pontos = pontuarTranscricao(texto, alt.confidence)
      if (pontos > melhorPontos) {
        melhorPontos = pontos
        melhor = texto
      }
    }
    return melhor
  }

  const corrigirStt = (texto) => {
    let t = (texto || "").trim()
    if (!t) return ""

    // Remove eco óbvio da mesma frase seguida
    t = t.replace(/\b(.{6,60}?)\s+\1\b/gi, "$1")

    const pares = [
      [/\bdaki\b/gi, "daqui"],
      [/\bda qui\b/gi, "daqui"],
      [/\bdaqui a daqui\b/gi, "daqui"],
      [/\bminudo\b/gi, "minuto"],
      [/\bminudos\b/gi, "minutos"],
      [/\bmimuto\b/gi, "minuto"],
      [/\bmimutos\b/gi, "minutos"],
      [/\bme lembra de me lembra de\b/gi, "me lembra de"],
      [/\blembrame\b/gi, "lembra-me"],
      [/\blembre me\b/gi, "lembra-me"],
      [/\blemvra[- ]?me\b/gi, "lembra-me"],
      [/\bavisame\b/gi, "avisa-me"],
      [/\bavisa me\b/gi, "avisa-me"],
      [/\bpousa(?:r)?\b/gi, "pausar"],
      [/\bpause a música\b/gi, "pausa a música"],
      [/\btocha\b/gi, "toca"],
      [/\btoca a toca\b/gi, "toca"],
      [/\bagua\b/gi, "água"],
    ]

    for (const [pat, rep] of pares) {
      t = t.replace(pat, rep)
    }

    t = t.replace(/\s+/g, " ").trim()
    return t
  }

  const idiomaStt = () => {
    const escolhido = (sttLang && sttLang.value) || "pt-BR"
    return escolhido === "pt-PT" ? "pt-PT" : "pt-BR"
  }

  const remarcarSilencioStt = () => {
    if (sttSilenceTimer) clearTimeout(sttSilenceTimer)
    sttSilenceTimer = setTimeout(() => {
      if (!aOuvir || !recognition) return
      sttEnviarAoFim = true
      try {
        recognition.stop()
      } catch (_) {
        resetSttUi()
      }
    }, STT_SILENCE_MS)
  }

  const finalizarSttEEnviar = () => {
    const mensagem = corrigirStt(sttBuffer || chatInput.value)
    sttBuffer = ""
    if (!mensagem || chatInput.disabled || btnEnviar.disabled) {
      if (!mensagem) mostrarChatMsg("Não ouvi nada. Fala um pouco mais perto do microfone.")
      return
    }
    chatInput.value = mensagem
    autoResize()
    mostrarChatMsg("")
    formChat.requestSubmit()
  }

  const setupStt = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) {
      sttNota.hidden = false
      sttNota.textContent =
        "Ditado não disponível neste browser. Continua a escrever — o texto funciona sempre."
      btnFalar.disabled = true
      btnFalar.title = "STT não suportado neste browser"
      if (sttLang) sttLang.disabled = true
      return
    }

    try {
      const salvo = localStorage.getItem(STT_LANG_KEY)
      if (sttLang && (salvo === "pt-BR" || salvo === "pt-PT")) sttLang.value = salvo
    } catch (_) {
      /* ignore */
    }

    recognition = new SR()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.maxAlternatives = 3
    recognition.lang = idiomaStt()

    if (sttLang) {
      sttLang.addEventListener("change", () => {
        recognition.lang = idiomaStt()
        try {
          localStorage.setItem(STT_LANG_KEY, recognition.lang)
        } catch (_) {
          /* ignore */
        }
        mostrarChatMsg(
          recognition.lang === "pt-BR"
            ? "Ditado em PT-BR (geralmente mais preciso no Chrome)."
            : "Ditado em PT-PT."
        )
      })
    }

    sttNota.hidden = false
    sttNota.textContent =
      "Dica: fala devagar e perto do microfone. Se falhar, experimenta Ditado PT-BR."

    recognition.onresult = (ev) => {
      let interim = ""
      for (let i = ev.resultIndex; i < ev.results.length; i += 1) {
        const piece = melhorAlternativa(ev.results[i])
        if (!piece) continue
        if (ev.results[i].isFinal) {
          sttBuffer = corrigirStt(`${sttBuffer} ${piece}`)
        } else {
          interim += piece
        }
      }
      const mostrado = corrigirStt(`${sttBuffer}${interim ? ` ${interim}` : ""}`)
      chatInput.value = mostrado
      autoResize()
      remarcarSilencioStt()
    }

    recognition.onerror = (ev) => {
      const motivo = (ev && ev.error) || ""
      if (motivo === "aborted") return
      sttEnviarAoFim = false
      sttBuffer = ""
      resetSttUi()
      if (!alertaAtual) setFace("listening")
      if (motivo === "no-speech") {
        mostrarChatMsg("Não ouvi nada. Fala mais perto ou escreve.")
        return
      }
      if (motivo === "audio-capture" || motivo === "not-allowed") {
        mostrarChatMsg("Microfone bloqueado. Permite o microfone neste site e tenta outra vez.")
        return
      }
      mostrarChatMsg("Não consegui ouvir bem. Tenta PT-BR ou escreve.")
    }

    recognition.onend = () => {
      const deveEnviar = sttEnviarAoFim
      sttEnviarAoFim = false
      resetSttUi()
      if (!alertaAtual) setFace("listening")
      if (deveEnviar) finalizarSttEEnviar()
    }
  }

  const handleFalar = () => {
    if (!recognition) {
      mostrarChatMsg("Ditado indisponível neste browser.")
      return
    }
    if (aOuvir) {
      sttEnviarAoFim = true
      limparTimersStt()
      try {
        recognition.stop()
      } catch (_) {
        resetSttUi()
      }
      return
    }
    if (chatInput.disabled || btnEnviar.disabled) {
      mostrarChatMsg("Espera a resposta anterior terminar.")
      return
    }
    try {
      sttBuffer = ""
      sttEnviarAoFim = true
      chatInput.value = ""
      autoResize()
      recognition.lang = idiomaStt()
      aOuvir = true
      btnFalar.classList.add("listening-stt")
      btnFalar.textContent = "A ouvir… (clica para enviar)"
      btnFalar.setAttribute("aria-pressed", "true")
      setFace("listening")
      mostrarChatMsg("Fala com calma… paro ~1,5 s depois do silêncio e envio.")
      recognition.start()
      sttMaxTimer = setTimeout(() => {
        if (!aOuvir || !recognition) return
        sttEnviarAoFim = true
        try {
          recognition.stop()
        } catch (_) {
          resetSttUi()
        }
      }, STT_MAX_MS)
    } catch (_) {
      sttEnviarAoFim = false
      sttBuffer = ""
      resetSttUi()
      mostrarChatMsg("Não foi possível iniciar o microfone.")
    }
  }

  formChat.addEventListener("submit", async (ev) => {
    ev.preventDefault()
    const mensagem = chatInput.value.trim()
    if (!mensagem) return

    addBubble("user", mensagem)
    historico.push({ role: "user", content: mensagem })
    chatInput.value = ""
    autoResize()
    if (mensagemPedeControloMusica(mensagem)) {
      desbloquearAudio()
    }
    btnEnviar.disabled = true
    chatInput.disabled = true
    setFace("thinking")
    mostrarChatMsg("A pensar…")
    const thinking = addBubble("assistant", "A pensar…", "thinking")

    try {
      const data = await handleApi("/api/chat", {
        method: "POST",
        body: JSON.stringify({
          mensagem,
          historico: historico.slice(0, -1).slice(-10),
        }),
      })
      thinking.remove()
      const resposta = data.resposta || "Pronto."
      addBubble("assistant", resposta)
      historico.push({ role: "assistant", content: resposta })
      aplicarPlayerDaResposta(data, mensagem)
      if (data.perfil) atualizarPerfilLinha(data.perfil)
      mostrarChatMsg("")
      await Promise.all([carregarLista(), carregarMusicas(), atualizarEstadoLlm()])
    } catch (err) {
      thinking.remove()
      const erro = err.message || "Não consegui falar com a LLM."
      addBubble("assistant", erro)
      mostrarChatMsg(erro + " — lembretes e música continuam disponíveis.")
      await atualizarEstadoLlm()
    } finally {
      btnEnviar.disabled = false
      chatInput.disabled = false
      if (!alertaAtual) setFace("listening")
      chatInput.focus()
    }
  })

  chatInput.addEventListener("input", autoResize)
  chatInput.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && !ev.shiftKey) {
      ev.preventDefault()
      formChat.requestSubmit()
    }
  })

  btnOk.addEventListener("click", () => {
    if (alertaAtual) handleConfirmar(alertaAtual.id)
  })
  btnAdiar.addEventListener("click", () => {
    if (alertaAtual) handleAdiarLembrete(alertaAtual.id)
  })
  btnFalar.addEventListener("click", handleFalar)

  btnPausar.addEventListener("click", () => {
    desbloquearAudio()
    pausarMusica()
  })
  btnContinuar.addEventListener("click", () => {
    desbloquearAudio()
    continuarMusica()
  })
  btnReiniciar.addEventListener("click", () => {
    desbloquearAudio()
    reiniciarMusica()
  })
  volumeInput.addEventListener("input", () => {
    aplicarVolume(Number(volumeInput.value) / 100)
  })

  audio.addEventListener("timeupdate", () => {
    atualizarPosicao()
    if (!audio.paused) guardarEstado()
  })
  audio.addEventListener("pause", guardarEstado)
  audio.addEventListener("play", () => {
    atualizarNowPlaying("a tocar")
    guardarEstado()
  })
  audio.addEventListener("ended", () => {
    atualizarNowPlaying("terminou")
    guardarEstado()
  })

  try {
    const volSalvo = localStorage.getItem(VOLUME_KEY)
    aplicarVolume(volSalvo !== null ? Number(volSalvo) : 0.7)
  } catch (_) {
    aplicarVolume(0.7)
  }

  const salvo = lerEstado()
  if (salvo) restaurarEstado(salvo, false)

  setFace("listening")
  setupStt()
  atualizarRelogio()
  setInterval(atualizarRelogio, 1000)
  atualizarEstadoLlm()
  carregarHistorico().catch(() => {})
  carregarPerfil().catch(() => {})
  carregarLista().catch(() => {})
  carregarMusicas().catch(() => {})
  verificarDevidos().catch(() => {})
  setInterval(() => {
    carregarLista().catch(() => {})
    verificarDevidos().catch(() => {})
  }, 4000)
  setInterval(atualizarEstadoLlm, 20000)
})()
