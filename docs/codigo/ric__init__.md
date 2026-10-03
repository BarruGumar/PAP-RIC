# Explicação: `ric/__init__.py`

## Para que serve

Em Python, uma pasta com `__init__.py` torna-se um **pacote** importável.

Por isso existe:

```powershell
py -m ric
```

e também:

```python
from ric import __version__
```

Sem este ficheiro (em versões antigas / certos modos), a pasta `ric/` não seria tratada como pacote de forma fiável.

## Conteúdo

```python
"""RIC — Robô Inteligente Companheiro (núcleo de lembretes locais)."""
```

- Docstring do pacote: descrição curta do que é o `ric`.

```python
__version__ = "0.1.0"
```

- Versão do núcleo de lembretes.
- Usada no CLI (`py -m ric --version`) via `ric/cli.py`.
- Convenção semântica simples: `0.1.0` = MVP inicial.

## Relação com o resto

| Ficheiro | Relação |
|---|---|
| `ric/cli.py` | Importa `__version__` |
| `ric/__main__.py` | Permite executar o pacote com `-m` |
| `ric/db.py` | Parte do mesmo pacote |

## Notas PAP

- Ficheiro pequeno, mas importante na estrutura do projeto.
- Quando o RIC crescer (UI, Ollama), a versão pode subir (ex.: `0.2.0`).
