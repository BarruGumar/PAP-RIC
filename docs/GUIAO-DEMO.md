# Guião de demo PAP — RIC (5–8 minutos)

Objetivo: mostrar companheiro local, privacidade, lembretes fiáveis e música offline.

## Antes de começar (2 min de preparação)

```powershell
cd C:\Users\pedro\OneDrive\Documentos\PAP
ollama serve
# noutro terminal:
py -m ric ui
```

- Confirmar modelo: `qwen2.5:3b`
- Ter pelo menos 1 música em `ric\musica\`
- Browser em `http://127.0.0.1:8787/`
- Opcional: pedir um lembrete 2 minutos à frente *antes* da apresentação

---

## Minuto a minuto

### 0:00–0:45 — O que é o RIC

- Mostrar a marca **RIC** e o rosto simples.
- Frase: *companheiro local de apoio — lembretes, conversa e música, com privacidade.*
- Salientar: **sem cloud por defeito**; dados em SQLite no PC.

### 0:45–2:00 — Lembrete e memória por chat

1. `Chamo-me Pedro` (mostra memória/perfil)
2. `Lembra-me de beber água às HH:MM` (hora daqui a ~1–2 min)
3. Mostrar o lembrete na lista lateral
4. Explicar: a **verdade** está no backend SQLite; a LLM só pediu a ação

### 2:00–3:30 — Alerta à hora

- Quando disparar: overlay + som (+ TTS se Windows SAPI)
- Mostrar **Já fiz** e (se tempo) **Adiar**
- Mencionar o **watchdog** no servidor: mesmo se o JS falhar, o terminal avisa

### 3:30–5:00 — Companhia + música offline

1. `Conta-me uma história curta`
2. `Toca metal` (ou outra faixa existente)
3. Enviar `Olá` → música **não** para
4. `Pausa` → `Continua` → `Do começo` → `Volume mais baixo`

### 5:00–6:30 — Privacidade e limites

- Dados locais: `ric/data/ric.db` + pastas de música
- Sem diagnóstico médico nem prescrição
- Se a LLM cair: lista/player/overlay continuam

### 6:30–8:00 — Fecho (se houver tempo)

- Fechar e reabrir a UI → nome/preferência e player lembrados
- Botão **Falar** (STT) se o browser permitir
- Melhorias futuras: hardware definitivo, locomoção só como extra

---

## Plano B (se algo falhar)

| Problema | Alternativa |
|---|---|
| Ollama lento/parado | Agendar pelo formulário lateral; explicar “modo só lembretes” |
| Música não toca sozinha | Clicar no player (gesto do browser) |
| Alerta ainda não disparou | Mostrar `py -m ric list` + watchdog no terminal |
| STT indisponível | Continuar só com teclado |

## Checklist pós-ensaio

Ver `docs/CHECKLIST-REGRESSAO.md`.
