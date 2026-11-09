"""System prompt e tools P1 (fatia LLM mínima)."""

from __future__ import annotations

SYSTEM_PROMPT = """
És o Ric, companheiro digital local. Fala sempre em português de Portugal (usa «tu», nunca «você»).
Responde APENAS ao que a pessoa disse, em 1 frase (máx. 2), fácil de ouvir em voz alta.
Se a frase for confusa, incompleta ou sem sentido, pede educadamente para repetir — não inventes um tema.
Não diagnostiques nem receites medicamentos.
Lembretes:
- Para VER lembretes usa listar_lembretes ou proximo_lembrete.
- Para CRIAR um lembrete não-médico (água, passeio, tarefa, consulta) usa sempre criar_lembrete com título e hora em HH:MM.
- Para APAGAR um lembrete autorizado (não médico / não crítico) usa apagar_lembrete (id ou título).
- Só confirma criar/apagar DEPOIS de a ferramenta devolver sucesso.
- Se faltar a hora ao criar, pergunta a hora (HH:MM) — não inventes.
- Se houver vários com o mesmo título ao apagar, pergunta qual (hora/id).
- Medicação / comprimidos / lembretes críticos: NÃO uses criar_lembrete nem apagar_lembrete; diz que só o cuidador pode gerir esses.
""".strip()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "listar_lembretes",
            "description": "Lista os lembretes activos (título, hora, tipo).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "proximo_lembrete",
            "description": "Devolve o próximo lembrete pendente.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "criar_lembrete",
            "description": (
                "Cria um lembrete NÃO médico (tarefa, consulta ou outro). "
                "Proibido para medicamento/medicação. Requer título e hora HH:MM."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {
                        "type": "string",
                        "description": "O que lembrar (ex.: Beber água).",
                    },
                    "hora": {
                        "type": "string",
                        "description": "Hora no formato HH:MM (24h).",
                    },
                    "tipo": {
                        "type": "string",
                        "enum": ["tarefa", "consulta", "outro"],
                        "description": "Categoria. Default: tarefa.",
                    },
                },
                "required": ["titulo", "hora"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apagar_lembrete",
            "description": (
                "Apaga um lembrete NÃO médico e NÃO crítico. "
                "Indica id e/ou titulo. Proibido para medicamento/crítico."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID do lembrete (preferível se conhecido).",
                    },
                    "titulo": {
                        "type": "string",
                        "description": "Título ou parte do título (ex.: beber água).",
                    },
                },
            },
        },
    },
]

FALLBACK_REPLY = (
    "Desculpa, neste momento não consigo conversar bem. "
    "Os teus lembretes continuam activos."
)

# Só anexar tools Ollama quando a pergunta parecer sobre lembretes —
# no CPU, tools em *todas* as mensagens tornam o 1.º turno muito lento.
_TOOL_HINTS = (
    "lembrete",
    "lembretes",
    "próximo",
    "proximo",
    "medicamento",
    "comprimido",
    "remédio",
    "remedio",
    "agenda",
    "hora de",
    "que horas",
    "cria",
    "criar",
    "marca",
    "marcar",
    "lembrar",
    "lembra",
    "avisa",
    "avisar",
    "apaga",
    "apagar",
    "remove",
    "remover",
    "cancela",
    "cancelar",
)


def needs_reminder_tools(text: str) -> bool:
    t = (text or "").casefold()
    if not t:
        return False
    return any(hint in t for hint in _TOOL_HINTS)
