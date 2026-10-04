# Tabela comparativa de LLMs locais — RIC (PAP)

Modelo de referência do projeto: **`qwen2.5:3b` via Ollama**.  
Preencher medições reais no PC do Pedro antes da defesa.

## Setup de teste (igual para todos)

| Item | Valor |
|---|---|
| Runtime | Ollama no PC do aluno |
| Prompt A | `Olá, como estás?` (conversa) |
| Prompt B | `Lembra-me de beber água às HH:MM` (tool agendar) |
| Prompt C | `Que géneros de música tens?` / `Toca metal` (tools música) |
| Prompt D | `Conta-me uma história curta` (companhia) |
| Medição | Cronómetro; 3 corridas cada |

## Comparação

| Critério | qwen2.5:3b (principal) | llama3.2:3b (alternativa) | qwen2.5:1.5b (PC fraco) | qwen2.5:7b (PC forte) |
|---|---|---|---|---|
| Qualidade conversa (1–5) | _a medir_ | _a medir_ | _a medir_ | _a medir_ |
| Tools (agendar/música) (1–5) | _a medir_ | _a medir_ | _a medir_ | _a medir_ |
| Latência típica (s) | _a medir_ | _a medir_ | _a medir_ | _a medir_ |
| RAM aproximada | ~3–4 GB | ~3–4 GB | ~2 GB | ~6–8 GB |
| Privacidade | Local | Local | Local | Local |
| Adequação ao hardware atual | Principal | Opcional | Se 3B for lento | Só se PC aguentar |
| Notas | Já testado pelo Pedro — “suficientemente boa” | Comparação PAP | Fallback fraco | Melhor qualidade, mais pesado |

## Protocolo de teste (repetir 3× por modelo)

1. Arrancar Ollama com o modelo a testar.
2. Cronometrar Prompt A.
3. Cronometrar Prompt B (hora 2 min à frente).
4. Cronometrar Prompt C.
5. Avaliar Prompt D (clareza e tom).
6. Registar falhas (tool não chamada, inventar música, etc.).

## Conclusões (rascunho)

1. Modelo principal: `qwen2.5:3b` — já validado como “suficientemente bom”.
2. Funções críticas (lembretes) **não dependem** da LLM — fallbacks em `ric/llm.py` + SQLite.
3. Cloud só como suplente opcional — fora do caminho crítico da PAP.
4. Chat/companhia degradam com modelo mais fraco; UI e player mantêm-se.

## Data / hardware do teste

- Data: _______________
- PC / RAM / CPU: _______________
- Ollama versão: _______________
