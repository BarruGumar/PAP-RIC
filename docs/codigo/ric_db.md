# Explicação: `ric/db.py`

## Para que serve

É o **cérebro de dados** do RIC (SQLite local):

- lembretes (criar por HH:MM ou por instante `adicionar_em`, listar, confirmar, adiar, devidos);
- **perfil** (preferências: nome, gostos…);
- **conversas** (histórico de chat + resumo quando cresce);
- **confirmações** (histórico simples de “já fiz”).

**Importante para a PAP:** funciona **offline**, sem LLM e sem internet.

---

## Constantes e caminhos

```python
DATA_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DATA_DIR / "ric.db"
```

- `__file__` = caminho deste ficheiro (`.../ric/db.py`).
- `.parent` = pasta `ric/`.
- `DATA_DIR` = `ric/data/`.
- `DB_PATH` = `ric/data/ric.db` (ficheiro da base de dados).

```python
TIPOS_VALIDOS = ("medicamento", "consulta", "tarefa", "outro")
```

- Tipos aceites no MVP (alinhados com as metas da PAP).

---

## Classe `Lembrete`

```python
@dataclass
class Lembrete:
    id: int
    titulo: str
    hora: str          # HH:MM (hora “de rotina”)
    tipo: str
    estado: str        # pendente | disparado | confirmado | adiado
    proximo_em: str    # data/hora ISO do próximo disparo
    criado_em: str
```

- `@dataclass` gera automaticamente `__init__`, etc.
- Representa **um** lembrete em memória Python (não é a tabela SQL em si).

### Estados

| Estado | Significado |
|---|---|
| `pendente` | Ainda não disparou |
| `disparado` | Já foi alertado pelo `run` |
| `confirmado` | Pessoa disse “já fiz” (`ok`) |
| `adiado` | Foi adiado; espera novo `proximo_em` |

---

## `_connect()`

```python
def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

- Garante que a pasta `data/` existe.
- Abre ligação SQLite ao ficheiro `ric.db`.
- `row_factory = sqlite3.Row` permite aceder a colunas por nome: `row["titulo"]`.

O `_` no início significa “função interna” (uso dentro do módulo).

---

## `init_db()`

Cria as tabelas se ainda não existirem:

### `lembretes`

| Coluna | Função |
|---|---|
| `id` | Identificador automático |
| `titulo` | Texto do lembrete |
| `hora` | Hora da rotina (HH:MM) |
| `tipo` | medicamento / consulta / ... |
| `estado` | Ciclo de vida do aviso |
| `proximo_em` | Quando deve voltar a alertar |
| `criado_em` | Quando foi criado |

### `perfil`

Chave/valor (`nome`, `genero_favorito`, …) com `atualizado_em`.

### `conversas`

Mensagens `user` / `assistant` / `system_resumo` para persistir o chat.

### `confirmacoes`

Registo opcional de ações `confirmar` / `adiar` (histórico simples para a PAP).

`CREATE TABLE IF NOT EXISTS` = seguro correr várias vezes.

---

## `_proximo_para_hora(hora)`

Converte `"18:00"` na **próxima** data/hora concreta.

1. Valida formato `HH:MM`.
2. Constrói “hoje às HH:MM”.
3. Se essa hora já passou, passa para **amanhã**.

Exemplo: são 15:00 e pedes `10:30` → agenda para amanhã 10:30.

---

## `adicionar(titulo, hora, tipo)`

1. Valida tipo e título.
2. Calcula `proximo_em`.
3. Faz `INSERT` na base com estado `pendente`.
4. Devolve o `Lembrete` criado (via `obter`).

Usa `?` nos SQL (parâmetros) para evitar injeção SQL.

---

## `listar(incluir_confirmados=True)`

- Por defeito lista **todos**.
- Se `incluir_confirmados=False`, esconde os já confirmados (útil no `run`).
- Ordena por `proximo_em`, depois `id`.

---

## `obter(lembrete_id)`

- Vai buscar um lembrete pelo número.
- Se não existir → `LookupError` (o CLI mostra “não encontrado”).

---

## `confirmar(lembrete_id)` / `adiar(...)`

- Marca estado `confirmado` ou `adiado` (com novo `proximo_em`).
- Regista também em `confirmacoes`.

---

## `marcar_disparado(lembrete_id)`

- Usado pelo `run` quando mostra o alerta.
- Evita tratar o lembrete como se nunca tivesse avisado.

---

## `devidos(agora=None)`

Devolve lembretes em que:

- estado é `pendente`, `adiado` ou `disparado`;
- e `proximo_em <= agora`.

É a pergunta central do motor: **“há algo para avisar agora?”**

---

## `limpar_tudo()`

- Apaga todos os lembretes.
- Limpa também `sqlite_sequence` para o próximo `id` voltar a 1.
- Usado pelo comando `demo` para recomeçar limpo.

---

## `_row_to_lembrete(row)`

Converte uma linha SQLite (`sqlite3.Row`) num objeto `Lembrete` Python.

---

## Perfil e conversas

| Função | Papel |
|---|---|
| `guardar_preferencia(chave, valor)` | UPSERT em `perfil` |
| `obter_perfil()` / `perfil_texto()` | Ler preferências (texto para o prompt LLM) |
| `adicionar_mensagem(role, conteudo)` | Guardar mensagem no chat |
| `listar_mensagens(limite)` | Últimas N mensagens (UI) |
| `historico_para_llm(limite)` | Formato `{role, content}` para o Ollama |
| `limpar_conversas()` | Apagar histórico |
| `_podar_conversas()` | Mantém tamanho; cria `system_resumo` se crescer |

---

## Diagrama de dados

```
Pessoa / CLI
    │
    ▼
 ric/db.py  ──── lê/escreve ────►  ric/data/ric.db
                                      (local, privado)
```

## Notas PAP / privacidade

- A base fica no PC do aluno.
- Está no `.gitignore` para não ir para o GitHub por engano.
- A LLM (Ollama) **não** deve ser necessária para estas funções.
