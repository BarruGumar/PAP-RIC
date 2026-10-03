(() => {
  const form = document.getElementById("form-agendar");
  const formMsg = document.getElementById("form-msg");
  const formChat = document.getElementById("form-chat");
  const chatInput = document.getElementById("chat-input");
  const chatLog = document.getElementById("chat-log");
  const chatMsg = document.getElementById("chat-msg");
  const btnEnviar = document.getElementById("btn-enviar");
  const llmEstado = document.getElementById("llm-estado");
  const lista = document.getElementById("lembretes");
  const listaVazia = document.getElementById("lista-vazia");
  const relogio = document.getElementById("relogio");
  const overlay = document.getElementById("overlay");
  const alertaTitulo = document.getElementById("alerta-titulo");
  const alertaFrase = document.getElementById("alerta-frase");
  const alertaMeta = document.getElementById("alerta-meta");
  const btnOk = document.getElementById("btn-ok");
  const btnAdiar = document.getElementById("btn-adiar");

  let alertaAtual = null;
  const jaAlertados = new Set();
  const historico = [];

  async function api(path, options = {}) {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.erro || "Pedido falhou.");
    }
    return data;
  }

  function mostrarMsg(texto) {
    formMsg.hidden = false;
    formMsg.textContent = texto;
  }

  function mostrarChatMsg(texto) {
    chatMsg.hidden = !texto;
    chatMsg.textContent = texto || "";
  }

  function atualizarRelogio() {
    const agora = new Date();
    relogio.textContent = agora.toLocaleTimeString("pt-PT", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }

  function addBubble(role, texto, extraClass = "") {
    const div = document.createElement("div");
    div.className = `bubble ${role}` + (extraClass ? ` ${extraClass}` : "");
    div.textContent = texto;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
    return div;
  }

  function etiquetaEstado(estado) {
    if (estado === "disparado" || estado === "adiado") return "warn";
    if (estado === "confirmado") return "ok";
    return "";
  }

  function renderLista(lembretes) {
    lista.innerHTML = "";
    const ativos = lembretes.filter((l) => l.estado !== "confirmado");
    const confirmados = lembretes.filter((l) => l.estado === "confirmado");
    const ordenados = [...ativos, ...confirmados];

    listaVazia.hidden = ordenados.length > 0;

    for (const item of ordenados) {
      const li = document.createElement("li");
      li.className = "item" + (item.estado === "disparado" ? " devido" : "");

      const top = document.createElement("div");
      top.className = "item-top";

      const info = document.createElement("div");
      const titulo = document.createElement("p");
      titulo.className = "item-titulo";
      titulo.textContent = item.titulo;
      const meta = document.createElement("p");
      meta.className = "item-meta";
      meta.textContent = `${item.hora} · ${item.tipo} · próximo: ${item.proximo_em.replace("T", " ")}`;
      info.append(titulo, meta);

      const badge = document.createElement("span");
      badge.className = "badge " + etiquetaEstado(item.estado);
      badge.textContent = item.estado;

      top.append(info, badge);
      li.append(top);

      if (item.estado !== "confirmado") {
        const acoes = document.createElement("div");
        acoes.className = "acoes";

        const ok = document.createElement("button");
        ok.type = "button";
        ok.className = "btn btn-primary";
        ok.textContent = "Já fiz";
        ok.addEventListener("click", () => confirmar(item.id));

        const adiar = document.createElement("button");
        adiar.type = "button";
        adiar.className = "btn btn-ghost";
        adiar.textContent = "Adiar 10 min";
        adiar.addEventListener("click", () => adiarLembrete(item.id));

        acoes.append(ok, adiar);
        li.append(acoes);
      }

      lista.append(li);
    }
  }

  async function carregarLista() {
    const data = await api("/api/lembretes");
    renderLista(data.lembretes || []);
  }

  async function atualizarEstadoLlm() {
    try {
      const st = await api("/api/llm");
      if (st.ok && st.modelo_disponivel) {
        llmEstado.textContent = `LLM local pronta (${st.modelo})`;
        llmEstado.className = "llm-estado ok";
      } else if (st.ok) {
        llmEstado.textContent = `Ollama ligado, mas falta o modelo ${st.modelo}`;
        llmEstado.className = "llm-estado bad";
      } else {
        llmEstado.textContent = "LLM local indisponível — podes agendar manualmente.";
        llmEstado.className = "llm-estado bad";
      }
    } catch (_) {
      llmEstado.textContent = "LLM local indisponível — podes agendar manualmente.";
      llmEstado.className = "llm-estado bad";
    }
  }

  function tocarAviso() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.value = 880;
      gain.gain.value = 0.08;
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      setTimeout(() => {
        osc.stop();
        ctx.close();
      }, 350);
    } catch (_) {
      /* silencioso */
    }
  }

  function pedirPermissaoNotificacoes() {
    if (!("Notification" in window)) return;
    if (Notification.permission === "default") {
      Notification.requestPermission().catch(() => {});
    }
  }

  function notificarBrowser(item, frase) {
    if (!("Notification" in window) || Notification.permission !== "granted") return;
    try {
      new Notification("RIC — lembrete", {
        body: frase || item.titulo,
        tag: "ric-" + item.id,
      });
    } catch (_) {
      /* overlay basta */
    }
  }

  function mostrarOverlay(item) {
    alertaAtual = item;
    alertaTitulo.textContent = item.titulo;
    alertaFrase.textContent = "A preparar o aviso…";
    alertaMeta.textContent = `Tipo: ${item.tipo} · Hora: ${item.hora}`;
    overlay.hidden = false;
    tocarAviso();
    notificarBrowser(item);

    api(`/api/lembretes/${item.id}/frase`, { method: "POST", body: "{}" })
      .then((data) => {
        if (!alertaAtual || alertaAtual.id !== item.id) return;
        alertaFrase.textContent = data.frase || item.titulo;
        notificarBrowser(item, data.frase);
      })
      .catch(() => {
        if (!alertaAtual || alertaAtual.id !== item.id) return;
        alertaFrase.textContent = `É a hora: ${item.titulo}`;
      });
  }

  function esconderOverlay() {
    overlay.hidden = true;
    alertaAtual = null;
  }

  async function confirmar(id) {
    await api(`/api/lembretes/${id}/ok`, { method: "POST", body: "{}" });
    jaAlertados.delete(id);
    if (alertaAtual && alertaAtual.id === id) esconderOverlay();
    await carregarLista();
  }

  async function adiarLembrete(id) {
    await api(`/api/lembretes/${id}/adiar`, {
      method: "POST",
      body: JSON.stringify({ minutos: 10 }),
    });
    jaAlertados.delete(id);
    if (alertaAtual && alertaAtual.id === id) esconderOverlay();
    await carregarLista();
  }

  async function verificarDevidos() {
    const data = await api("/api/devidos");
    const devidos = data.devidos || [];

    for (const item of devidos) {
      if (jaAlertados.has(item.id)) continue;
      jaAlertados.add(item.id);
      await api(`/api/lembretes/${item.id}/disparar`, { method: "POST", body: "{}" });
      if (!alertaAtual) {
        mostrarOverlay(item);
      }
      break;
    }

    const ids = new Set(devidos.map((d) => d.id));
    for (const id of [...jaAlertados]) {
      if (!ids.has(id) && (!alertaAtual || alertaAtual.id !== id)) {
        jaAlertados.delete(id);
      }
    }
  }

  formChat.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const mensagem = chatInput.value.trim();
    if (!mensagem) return;

    addBubble("user", mensagem);
    historico.push({ role: "user", content: mensagem });
    chatInput.value = "";
    btnEnviar.disabled = true;
    chatInput.disabled = true;
    mostrarChatMsg("A pensar…");
    const thinking = addBubble("assistant", "A pensar…", "thinking");

    try {
      const data = await api("/api/chat", {
        method: "POST",
        body: JSON.stringify({
          mensagem,
          historico: historico.slice(0, -1),
        }),
      });
      thinking.remove();
      const resposta = data.resposta || "Pronto.";
      addBubble("assistant", resposta);
      historico.push({ role: "assistant", content: resposta });
      mostrarChatMsg("");
      await carregarLista();
      await atualizarEstadoLlm();
    } catch (err) {
      thinking.remove();
      const erro = err.message || "Não consegui falar com a LLM.";
      addBubble("assistant", erro);
      mostrarChatMsg(erro);
    } finally {
      btnEnviar.disabled = false;
      chatInput.disabled = false;
      chatInput.focus();
    }
  });

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const titulo = document.getElementById("titulo").value.trim();
    const hora = document.getElementById("hora").value;
    const tipo = document.getElementById("tipo").value;
    try {
      await api("/api/lembretes", {
        method: "POST",
        body: JSON.stringify({ titulo, hora, tipo }),
      });
      form.reset();
      mostrarMsg("Lembrete agendado.");
      await carregarLista();
    } catch (err) {
      mostrarMsg(err.message || "Não foi possível agendar.");
    }
  });

  btnOk.addEventListener("click", () => {
    if (alertaAtual) confirmar(alertaAtual.id);
  });

  btnAdiar.addEventListener("click", () => {
    if (alertaAtual) adiarLembrete(alertaAtual.id);
  });

  pedirPermissaoNotificacoes();
  atualizarRelogio();
  setInterval(atualizarRelogio, 1000);

  atualizarEstadoLlm();
  carregarLista().catch((err) => mostrarMsg(err.message));
  verificarDevidos().catch(() => {});
  setInterval(() => {
    carregarLista().catch(() => {});
    verificarDevidos().catch(() => {});
  }, 4000);
  setInterval(atualizarEstadoLlm, 20000);
})();
