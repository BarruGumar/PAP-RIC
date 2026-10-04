# Guia — Lembretes RIC no Windows

## Requisitos

- Python 3.10+ — neste PC usa o launcher: `py --version`
- Pasta do projeto: `C:\Users\pedro\OneDrive\Documentos\PAP`

> Se `python` abrir a Microsoft Store, usa sempre `py` (ou `py -3`).

## Comandos

Na pasta do projeto:

```powershell
py -m ric demo
py -m ric list
py -m ric add "Tomar medicamento" 18:00 --tipo medicamento
py -m ric run
py -m ric ui
py -m ric ok 1
py -m ric adiar 1
```

Também podes usar: `py main.py list`

## Interface web (recomendado no dia a dia)

```powershell
py -m ric ui
```

Abre o browser em `http://127.0.0.1:8787/`.

1. Confirma que o Ollama está a correr (modelo `qwen2.5:3b`) — opcional  
2. Na conversa podes usar linguagem natural, por exemplo:
   - `Lembra-me de beber água às 16:45`
   - `Me lembra de beber água daqui 1 minuto`
   - `Avisa-me em 5 minutos para tomar chá`
3. Vê o lembrete na lista  
4. Aviso: hora 1–2 min à frente → overlay + beep; no terminal aparece `[RIC watchdog]`  
5. Usa **Já fiz** ou **Adiar 10 min**  

O RIC combina a LLM com **interpretação local** (tempos relativos, pausa/continua).  
Não precisas de frases exactas. Se a LLM estiver desligada, lista/player/overlay continuam.  
Checklist: `docs/CHECKLIST-REGRESSAO.md`.

## Músicas offline

Pasta: `ric\musica\<genero>\ficheiro.mp3` (ou `.wav`, etc.)

Frases canónicas na conversa:
- `Que géneros tens?` / `Que músicas tens de metal?`
- `Toca metal` / `Toca Caravan`
- `Pausa` → `Continua` → `Do começo` / `Reinicia`
- `Volume mais baixo` / `Volume mais alto` / `Volume 40` / `mudo`
- Mensagem normal (`Olá`) **não** deve parar a música

## Memória e voz

- Nome/preferências: `O meu nome é Pedro` (guardado em SQLite)
- História: `Conta-me uma história curta`
- TTS nos avisos (Windows SAPI se disponível)
- Botão **Falar** = ditado no browser (quando suportado)

## O que cada comando faz

| Comando | Função |
|---|---|
| `demo` | Limpa e cria 3 lembretes de exemplo (um ~1 min à frente) |
| `add` | Cria lembrete (`medicamento`, `consulta`, `tarefa`, `outro`) |
| `list` | Mostra todos os lembretes |
| `run` | Fica a vigiar e alerta quando chega a hora (som + texto) |
| `ok ID` | Confirma (“já fiz”) |
| `adiar ID` | Adia 10 minutos (ou `--minutos N`) |

## Dados

- Base local: `ric\data\ric.db`
- Privado no teu PC — não vai para a cloud
- O ficheiro `.db` está no `.gitignore`

## Teste rápido sugerido

1. `py -m ric demo`
2. `py -m ric list`
3. `py -m ric run` e espera ~1 minuto pelo alerta do medicamento
4. Noutro terminal: `py -m ric ok 1`
5. Confirma com `py -m ric list` que ficou `confirmado`

## Nota PAP

Os lembretes **não dependem** da LLM nem da internet. A ligação ao Qwen/Ollama é o passo seguinte (só para gerar a frase do aviso).
