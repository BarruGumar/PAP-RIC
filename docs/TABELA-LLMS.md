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
| Notas | Já testado pelo Pedro — “suficientemente boa” | Comparação PAP | Fallback fraco. É o tamanho que o AI HAT+ 2 publica | Melhor qualidade, mais pesado |

## AMALIA-9B (pedido do orientador, 2026-10-18)

Modelo de texto para português de Portugal. Licença Apache-2.0. Publicado a 1 de julho de 2026. Não ouve nem fala.

| Variante no Ollama | Tamanho | Quando |
|---|---|---|
| `teex/amalia:q4_K_M` | 5,6 GB | A testar num PC com 16 GB, ao lado do faster-whisper `small` |
| `teex/amalia:q8_0` | 9,7 GB | Só se o Q4 falhar por qualidade e ainda sobrar RAM |

Critério para passar a modelo principal: nos prompts A a D desta tabela, fala mais claro em português de Portugal do que o `qwen2.5:3b` e a ferramenta de agendar é chamada. O estudo completo está em [`FEEDBACK-ORIENTADOR.md`](FEEDBACK-ORIENTADOR.md).

## Voz — audição no PC (2026-10-18)

O roteiro está em [`ROTEIRO-VOZ.md`](ROTEIRO-VOZ.md). Corre no PC do Pedro. O Piper e o Whisper ainda não entram no `ric/`.

| | Piper tugão | tts-eu-pt |
|---|---|---|
| A hora do comprimido percebe-se? | por medir | por medir |
| «16:54» soa a português de Portugal? | por medir | por medir |
| Notas | | |
| Fico com esta voz? | | |

Voz escolhida: por medir.  
Data da audição: _______________  
PC e RAM: _______________

Reconhecimento com faster-whisper, Ollama aberto e rede desligada na corrida que conta.

| | |
|---|---|
| Modelo Whisper | por medir (`small`, ou `base` se o `small` não couber) |
| Ollama aberto | por medir |
| Frases certas | ____ / 10 |

As dez frases e o sítio para colar o texto transcrito estão no roteiro. Esta tabela fica assim até essa audição.

## Protocolo de teste (repetir 3× por modelo)

1. Arrancar Ollama com o modelo a testar.
2. Cronometrar Prompt A.
3. Cronometrar Prompt B (hora 2 min à frente).
4. Cronometrar Prompt C.
5. Avaliar Prompt D (clareza e tom).
6. Registar falhas (tool não chamada, inventar música, etc.).

## Modelos Qwen com entrada de áudio (2026-10-16)

O Pedro encontrou modelos Qwen que recebem áudio, não só texto. Existem três linhas. Nenhuma substitui o `qwen2.5:3b` nesta PAP.

| Modelo | O que aceita | O que devolve | Onde corre | Porque fica de fora |
|---|---|---|---|---|
| Qwen2-Audio-7B | Áudio e texto. Frases curtas, até cerca de 30 s | Texto | Transformers ou Nexa. O Ollama do RIC não recebe o áudio | Cerca de 16 GB de VRAM em FP16. A versão quantizada existe, mas noutro programa |
| Qwen2.5-Omni-3B e 7B | Texto, imagem, áudio e vídeo | Texto e fala | Transformers ou vLLM. O 3B em BF16 parte de cerca de 18 GB para um vídeo curto. Há relatos de áudio por volta de 12 GB | Os testes oficiais de reconhecimento são inglês, chinês, cantonês e francês. Num estudo de 2026 sobre português do Brasil, o Omni-3B errou mais do que o Whisper |
| Qwen3-Omni-30B-A3B | Texto, imagem, áudio e vídeo. A lista de 19 línguas faladas inclui português | Texto e fala, também em português | Transformers ou vLLM. A ficha oficial pede cerca de 79 GB de GPU no modelo Instruct | Não cabe num PC reaproveitado. A API DashScope envia o áudio para a nuvem da Alibaba |

O Ollama, em outubro de 2026, continua sem entrada de áudio para estes modelos. O pedido está em aberto no projeto (ollama/ollama#12376). O RIC fala com o Ollama por texto, em `http://127.0.0.1:11434`.

Ouvir fica nas duas vias já previstas: Vosk, ou Whisper local se o PC ainda tiver folga com o `qwen2.5:3b` ligado. Um Qwen de áudio só volta a ser candidato se aparecer uma GPU e um teste curto em português de Portugal perceber melhor as frases do que o Whisper, no mesmo PC.

## Conclusões (rascunho)

1. Modelo principal: `qwen2.5:3b` — já validado como “suficientemente bom”.
2. Funções críticas (lembretes) **não dependem** da LLM — fallbacks em `ric/llm.py` + SQLite.
3. Cloud só como suplente opcional — fora do caminho crítico da PAP.
4. Chat/companhia degradam com modelo mais fraco; UI e player mantêm-se.

## Data / hardware do teste

- Data: _______________
- PC / RAM / CPU: _______________
- Ollama versão: _______________
