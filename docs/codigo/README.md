# Explicações do código — RIC

Esta pasta explica **cada ficheiro de código** do projeto, ao pormenor, para a PAP e para qualquer pessoa (ou IA) que precise de perceber o sistema.

## Como está organizado

| Ficheiro de código | Explicação |
|---|---|
| `main.py` | [main.md](main.md) |
| `ric/__init__.py` | [ric__init__.md](ric__init__.md) |
| `ric/__main__.py` | [ric__main__.md](ric__main__.md) |
| `ric/db.py` | [ric_db.md](ric_db.md) |
| `ric/cli.py` | [ric_cli.md](ric_cli.md) |
| `ric/web_server.py` | [ric_web_server.md](ric_web_server.md) |
| `ric/web/` (HTML/CSS/JS) | [ric_web_ui.md](ric_web_ui.md) |
| `ric/llm.py` | [ric_llm.md](ric_llm.md) |

## Regra do projeto

Sempre que se **criar ou alterar** código relevante, a explicação correspondente em `docs/codigo/` deve ser **criada ou atualizada**.

## Fluxo geral (visão rápida)

```
py -m ric <comando>
        │
        ▼
 ric/__main__.py  →  ric/cli.py  →  ric/db.py  →  ric/data/ric.db
      (entrada)      (comandos)     (SQLite)         (dados locais)
                          │
                          └─ ui → ric/web_server.py → browser (ric/web/)
                                        │
                                        └─ chat/frase → ric/llm.py → Ollama (qwen2.5:3b)
```

`main.py` é só um atalho opcional para o mesmo `cli`.
