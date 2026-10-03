# Explicação: `ric/llm.py`

## Para que serve

Liga o RIC ao **Ollama** (LLM local `qwen2.5:3b`) para:

1. **Conversar** contigo em português de Portugal  
2. **Agendar / listar / confirmar / adiar** lembretes através de ferramentas  
3. **Gerar uma frase amigável** quando chega a hora do aviso  

A verdade dos horários continua na SQLite (`ric/db.py`). A LLM **pede** ações; o backend **executa e valida**.

## Dependências

- Ollama a correr em `http://127.0.0.1:11434`
- Modelo: `qwen2.5:3b`
- Sem bibliotecas pip extra (usa `urllib`)

## Funções principais

| Função | Papel |
|---|---|
| `estado()` | Verifica se o Ollama e o modelo estão disponíveis |
| `conversar(mensagem, historico)` | Chat + tool calls + resposta final |
| `frase_aviso(titulo, tipo, hora)` | Frase curta para o overlay de alerta |
| `_executar_ferramenta(...)` | Corre ações na base de dados |

## Ferramentas (tools)

- `agendar_lembrete(titulo, hora, tipo?)`
- `listar_lembretes()`
- `confirmar_lembrete(id)`
- `adiar_lembrete(id, minutos?)`

## Fluxo de uma conversa

```
Utilizador: "Lembra-me de beber água às 16:45"
        │
        ▼
 Ollama (tools) → agendar_lembrete(...)
        │
        ▼
 db.adicionar(...)  → ric.db
        │
        ▼
 Ollama (resposta natural) → "Agendei para as 16:45…"
```

## Se a LLM falhar

- Chat devolve erro claro (503)
- Formulário manual e lista de lembretes **continuam a funcionar**
- `frase_aviso` cai para: `É a hora: {titulo}`

## Privacidade (PAP)

- Tudo local (PC + Ollama)
- Sem cloud por defeito
- Sem diagnósticos médicos no system prompt
