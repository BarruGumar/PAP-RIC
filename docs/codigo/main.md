# Explicação: `main.py`

## Para que serve

É um **atalho** na raiz do projeto. Em vez de escrever sempre `py -m ric ...`, podes usar:

```powershell
py main.py list
py main.py demo
```

Não contém lógica própria do RIC. Apenas chama o mesmo ponto de entrada que o pacote `ric`.

## Linha a linha

```python
"""Atalho local: python main.py <comando> ..."""
```

- Comentário/documentação do módulo (docstring).
- Explica o propósito do ficheiro a quem o abre.

```python
from ric.cli import main
```

- Importa a função `main` definida em `ric/cli.py`.
- Essa função trata dos argumentos da linha de comandos (`demo`, `list`, `add`, etc.).

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

- `if __name__ == "__main__":` só corre quando executas o ficheiro diretamente (`py main.py`), não quando alguém faz `import main`.
- `main()` devolve um código de saída (`0` = sucesso, `1` = erro).
- `raise SystemExit(...)` termina o programa com esse código, o que é o comportamento normal de ferramentas CLI.

## Relação com o resto

| Ficheiro | Relação |
|---|---|
| `ric/cli.py` | Onde está a lógica real dos comandos |
| `ric/__main__.py` | Alternativa oficial: `py -m ric` |

## Notas PAP

- Útil para demos rápidas.
- Não é obrigatório: o caminho “oficial” documentado é `py -m ric`.
