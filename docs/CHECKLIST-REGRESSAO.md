# Checklist de regressão — RIC (MVP)

Testes manuais curtos antes de uma demo. Tempo estimado: 10–15 minutos.

## Preparação

```powershell
cd C:\Users\pedro\OneDrive\Documentos\PAP
# Parar UI antiga (Ctrl+C) e reiniciar:
py -m ric ui
```

- Browser: `http://127.0.0.1:8787/`
- Ollama opcional: `ollama serve` + modelo `qwen2.5:3b`
- Sem Ollama: lembretes, lista, player e overlay devem continuar a funcionar

---

## 1. Lembretes

| # | Passo | Esperado |
|---|---|---|
| 1.1 | Chat: `Lembra-me de beber água às HH:MM` (1–2 min à frente) | Lembrete na lista lateral |
| 1.1b | Chat relativo: `Me lembra de beber água daqui 1 minuto` | Agenda sem pedir HH:MM; dispara ~1 min depois |
| 1.2 | Formulário/lista: confirmar com **Já fiz** noutro lembrete existente | Estado `confirmado`, some dos ativos |
| 1.3 | À hora: overlay “É a hora” + som (browser e/ou terminal watchdog) | Aviso visível; frase ou fallback |
| 1.4 | No overlay: **Já fiz** | Overlay fecha; lembrete confirmado |
| 1.5 | Novo lembrete → à hora → **Adiar 10 min** | Overlay fecha; volta a disparar depois |
| 1.6 | Com UI aberta, ver no terminal `[RIC watchdog]` quando chega a hora | Rede de segurança do servidor |

## 2. Modo sem Ollama

| # | Passo | Esperado |
|---|---|---|
| 2.1 | Parar Ollama (ou ignorá-lo) e abrir UI | Estado “LLM indisponível”; UI carrega |
| 2.2 | Usar lista de lembretes + player | Funcionam sem chat |
| 2.3 | Enviar mensagem no chat | Erro amigável; música/lembretes intactos |

## 3. Música (offline)

Frases canónicas (chat ou botões):

| Pedido | Ação |
|---|---|
| `Toca metal` / `Toca Caravan` | Começa a tocar |
| `Pausa` / `Pausar` | Pausa, guarda posição |
| `Continua` / `Retoma` | Retoma do mesmo ponto |
| `Do começo` / `Reinicia` | Volta ao tempo 0 e toca |
| `Volume mais baixo` / `mais alto` | Ajusta volume |
| `Volume 40` / `mudo` | Volume absoluto / 0 |

| # | Passo | Esperado |
|---|---|---|
| 3.1 | Tocar uma faixa | Player mostra título + tempo |
| 3.2 | Pausar → Continuar | Retoma sem reiniciar |
| 3.3 | Do começo | Tempo ~00:00 |
| 3.4 | Volume slider + pedido por chat | Volume muda |
| 3.5 | Com música a tocar, enviar `Olá` | Música **não** para |

## 4. Memória / perfil

| # | Passo | Esperado |
|---|---|---|
| 4.1 | `O meu nome é Pedro` (com Ollama) | RIC confirma; perfil guardado |
| 4.2 | Fechar e reabrir UI (`Ctrl+C` + `py -m ric ui`) | Chat e nome/preferências persistem |
| 4.3 | `Conta-me uma história curta` | História breve em pt-PT |

## 5. Voz

| # | Passo | Esperado |
|---|---|---|
| 5.1 | Disparar lembrete | Beep; TTS se Windows SAPI disponível |
| 5.2 | Botão **Falar** (se browser suportar) | Ditado para a caixa de texto |
| 5.3 | Browser sem STT | Mensagem clara; texto continua a funcionar |

## Critério “demo OK”

Sem internet (exceto Ollama local já no PC):

1. Pedir lembrete daqui a 1–2 min → alerta  
2. Confirmar / adiar  
3. Pedir música → “olá” não para a música  
4. Pausa / continua / do começo / volume  
5. Reabrir UI → lembra nome/chat e posição do player  
