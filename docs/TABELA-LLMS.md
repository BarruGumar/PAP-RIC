# Tabela comparativa de LLMs locais — RIC (PAP)

Modelo de referência do projeto: **`qwen2.5:3b` via Ollama**.  
Comparação com **`qwen2.5:7b`** medida em 2026-10-11 no PC do Pedro (caminho real `ric.llm.conversar`, com tools).

## Setup de teste (igual para todos)

| Item | Valor |
|---|---|
| Runtime | Ollama 0.40.2 no PC do aluno |
| Hardware | Windows 11, 16 GB RAM (~2–3 GB livres no arranque do teste) |
| Prompt A | `Olá, como estás?` (conversa) |
| Prompt B | `Lembra-me de beber água às 18:30` (tool agendar) |
| Prompt B natural | `olha, todos os dias as oito da manha tenho de tomar o comprimido da tensao, avisa-me` |
| Prompt C | `Que géneros de música tens?` / `Toca metal` (tools música) |
| Prompt D | `Conta-me uma história curta` (companhia) |
| Medição | Tempo total da chamada `conversar` já com o modelo aquecido |

## Comparação (2026-10-11)

| Critério | qwen2.5:3b (principal) | qwen2.5:7b (PC forte) | llama3.2:3b | qwen2.5:1.5b |
|---|---|---|---|---|
| Qualidade conversa (1–5) | 3 — responde, mas misturou memória antiga | 4 — cumprimentou de forma clara | _a medir_ | _a medir_ |
| Tools (agendar/música) (1–5) | 3 — agendou o B simples e tocou metal; falhou o B natural e a lista de géneros | 5 — agendou B e B natural; listou géneros; tocou metal | _a medir_ | _a medir_ |
| Latência típica (s) | 0,5–4,6 (quente) | 4–24 (quente) | _a medir_ | _a medir_ |
| RAM aproximada em uso | ~3–4 GB | ~5,1 GB (CPU+GPU) | ~3–4 GB | ~2 GB |
| Privacidade | Local | Local | Local | Local |
| Adequação ao hardware atual | Principal (rápido) | Cabe nos 16 GB; mais lento; melhor em fala livre | Opcional | Se 3B for lento |

### Tempos medidos (modelo já aquecido)

| Prompt | qwen2.5:3b | qwen2.5:7b | Notas |
|---|---|---|---|
| A conversa | 0,5 s | 4,0 s | Ambos OK |
| B lembrete 18:30 | 1,7 s | 14,7 s | Ambos agendaram (`agendar:ok`) |
| B natural (comprimido às 8) | 4,6 s — **falhou** | 17,5 s — **ok** | 3B pediu a hora de novo; 7B criou às 08:00 e falou em todos os dias |
| C géneros | 2,7 s — **falhou** | 23,2 s — **ok** | 3B devolveu lixo de memória antiga; 7B listou géneros reais |
| C tocar metal | 0,6 s | 10,4 s | Ambos tocaram (`tocar:ok`) |
| D história | 1,5 s | 24,2 s | 7B mais longa e mais natural |

Aquecimento (primeira carga do modelo nesta sessão): 3B ~6,7 s; 7B ~15,1 s.

## Protocolo de teste (repetido)

1. Aquecer o modelo com `ola`.
2. Correr A, B, B natural, C géneros, C tocar, D pelo `ric.llm.conversar`.
3. Registar tempo, se a tool foi chamada e se a resposta faz sentido em português de Portugal.

## Conclusões (atualizadas 2026-10-11)

1. **`qwen2.5:3b`** continua válido como modelo principal rápido: agendar simples e tocar música funcionam.
2. **`qwen2.5:7b`** ganha onde a etapa 1 precisa de fala livre: o pedido natural do comprimido às oito só o 7B percebeu e agendou.
3. O 7B é **3 a 10× mais lento** neste PC. Em conversa falada, 15–24 s por resposta pode ser demasiado.
4. Funções críticas (disparo de lembretes) **não dependem** da LLM — fallbacks em `ric/llm.py` + SQLite.
5. Decisão prática: manter o 3B por defeito; usar o 7B nos testes de fala livre e no NUC, se a RAM for ≥ 16 GB e a latência for aceitável com a voz.

## Data / hardware do teste

- Data: 2026-10-11
- PC / RAM / CPU: Windows 11 Home, 16 GB RAM, Ollama a usar CPU+GPU no 7B
- Ollama versão: 0.40.2
