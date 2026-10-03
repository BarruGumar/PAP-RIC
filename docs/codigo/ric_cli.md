# Explicação: `ric/cli.py`

## Para que serve

É a **interface de linha de comandos** (CLI) do RIC.

Traduz o que escreves no terminal em ações sobre a base de dados (`ric/db.py`).

Exemplos:

```powershell
py -m ric demo
py -m ric add "Tomar medicamento" 18:00 --tipo medicamento
py -m ric list
py -m ric run
py -m ric ok 1
py -m ric adiar 1
```

---

## Importações

| Import | Para quê |
|---|---|
| `argparse` | Ler comandos e opções do terminal |
| `sys` | Escrever erros em `stderr` |
| `time` | Esperar entre verificações no `run` |
| `datetime` / `timedelta` | Horas da demo e do adiamento |
| `ric.db` | Operações na base SQLite |
| `__version__` | Mostrar versão com `--version` |

`from __future__ import annotations` melhora anotações de tipos em Python 3.11.

---

## `_fmt(lembrete)`

Formata um lembrete numa linha legível, por exemplo:

```text
#  1  18:00  [medicamento]  Tomar medicamento  (pendente)  -> 2026-10-03T18:00:00
```

Usa ASCII (`->`) para não rebentar na consola Windows (cp1252).

---

## Comandos (funções `cmd_*`)

Cada comando:

1. recebe `args` (argumentos já lidos pelo `argparse`);
2. chama funções de `db`;
3. imprime resultado;
4. devolve `0` (ok) ou `1` (erro).

### `cmd_demo`

- Apaga lembretes antigos (`limpar_tudo`).
- Cria 3 exemplos:
  - medicamento ~1 minuto à frente (para testar `run` depressa);
  - consulta às 10:30;
  - tarefa “Beber água” às 16:00.
- Mostra comandos úteis com o `id` real do primeiro lembrete.

### `cmd_add`

- Cria lembrete com título, hora e `--tipo`.
- Se hora/tipo/título forem inválidos → mensagem de erro e código `1`.

### `cmd_list`

- Lista todos os lembretes.
- Se a lista estiver vazia, sugere o comando `add`.

### `cmd_ok`

- Confirma lembrete pelo `id` (“já fiz”).
- Se o `id` não existir → erro.

### `cmd_adiar`

- Adia o lembrete (`--minutos`, defeito 10).
- Atualiza `proximo_em` na base.

---

## `_alerta(lembrete)`

Mostra um aviso bem visível no terminal e tenta emitir som:

1. Tenta `winsound.MessageBeep` (Windows).
2. Se falhar, usa `\a` (bell do terminal).

Também imprime os comandos para confirmar ou adiar.

**Nota:** neste passo a frase do aviso é fixa (texto do programa). Mais tarde pode ser gerada pelo Qwen/Ollama — mas o disparo continua a vir do backend.

---

## `cmd_run`

Motor que **fica a correr** e vigia lembretes:

1. `init_db()` garante que a base existe.
2. Loop infinito:
   - pede a `db.devidos()` os lembretes cuja hora já chegou;
   - se ainda não avisou (controlo com o conjunto `avisados`), marca `disparado` e chama `_alerta`;
   - sincroniza com confirmações/adiamentos feitos noutro terminal;
   - `time.sleep(intervalo)` (defeito 5 segundos).
3. `Ctrl+C` → `KeyboardInterrupt` → mensagem “RIC parado.” e sai com `0`.

### Conjunto `avisados`

Evita spam do mesmo alerta em cada ciclo de 5 segundos enquanto o estado continua `disparado`.

Se o utilizador **adiar**, o `id` pode sair de `avisados` para voltar a alertar mais tarde.

---

## `build_parser()`

Define a “gramática” dos comandos com `argparse`:

| Subcomando | Argumentos | Função |
|---|---|---|
| `demo` | — | `cmd_demo` |
| `add` | `titulo`, `hora`, `--tipo` | `cmd_add` |
| `list` | — | `cmd_list` |
| `ok` | `id` | `cmd_ok` |
| `adiar` | `id`, `--minutos` | `cmd_adiar` |
| `run` | `--intervalo` | `cmd_run` |
| `ui` | `--host`, `--port`, `--sem-browser` | `cmd_ui` → interface web |

`set_defaults(func=...)` liga cada subcomando à função Python certa.

---

## `main(argv=None)`

1. Constrói o parser.
2. Lê os argumentos (`sys.argv` se `argv` for `None`).
3. Chama `args.func(args)`.
4. Devolve o código de saída.

É o ponto único usado por:

- `ric/__main__.py` (`py -m ric`)
- `main.py` (`py main.py`)

---

## Fluxo de um comando completo

```
Terminal: py -m ric ok 1
        │
        ▼
 __main__.py → cli.main()
        │
        ▼
 argparse escolhe cmd_ok
        │
        ▼
 db.confirmar(1)
        │
        ▼
 UPDATE em ric.db → imprime resultado
```

---

## Notas PAP

- Separação clara: **CLI** (apresentação) vs **DB** (dados).
- Lembretes não dependem da LLM.
- Mensagens do terminal em português; evita caracteres exóticos na consola Windows.
- Próximo passo natural: em `_alerta`, pedir uma frase ao Ollama **sem** deixar de funcionar se o Ollama estiver desligado.
