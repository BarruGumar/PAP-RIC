# Explicação: `ric/__main__.py`

## Para que serve

Este ficheiro é o que Python procura quando corres:

```powershell
py -m ric
```

Ou seja: “executa o pacote `ric` como programa”.

## Linha a linha

```python
from ric.cli import main
```

- Importa a função principal do CLI.

```python
raise SystemExit(main())
```

- Corre o CLI.
- Termina o processo com o código devolvido por `main()`:
  - `0` → correu bem
  - `1` → erro (ex.: lembrete inexistente, hora inválida)

## Porquê `raise SystemExit` e não só `main()`?

- `SystemExit` é a forma correta de terminar um programa CLI com um código de saída.
- Scripts e automação (e a PAP em testes) podem verificar se o comando falhou.

## Relação com o resto

```
py -m ric list
      │
      ▼
ric/__main__.py
      │
      ▼
ric/cli.py → cmd_list() → ric/db.py
```

## Diferença face a `main.py`

| Entrada | Ficheiro usado |
|---|---|
| `py -m ric ...` | `ric/__main__.py` |
| `py main.py ...` | `main.py` na raiz |

Ambos acabam na mesma função `ric.cli.main`.
