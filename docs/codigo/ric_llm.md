# Explicação: `ric/llm.py`

## Para que serve

Liga o RIC ao **Ollama** (LLM local `qwen2.5:3b`) para:

1. **Conversar** em português de Portugal  
2. **Agendar / listar / confirmar / adiar** lembretes via tools  
3. **Música offline** (listar / tocar / pausar / continuar / reiniciar / volume)  
4. **Perfil** (`guardar_preferencia`, `obter_perfil`)  
5. **Histórias curtas** (modo especial no prompt)  
6. **Frase amigável** no aviso (`frase_aviso`)

A verdade dos horários e preferências continua na SQLite (`ric/db.py`).

## Dependências

- Ollama em `http://127.0.0.1:11434`
- Modelo: `qwen2.5:3b`
- Sem pip extra (usa `urllib`)

## Funções principais

| Função | Papel |
|---|---|
| `estado()` | Ollama / modelo disponíveis |
| `conversar(mensagem, historico)` | Chat + tools + fallbacks + grava histórico |
| `frase_aviso(...)` | Frase curta para overlay (fallback local) |

## Ferramentas (tools)

Lembretes: `agendar_lembrete`, `listar_lembretes`, `confirmar_lembrete`, `adiar_lembrete`  
Música: `listar_generos`, `listar_musicas`, `tocar_musica`, `pausar_musica`, `continuar_musica`, `reiniciar_musica`, `ajustar_volume`, `definir_volume`  
Memória: `guardar_preferencia`, `obter_perfil`

## Fallbacks / NLU local (quando a LLM não chama a tool)

A `qwen2.5:3b` é pequena: por isso ações críticas têm interpretação em português **no código**, não só no modelo.

- Lembretes: `daqui 1 minuto`, `em 5 minutos`, `às 18:00`, `meia hora` → `interpretar_quando` + `db.adicionar_em`  
- Pausa / continua / do começo / volume / tocar → regex alargadas  
- “O meu nome é …” → grava `perfil.nome`  
- Pedido de história → reforço no system prompt  

Isto aproxima o RIC de “entender o pedido” sem depender de uma LLM cloud grande.

## Persistência

No fim de `conversar`, grava `user` + `assistant` via `db.adicionar_mensagem`.  
Se `historico` não for enviado, usa `db.historico_para_llm(10)`.

## Se a LLM falhar

- Chat → erro 503 claro  
- Lembretes, UI, player e watchdog **continuam**  
- `frase_aviso` → `É a hora: {titulo}`

## Privacidade (PAP)

- Tudo local; sem cloud por defeito  
- Sem diagnósticos médicos no system prompt  
