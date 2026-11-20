# RIC — Robô Interativo Companheiro

Companheiro digital local (voz + lembretes) para apoio a rotinas, com privacidade e hardware reaproveitado.

**PAP** — Prova de Aptidão Profissional  
**Curso:** Técnico/a de Informática — Sistemas (3-TIS) · ETEO  
**Aluno:** Pedro Albuquerque  
**Orientador:** Gil Ribeiro

> Protótipo escolar. Não é produto médico. Não diagnostica nem prescrita medicação.

---

## O problema

Muitas pessoas (em especial idosos) precisam de apoio a rotinas — medicamentos, consultas, hábitos — mas têm pouca literacia digital. Interfaces só com menus e texto falham.

O RIC prioriza **falar e ouvir**, funciona **offline** nas funções essenciais, e corre num PC reaproveitado (Intel NUC) em vez de depender da nuvem.

## Ideia em uma frase

Um companheiro parado (corpo tipo gato + ecrã como “rosto”) que lembra, conversa em português de Portugal e guarda o mínimo de preferências **na máquina**, sem Internet obrigatória.

---

## Demo para o júri (função única)

Se só puder mostrar **uma** coisa: **lembretes offline**.

1. Criar um lembrete  
2. À hora certa: alerta com som + ecrã  
3. Confirmar **Já fiz** ou **Adiar 10 min**  

Isto **não depende** da LLM nem da Internet.

*(Screenshot / GIF / vídeo: a acrescentar quando a demo estiver estável no NUC.)*

---

## O que já faz (MVP)

| Área | Estado |
|---|---|
| Lembretes offline | Criar, disparar, confirmar, adiar (SQLite) |
| UI kiosk | Rosto EVE + botões; `http://127.0.0.1:8787` |
| TTS | Piper (pt_PT tugão medium) |
| STT | faster-whisper |
| Wake-word | openWakeWord (temporário `hey_jarvis`; alvo **«ei RIC»**) |
| Memória mínima | Preferências / nome em SQLite |
| LLM local (opcional) | Ollama `qwen2.5:3b` — conversa; o núcleo sobe sem Ollama |

## O que não faz (nesta PAP)

- Diagnosticar doenças ou aconselhar doses  
- Locomoção, rodas ou braços  
- Testes com utentes idosos reais (só simulação com o aluno / família / colegas; se no futuro houver idosos reais, consentimento informado por escrito)  
- Cloud LLM no núcleo  
- Enviar dados sensíveis para a nuvem por defeito  

---

## Arquitetura (resumo)

```
Pessoa  ↔  Ecrã tactile kiosk (rosto SVG)
                 ↕  http://127.0.0.1:8787  (REST + WebSocket)
        Um processo Python (RIC)
        - lembretes + SQLite   ← fiáveis, sem LLM
        - voz (wake + Whisper + Piper)
        - LLM Ollama (opcional)
```

**Regra de ouro:** lembretes e o núcleo offline **não dependem** da LLM nem da Internet.

Detalhe: [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md)

---

## Hardware

| Papel | Escolha |
|---|---|
| Cérebro | Intel **NUC5i3RYH** (Core i3-5010U), expansão a **16 GB** DDR3L |
| Reserva | NUC DN2820FYK (Celeron) — só emergência; não sustenta LLM + STT juntos |
| UI | Ecrã **tactile** no mesmo NUC (HDMI/DP + USB) |
| Áudio | Microfone e colunas (emprestar ou comprar) |
| SO alvo | **Linux Mint XFCE** (`ric.service` + kiosk) |
| Corpo | Estrutura **parada** tipo gato (cabeça = ecrã) |

Inventário e comparação: [`docs/INVENTARIO-HARDWARE.md`](docs/INVENTARIO-HARDWARE.md) · Orçamento: [`docs/ORCAMENTO.md`](docs/ORCAMENTO.md)

Windows pode servir para desenvolver; a máquina da demo é Linux Mint no NUC.

---

## Stack

| Peça | Uso |
|---|---|
| Python 3 | App única (API, UI estática, voz, lembretes) |
| SQLite | Lembretes, preferências, histórico curto |
| Piper | TTS offline PT-PT |
| faster-whisper | STT local |
| openWakeWord + sounddevice | Wake-word contínuo |
| Ollama + Qwen2.5 3B | Conversa / tools (opcional) |
| HTML/CSS/JS | UI kiosk (rosto + botões) |

---

## Estrutura do repositório

```
ric/                 aplicação nova (código da demo)
docs/                arquitetura, metas, hardware, planeamento, explicações
tests/               testes
archive/legacy/      protótipo antigo (referência)
config.example.env   exemplo de configuração
requirements.txt     deps opcionais de voz
CONTEXTO-PAP.md      contexto completo do projeto (para humanos e IAs)
```

---

## Como correr (desenvolvimento)

Requisitos: **Python 3.11+** (recomendado). O núcleo (lembretes + API + UI) corre com a biblioteca standard; voz e wake pedem pacotes extra.

```bash
git clone https://github.com/BarruGumar/PAP-RIC.git
cd PAP-RIC

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux:
# source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt   # testes

copy config.example.env .env          # Windows
# cp config.example.env .env          # Linux
```

Coloca o modelo Piper em `ric-data/vozes/` (ver `py -m ric voices`).

**Ollama (opcional):** instala [Ollama](https://ollama.com), depois `ollama pull qwen2.5:3b`.

### Arranque

```bash
py -m ric ui
```

Abre [http://127.0.0.1:8787](http://127.0.0.1:8787).

### Comandos úteis

```bash
py -m ric add "Beber água" 09:00
py -m ric soon "Teste" --minutos 1
py -m ric list
py -m ric say "Olá, eu sou o RIC."
py -m ric voices
py -m ric wake-setup
```

Wake «ei RIC»: segue [`docs/ROTEIRO-WAKE-EI-RIC.md`](docs/ROTEIRO-WAKE-EI-RIC.md), depois `py -m ric wake-install <caminho/ric.onnx>`.

### Testes

```bash
py -m pytest tests/ -v
```

---

## Documentação

| Documento | Conteúdo |
|---|---|
| [`CONTEXTO-PAP.md`](CONTEXTO-PAP.md) | Visão, decisões, estado, calendário |
| [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) | Arquitetura acordada |
| [`docs/PLANEAMENTO.md`](docs/PLANEAMENTO.md) | Cronograma e etapas |
| [`docs/metas/`](docs/metas/README.md) | Fichas de funcionalidades |
| [`docs/codigo/`](docs/codigo/README.md) | Explicação por módulo |
| [`docs/CORRECOES-PRE-PROJETO.md`](docs/CORRECOES-PRE-PROJETO.md) | Textos fechados com o orientador |

---

## Estado e próximos passos

**Feito:** arquitetura, 1.ª fatia lembretes/API/UI, Piper, Whisper, Ollama na conversa, wake contínuo (modelo temporário), hardware fechado (NUC i3).

**A seguir:** treinar e instalar «ei RIC»; validar Mint XFCE + tactile no NUC; PIN cuidador; música/histórias; polish para defesa.

Calendário provisório e etapas: [`docs/PLANEAMENTO.md`](docs/PLANEAMENTO.md).

---

## Privacidade e ética

- Local-first: funções essenciais sem Internet  
- Sem gravação de áudio por defeito; logs técnicos (frases só com `RIC_DEBUG=1`)  
- Não substitui médico, enfermeiro ou cuidador  
- Dados pessoais do aluno (CC, telefone, etc.) **não** entram neste repositório  

---

## Créditos

- **Autor:** Pedro Albuquerque  
- **Orientação:** Gil Ribeiro (ETEO)  
- Tecnologias: [Piper](https://github.com/rhasspy/piper), [faster-whisper](https://github.com/SYSTRAN/faster-whisper), [openWakeWord](https://github.com/dscripka/openWakeWord), [Ollama](https://ollama.com), Qwen2.5  

Inspiração visual do rosto: estilo companheiro minimalista (EVE); o corpo físico é um gato estático original do projeto — ver [`docs/estudos/VISUAL-E-CORPO.md`](docs/estudos/VISUAL-E-CORPO.md).

## Licença

Projeto escolar (PAP). Uso e redistribuição: contactar o autor. Licença formal a definir antes de qualquer divulgação pública alargada.
