from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from typing import Any

from ric import db
from ric import music

OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:3b"
TIMEOUT_S = 120

_NUM_PALAVRAS = {
    "um": 1,
    "uma": 1,
    "uns": 1,
    "dois": 2,
    "duas": 2,
    "tres": 3,
    "três": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "quinze": 15,
    "vinte": 20,
    "trinta": 30,
}

SYSTEM_PROMPT = """
És o RIC, companheiro digital local (português de Portugal).
Ajudas a conversar, a gerir lembretes, a lembrar preferências e a tocar músicas OFFLINE.
NÃO diagnosticas nem receitas medicamentos.
NÃO inventas músicas que não existem na biblioteca.
MEMÓRIA:
- Se a pessoa disser o nome ou gostos, usa guardar_preferencia.
- Para recordar o que sabes dela, usa obter_perfil.
- Histórias: se pedirem uma história, conta uma história CURTA (6–10 frases), calma e positiva.
IMPORTANTE SOBRE MÚSICA:
- A música deve CONTINUAR a tocar em fundo durante a conversa normal.
- Só chama ferramentas de música se o utilizador PEDIR explicitamente.
- NÃO pauses nem reinicies música só porque o utilizador falou de outra coisa.
- TOCAR/OUVIR/TROCAR/MUDAR de música ou género → tocar_musica (obrigatório; não digas que trocou sem chamar a tool).
- PAUSAR/PARAR a música → pausar_musica (aceita linguagem natural: “podes pausar”, “para a música”).
- CONTINUAR/RETOMAR do mesmo ponto → continuar_musica.
- DO COMEÇO / REINICIAR → reiniciar_musica (sempre que diga “do começo/início”).
- VOLUME mais baixo/alto → ajustar_volume (delta -0.1 ou +0.1) ou definir_volume (0 a 1).
NUNCA digas ao utilizador para correr comandos nem nomes de ferramentas.
Quando só perguntar o que existe: usa listar_generos ou listar_musicas.
Quando pedirem lembretes: USA SEMPRE agendar_lembrete (não peças só a hora).
Tempos relativos (“daqui 1 minuto”, “em 5 minutos”, “daqui a meia hora”) → converte para HH:MM
com base em “Agora local” e chama a tool de imediato. Também podes passar o texto relativo em hora.
Tipos: medicamento, consulta, tarefa, outro.
Sê breve, claro e simpático.
""".strip()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "agendar_lembrete",
            "description": (
                "Agenda um lembrete local. hora pode ser HH:MM ou relativo "
                "(ex.: 'daqui 1 minuto', 'em 5 minutos')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string"},
                    "hora": {
                        "type": "string",
                        "description": "HH:MM ou relativo (daqui 2 minutos)",
                    },
                    "tipo": {
                        "type": "string",
                        "enum": list(db.TIPOS_VALIDOS),
                    },
                },
                "required": ["titulo", "hora"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_lembretes",
            "description": "Lista os lembretes atuais.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "confirmar_lembrete",
            "description": "Marca um lembrete como feito.",
            "parameters": {
                "type": "object",
                "properties": {"id": {"type": "integer"}},
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adiar_lembrete",
            "description": "Adia um lembrete alguns minutos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "minutos": {"type": "integer", "default": 10},
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_generos",
            "description": "Lista géneros da biblioteca de músicas local (offline).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_musicas",
            "description": "Lista músicas locais. Pode filtrar por género.",
            "parameters": {
                "type": "object",
                "properties": {
                    "genero": {
                        "type": "string",
                        "description": "Nome da pasta/género, opcional",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tocar_musica",
            "description": (
                "Toca AGORA uma música da biblioteca local. "
                "Usa sempre que o utilizador pedir para tocar/ouvir. "
                "Podes indicar id, titulo e/ou genero."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Id da faixa (ex.: metal__the-emptiness-machine-linkin-park)",
                    },
                    "titulo": {"type": "string"},
                    "genero": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pausar_musica",
            "description": "Pausa a música atual, guardando a posição para continuar depois.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "continuar_musica",
            "description": "Continua a música pausada a partir do ponto onde parou.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reiniciar_musica",
            "description": (
                "Reinicia a música atual DO COMEÇO (tempo 0). "
                "Usa quando o utilizador pedir 'do começo', 'do início', 'reinicia'."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ajustar_volume",
            "description": "Sobe ou desce o volume. delta entre -1 e 1 (ex.: -0.15 mais baixo, +0.15 mais alto).",
            "parameters": {
                "type": "object",
                "properties": {
                    "delta": {
                        "type": "number",
                        "description": "Variação do volume (ex.: -0.15 ou 0.15)",
                    }
                },
                "required": ["delta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "definir_volume",
            "description": "Define o volume absoluto entre 0 (mudo) e 1 (máximo).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nivel": {
                        "type": "number",
                        "description": "0.0 a 1.0",
                    }
                },
                "required": ["nivel"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "guardar_preferencia",
            "description": (
                "Guarda uma preferência da pessoa (nome, gosto musical, rotina, etc.). "
                "Usa quando disser o nome ou algo que queira lembrar."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "chave": {
                        "type": "string",
                        "description": "Ex.: nome, genero_favorito, cidade",
                    },
                    "valor": {"type": "string"},
                },
                "required": ["chave", "valor"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "obter_perfil",
            "description": "Obtém o perfil/preferências já guardadas da pessoa.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


class LlmError(RuntimeError):
    pass


def estado() -> dict[str, Any]:
    try:
        data = _http_json(f"{OLLAMA_URL}/api/tags", method="GET", payload=None, timeout=3)
        nomes = [m.get("name", "") for m in data.get("models", [])]
        return {
            "ok": True,
            "modelo": DEFAULT_MODEL,
            "modelo_disponivel": DEFAULT_MODEL in nomes
            or any(n.startswith("qwen2.5:3b") for n in nomes),
            "modelos": nomes,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "modelo": DEFAULT_MODEL,
            "modelo_disponivel": False,
            "erro": str(exc),
        }


def _http_json(
    url: str,
    method: str = "POST",
    payload: dict | None = None,
    timeout: int = TIMEOUT_S,
) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data is not None else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise LlmError(
            "Ollama indisponível. Confirma que está a correr em http://127.0.0.1:11434"
        ) from exc
    except TimeoutError as exc:
        raise LlmError("A LLM demorou demasiado. Tenta outra vez.") from exc


def _contexto() -> str:
    lembretes = db.listar()
    if lembretes:
        linhas_l = [
            f"- #{i.id} {i.hora} [{i.tipo}] {i.titulo} ({i.estado})"
            for i in lembretes[:12]
        ]
        bloco_l = "Lembretes:\n" + "\n".join(linhas_l)
    else:
        bloco_l = "Lembretes: (nenhum)"

    generos = music.listar_generos()
    if generos:
        linhas_g = [f"- {g['genero']} ({g['quantidade']})" for g in generos]
        bloco_g = "Géneros musicais locais:\n" + "\n".join(linhas_g)
    else:
        bloco_g = "Géneros musicais locais: (biblioteca vazia)"

    return f"{db.perfil_texto()}\n\n{bloco_l}\n\n{bloco_g}"


def _numero_de_texto(token: str) -> int | None:
    token = token.lower().strip()
    if token.isdigit():
        return int(token)
    return _NUM_PALAVRAS.get(token)


def _unidade_para_delta(unidade: str, quantidade: int) -> timedelta:
    u = unidade.lower().strip()
    if u in ("s", "seg", "segs", "segundo", "segundos"):
        return timedelta(seconds=quantidade)
    if u in ("m", "min", "mins", "minuto", "minutos"):
        return timedelta(minutes=quantidade)
    if u in ("h", "hr", "hrs", "hora", "horas"):
        return timedelta(hours=quantidade)
    raise ValueError(f"Unidade de tempo desconhecida: {unidade}")


def interpretar_quando(texto: str, agora: datetime | None = None) -> datetime | None:
    """Interpreta HH:MM ou tempos relativos em português ('daqui 1 minuto')."""
    agora = agora or datetime.now()
    t = (texto or "").lower().strip()
    if not t:
        return None

    if re.search(r"\bmeia[- ]?hora\b", t):
        return agora + timedelta(minutes=30)

    m = re.search(r"\b(\d{1,2}):(\d{2})\b", t)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mi <= 59:
            alvo = agora.replace(hour=h, minute=mi, second=0, microsecond=0)
            if alvo <= agora:
                alvo += timedelta(days=1)
            return alvo

    rel = re.search(
        r"(?:daqui(?:\s+a)?|em)\s+(\d+|[a-zà-ÿ]+)\s*"
        r"(s|seg|segs|segundo|segundos|m|min|mins|minuto|minutos|h|hr|hrs|hora|horas)\b",
        t,
        flags=re.IGNORECASE,
    )
    if rel:
        n = _numero_de_texto(rel.group(1))
        if n is not None and n > 0:
            return agora + _unidade_para_delta(rel.group(2), n)

    # "daqui a um minuto" sem dígitos já coberto; "1 min" solto
    curto = re.search(
        r"\b(\d+)\s*(s|seg|segs|segundo|segundos|m|min|mins|minuto|minutos|h|hr|hrs|hora|horas)\b",
        t,
    )
    if curto and re.search(r"\b(daqui|em|depois|passar)\b", t):
        n = int(curto.group(1))
        if n > 0:
            return agora + _unidade_para_delta(curto.group(2), n)

    return None


def _pedido_lembrete(mensagem: str) -> bool:
    t = mensagem.lower()
    if re.search(
        r"\b(lembra(?:-me)?|lembrar(?:-me)?|lembrete|agenda(?:r)?|avisa(?:-me)?|avisar)\b",
        t,
    ):
        return True
    # "me lembra de ..." / "não me deixes esquecer"
    if re.search(r"\bme\s+lembra\b|\bn[aã]o\s+me\s+deixes\s+esquecer\b", t):
        return True
    return False


def _extrair_titulo_lembrete(mensagem: str) -> str:
    t = mensagem.strip()
    limpo = re.sub(
        r"(?:daqui(?:\s+a)?|em)\s+(?:\d+|[a-zà-ÿ]+)\s*"
        r"(?:s|seg|segs|segundo|segundos|m|min|mins|minuto|minutos|h|hr|hrs|hora|horas)\b",
        " ",
        t,
        flags=re.IGNORECASE,
    )
    limpo = re.sub(r"\bmeia[- ]?hora\b", " ", limpo, flags=re.IGNORECASE)
    limpo = re.sub(r"\b(?:às|as|a)\s*\d{1,2}:\d{2}\b", " ", limpo, flags=re.IGNORECASE)
    limpo = re.sub(r"\b\d{1,2}:\d{2}\b", " ", limpo)
    limpo = re.sub(
        r"\b(?:por\s+favor|pf|pfv)\b",
        " ",
        limpo,
        flags=re.IGNORECASE,
    )
    limpo = re.sub(
        r"\b(?:me\s+)?lembra(?:-me)?(?:\s+de)?|"
        r"lembrar(?:-me)?(?:\s+de)?|"
        r"faz(?:er)?\s+(?:um\s+)?lembrete(?:\s+de)?|"
        r"cria(?:r)?\s+(?:um\s+)?lembrete(?:\s+de)?|"
        r"agenda(?:r)?(?:\s+um\s+lembrete)?(?:\s+de)?|"
        r"avisa(?:-me)?(?:\s+de)?|"
        r"n[aã]o\s+me\s+deixes\s+esquecer(?:\s+de)?\b",
        " ",
        limpo,
        flags=re.IGNORECASE,
    )
    limpo = " ".join(limpo.split()).strip(" .,!;:")
    limpo = re.sub(r"^(?:para|pra|de|do|da|o|a)\s+", "", limpo, flags=re.IGNORECASE)
    limpo = limpo.strip(" .,!;:")
    if not limpo:
        return "Lembrete"
    return limpo[:80]


def _tipo_lembrete(mensagem: str) -> str:
    t = mensagem.lower()
    if re.search(r"medicamento|comprimido|rem[eé]dio|p[ií]lula", t):
        return "medicamento"
    if re.search(r"consulta|m[eé]dico|dentista|hospital", t):
        return "consulta"
    return "tarefa"


def _fallback_agendar(mensagem: str) -> dict[str, Any] | None:
    """Agenda mesmo se a LLM pequena não chamar a tool ou falhar a hora."""
    if not _pedido_lembrete(mensagem):
        return None
    quando = interpretar_quando(mensagem)
    if quando is None:
        return {
            "ok": False,
            "acao": "agendar",
            "erro": (
                "Não percebi quando. Diz por exemplo "
                "“daqui 1 minuto” ou “às 18:00”."
            ),
            "fallback": True,
        }
    titulo = _extrair_titulo_lembrete(mensagem)
    try:
        item = db.adicionar_em(titulo, quando, _tipo_lembrete(mensagem))
    except ValueError as exc:
        return {"ok": False, "acao": "agendar", "erro": str(exc), "fallback": True}
    return {
        "ok": True,
        "acao": "agendar",
        "lembrete": {
            "id": item.id,
            "titulo": item.titulo,
            "hora": item.hora,
            "tipo": item.tipo,
            "proximo_em": item.proximo_em,
        },
        "fallback": True,
    }


def _executar_ferramenta(nome: str, args: dict[str, Any]) -> dict[str, Any]:
    if nome == "agendar_lembrete":
        titulo = str(args.get("titulo", "")).strip()
        hora_raw = str(args.get("hora", "")).strip()
        tipo = str(args.get("tipo", "tarefa") or "tarefa")
        quando = interpretar_quando(hora_raw) or interpretar_quando(
            f"{titulo} {hora_raw}".strip()
        )
        if quando is not None:
            item = db.adicionar_em(titulo or "Lembrete", quando, tipo)
        else:
            item = db.adicionar(titulo, hora_raw, tipo)
        return {
            "ok": True,
            "acao": "agendar",
            "lembrete": {
                "id": item.id,
                "titulo": item.titulo,
                "hora": item.hora,
                "tipo": item.tipo,
                "proximo_em": item.proximo_em,
            },
        }
    if nome == "listar_lembretes":
        itens = db.listar()
        return {
            "ok": True,
            "acao": "listar",
            "lembretes": [
                {
                    "id": i.id,
                    "titulo": i.titulo,
                    "hora": i.hora,
                    "tipo": i.tipo,
                    "estado": i.estado,
                    "proximo_em": i.proximo_em,
                }
                for i in itens
            ],
        }
    if nome == "confirmar_lembrete":
        item = db.confirmar(int(args["id"]))
        return {
            "ok": True,
            "acao": "confirmar",
            "lembrete": {"id": item.id, "titulo": item.titulo, "estado": item.estado},
        }
    if nome == "adiar_lembrete":
        minutos = int(args.get("minutos", 10) or 10)
        item = db.adiar(int(args["id"]), minutos)
        return {
            "ok": True,
            "acao": "adiar",
            "lembrete": {
                "id": item.id,
                "titulo": item.titulo,
                "estado": item.estado,
                "proximo_em": item.proximo_em,
            },
        }
    if nome == "listar_generos":
        return {"ok": True, "acao": "listar_generos", "generos": music.listar_generos()}
    if nome == "listar_musicas":
        genero = args.get("genero")
        faixas = music.listar_por_genero(str(genero) if genero else None)
        return {
            "ok": True,
            "acao": "listar_musicas",
            "musicas": [f.to_dict() for f in faixas],
        }
    if nome == "tocar_musica":
        faixa_id = args.get("id")
        titulo = args.get("titulo")
        genero = args.get("genero")
        if faixa_id:
            faixa = music.obter(str(faixa_id))
        else:
            faixa = music.escolher_para_tocar(
                str(titulo) if titulo else None,
                str(genero) if genero else None,
            )
        return {
            "ok": True,
            "acao": "tocar",
            "musica": faixa.to_dict(),
        }
    if nome == "pausar_musica":
        return {"ok": True, "acao": "pausar"}
    if nome == "continuar_musica":
        return {"ok": True, "acao": "continuar"}
    if nome == "reiniciar_musica":
        return {"ok": True, "acao": "reiniciar"}
    if nome == "ajustar_volume":
        delta = float(args.get("delta", 0))
        delta = max(-1.0, min(1.0, delta))
        return {"ok": True, "acao": "volume_delta", "delta": delta}
    if nome == "definir_volume":
        nivel = float(args.get("nivel", 0.7))
        nivel = max(0.0, min(1.0, nivel))
        return {"ok": True, "acao": "volume", "nivel": nivel}
    if nome == "guardar_preferencia":
        pref = db.guardar_preferencia(str(args.get("chave", "")), str(args.get("valor", "")))
        return {"ok": True, "acao": "guardar_preferencia", "preferencia": pref}
    if nome == "obter_perfil":
        return {"ok": True, "acao": "obter_perfil", "perfil": db.obter_perfil()}
    return {"ok": False, "erro": f"Ferramenta desconhecida: {nome}"}


def _chat_ollama(messages: list[dict[str, Any]], usar_tools: bool = True) -> dict:
    payload: dict[str, Any] = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    if usar_tools:
        payload["tools"] = TOOLS
    return _http_json(f"{OLLAMA_URL}/api/chat", payload=payload)


def _parse_args(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return {}
        return json.loads(raw)
    return {}


def _pedido_reiniciar(mensagem: str) -> bool:
    t = mensagem.lower().strip()
    padroes = (
        r"do come[cç]o",
        r"do in[ií]cio",
        r"desde o come[cç]o",
        r"desde o in[ií]cio",
        r"\breinicia",
        r"\breiniciar\b",
        r"\brecome[cç]a",
        r"\brecome[cç]ar\b",
        r"outra vez do come[cç]o",
        r"play do come[cç]o",
        r"toca do come[cç]o",
        r"volta .* come[cç]o",
        r"volta .* in[ií]cio",
    )
    return any(re.search(p, t) for p in padroes)


def _pedido_pausar(mensagem: str) -> bool:
    """Pausa pura — se também pede reiniciar/do começo, não trata só como pausa."""
    if _pedido_reiniciar(mensagem):
        return False
    t = mensagem.lower().strip()
    padroes = (
        r"\bpausa(?:r)?\b",
        r"\bpause\b",
        r"\bstop\b",
        r"podes?\s+pausar",
        r"pode(?:s)?\s+parar",
        r"mete(?:r)?\s+em\s+pausa",
        r"p[oõ]e(?:r)?\s+em\s+pausa",
        r"interrompe(?:r)?(?:\s+a\s+m[uú]sica)?",
        r"\bpara(?:\s+a)?\s+m[uú]sica\b",
        r"\bpara(?:\s+a)?\s+musica\b",
        r"\bpara\s+de\s+tocar\b",
        r"\bpare(?:\s+a)?\s+m[uú]sica\b",
        r"\bpare(?:\s+a)?\s+musica\b",
        r"\bpara\s+o\s+som\b",
        r"sil[eê]ncio\s+(?:na\s+)?m[uú]sica",
        r"cala\s+a\s+m[uú]sica",
    )
    return any(re.search(p, t) for p in padroes)


def _pedido_continuar(mensagem: str) -> bool:
    # "volta a tocar do começo" NÃO é continuar — é reiniciar
    if _pedido_reiniciar(mensagem):
        return False
    t = mensagem.lower().strip()
    padroes = (
        r"\bcontinua(?:r)?\b",
        r"\bretoma(?:r)?\b",
        r"\bresume\b",
        r"\bdespausa(?:r)?\b",
        r"volta\s+a\s+tocar",
        r"volta\s+tocar",
        r"podes?\s+continuar",
        r"segue(?:\s+a\s+m[uú]sica)?",
        r"recome[cç]a(?:r)?\s+de\s+onde\s+parou",
    )
    return any(re.search(p, t) for p in padroes)


def _pedido_volume(mensagem: str) -> dict[str, Any] | None:
    t = mensagem.lower().strip()
    if re.search(
        r"mais baixo|abaixa|diminu|baixa o volume|volume baixo|menos volume|"
        r"podes?\s+baixar|mais\s+baixinho|abaixa\s+(?:um\s+)?pouco",
        t,
    ):
        return {"ok": True, "acao": "volume_delta", "delta": -0.15, "fallback": True}
    if re.search(
        r"mais alto|aumenta|sobe o volume|volume alto|mais volume|"
        r"podes?\s+aumentar|mais\s+forte",
        t,
    ):
        return {"ok": True, "acao": "volume_delta", "delta": 0.15, "fallback": True}
    if re.search(r"\bmudo\b|sem som|mute\b", t):
        return {"ok": True, "acao": "volume", "nivel": 0.0, "fallback": True}
    m = re.search(r"volume\s*(?:em|a|para)?\s*(\d{1,3})\s*%?", t)
    if m:
        pct = max(0, min(100, int(m.group(1))))
        return {"ok": True, "acao": "volume", "nivel": pct / 100.0, "fallback": True}
    return None


def _pedido_tocar(mensagem: str) -> bool:
    if (
        _pedido_pausar(mensagem)
        or _pedido_continuar(mensagem)
        or _pedido_reiniciar(mensagem)
        or _pedido_volume(mensagem) is not None
    ):
        return False
    t = mensagem.lower()
    palavras = (
        "toca",
        "tocar",
        "touca",
        "ouvir",
        "ouve",
        "quero ouvir",
        "põe",
        "poe",
        "play",
        "reproduz",
        "mete música",
        "mete musica",
        "troca",
        "trocar",
        "muda",
        "mudar",
        "passa para",
        "passar para",
        "muda para",
        "mudar para",
        "troca para",
        "trocar para",
    )
    if any(p in t for p in palavras):
        return True
    # "música de jazz" / "põe jazz" sem verbo explícito de play
    if _extrair_genero(t) and re.search(
        r"\b(m[uú]sica|musica|som|faixa|g[eé]nero|genero)\b", t
    ):
        return True
    return False


def _extrair_genero(mensagem: str) -> str | None:
    t = mensagem.lower()
    # ids tipo metal__...
    for g in music.GENEROS_CONHECIDOS:
        if g in t or music.nome_genero(g).lower() in t:
            return g
    return None


def _extrair_titulo(mensagem: str, genero: str | None) -> str | None:
    t = mensagem.lower()
    # Se mencionar id completo da faixa
    for faixa in music.listar_biblioteca():
        if faixa.id.lower() in t or faixa.titulo.lower() in t:
            return faixa.titulo
    limpo = t
    ruidos = (
        "quero ouvir",
        "por favor",
        "uma música",
        "uma musica",
        "toca",
        "tocar",
        "troca",
        "trocar",
        "muda",
        "mudar",
        "passa",
        "passar",
        "para",
        "música",
        "musica",
        "de",
        "do",
        "da",
        "me",
    )
    for ruido in ruidos:
        limpo = re.sub(rf"\b{re.escape(ruido)}\b", " ", limpo, flags=re.IGNORECASE)
    if genero:
        limpo = re.sub(rf"\b{re.escape(genero)}\b", " ", limpo, flags=re.IGNORECASE)
        nome_g = music.nome_genero(genero).lower()
        limpo = re.sub(rf"\b{re.escape(nome_g)}\b", " ", limpo, flags=re.IGNORECASE)
    limpo = " ".join(limpo.split()).strip(" .,!;:")
    # Lixo residual curto não é título (evita "j zz" / "x")
    if len(limpo) < 3:
        return None
    return limpo


def _fallback_tocar(mensagem: str) -> dict[str, Any] | None:
    """Se a LLM não chamou a tool, tenta tocar na mesma."""
    if not _pedido_tocar(mensagem):
        return None
    genero = _extrair_genero(mensagem)
    titulo = _extrair_titulo(mensagem, genero)
    try:
        if titulo and "__" in titulo:
            faixa = music.obter(titulo)
        elif genero and not titulo:
            faixa = music.escolher_para_tocar(None, genero)
        else:
            try:
                faixa = music.escolher_para_tocar(titulo, genero)
            except LookupError:
                if not genero:
                    raise
                faixa = music.escolher_para_tocar(None, genero)
        return {
            "ok": True,
            "acao": "tocar",
            "musica": faixa.to_dict(),
            "fallback": True,
        }
    except LookupError as exc:
        return {"ok": False, "acao": "tocar", "erro": str(exc), "fallback": True}


def _pedido_historia(mensagem: str) -> bool:
    t = mensagem.lower().strip()
    return any(
        p in t
        for p in (
            "conta uma história",
            "conta uma historia",
            "conta-me uma história",
            "conta-me uma historia",
            "contame uma historia",
            "história curta",
            "historia curta",
            "contar uma história",
            "contar uma historia",
        )
    )


def _fallback_nome(mensagem: str) -> dict[str, Any] | None:
    t = mensagem.strip()
    m = re.search(
        r"(?:chamo-me|chamo me|o meu nome [eé]|meu nome [eé]|sou o|sou a)\s+([A-Za-zÀ-ÿ][\wÀ-ÿ\- ]{1,40})",
        t,
        flags=re.IGNORECASE,
    )
    if not m:
        return None
    nome = m.group(1).strip(" .,!")
    if not nome:
        return None
    pref = db.guardar_preferencia("nome", nome)
    return {"ok": True, "acao": "guardar_preferencia", "preferencia": pref, "fallback": True}


def conversar(mensagem: str, historico: list[dict[str, str]] | None = None) -> dict[str, Any]:
    mensagem = (mensagem or "").strip()
    if not mensagem:
        raise ValueError("A mensagem não pode estar vazia.")

    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Inclui lista curta de músicas para o modelo não inventar nomes
    faixas = music.listar_biblioteca()
    if faixas:
        linhas_m = [
            f"- {f.id} | {f.titulo} [{f.genero}]" for f in faixas[:40]
        ]
        bloco_m = "Músicas disponíveis:\n" + "\n".join(linhas_m)
    else:
        bloco_m = "Músicas disponíveis: (nenhuma)"
    system = f"{SYSTEM_PROMPT}\n\nAgora local: {agora}\n{_contexto()}\n\n{bloco_m}"
    if _pedido_historia(mensagem):
        system += (
            "\n\nMODO HISTÓRIA: responde já com uma história curta original "
            "(6–10 frases), calma, em português de Portugal. Sem tools."
        )

    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    hist = historico if historico is not None else db.historico_para_llm(10)
    for item in hist[-10:]:
        role = item.get("role")
        content = (item.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": mensagem})

    acoes: list[dict[str, Any]] = []
    data = _chat_ollama(messages, usar_tools=True)
    msg = data.get("message") or {}
    tool_calls = msg.get("tool_calls") or []

    if tool_calls:
        messages.append(msg)
        for call in tool_calls:
            fn = call.get("function") or {}
            nome = fn.get("name") or ""
            try:
                args = _parse_args(fn.get("arguments"))
                resultado = _executar_ferramenta(nome, args)
            except (
                ValueError,
                LookupError,
                json.JSONDecodeError,
                KeyError,
                TypeError,
            ) as exc:
                resultado = {"ok": False, "acao": nome, "erro": str(exc)}
            acoes.append(resultado)
            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(resultado, ensure_ascii=False),
                }
            )

        data2 = _chat_ollama(messages, usar_tools=False)
        msg = data2.get("message") or {}

    resposta = (msg.get("content") or "").strip()
    if not resposta:
        if any(a.get("ok") for a in acoes):
            resposta = "Feito."
        else:
            resposta = "Percebi, mas não consegui formular a resposta. Podes repetir?"

    player = None
    player_control = None
    volume_delta = None
    volume_nivel = None
    for acao in acoes:
        if not acao.get("ok"):
            continue
        if acao.get("acao") == "tocar" and acao.get("musica"):
            player = acao["musica"]
        elif acao.get("acao") in ("pausar", "continuar", "reiniciar"):
            player_control = acao["acao"]
        elif acao.get("acao") == "volume_delta":
            volume_delta = float(acao.get("delta", 0))
        elif acao.get("acao") == "volume":
            volume_nivel = float(acao.get("nivel", 0.7))

    # Prioridade: reiniciar > pausar/continuar > volume > tocar
    if player_control != "reiniciar" and _pedido_reiniciar(mensagem):
        acoes.append({"ok": True, "acao": "reiniciar", "fallback": True})
        player_control = "reiniciar"
        resposta = "A reiniciar a música do começo."
    elif player_control is None and _pedido_pausar(mensagem):
        acoes.append({"ok": True, "acao": "pausar", "fallback": True})
        player_control = "pausar"
        resposta = "Música em pausa. Diz “continua” quando quiseres retomar."
    elif player_control is None and _pedido_continuar(mensagem):
        acoes.append({"ok": True, "acao": "continuar", "fallback": True})
        player_control = "continuar"
        resposta = "A continuar a música de onde parou."
    elif volume_delta is None and volume_nivel is None:
        vol = _pedido_volume(mensagem)
        if vol is not None:
            acoes.append(vol)
            if vol["acao"] == "volume_delta":
                volume_delta = float(vol["delta"])
                sentido = "mais baixo" if volume_delta < 0 else "mais alto"
                resposta = f"Volume {sentido}."
            else:
                volume_nivel = float(vol["nivel"])
                resposta = f"Volume em {int(volume_nivel * 100)}%."
        elif player is None:
            fb = _fallback_tocar(mensagem)
            if fb is not None:
                acoes.append(fb)
                if fb.get("ok") and fb.get("musica"):
                    player = fb["musica"]
                    resposta = (
                        f"A tocar: {player['titulo']} "
                        f"({music.nome_genero(player['genero'])})."
                    )
                elif not fb.get("ok"):
                    resposta = fb.get("erro") or (
                        "Não encontrei essa música na biblioteca local."
                    )

    if not any(a.get("acao") == "guardar_preferencia" and a.get("ok") for a in acoes):
        fb_nome = _fallback_nome(mensagem)
        if fb_nome is not None:
            acoes.append(fb_nome)
            nome = fb_nome["preferencia"]["valor"]
            if "guardar_preferencia" in resposta.lower() or len(resposta) < 8:
                resposta = f"Prazer em conhecer-te, {nome}. Vou lembrar-me do teu nome."

    agendou = any(a.get("acao") == "agendar" and a.get("ok") for a in acoes)
    if not agendou and _pedido_lembrete(mensagem):
        fb_ag = _fallback_agendar(mensagem)
        if fb_ag is not None:
            acoes.append(fb_ag)
            if fb_ag.get("ok") and fb_ag.get("lembrete"):
                lem = fb_ag["lembrete"]
                resposta = (
                    f"Lembrete agendado: {lem['titulo']} às {lem['hora']} "
                    f"(dispara em {lem['proximo_em'].replace('T', ' ')})."
                )
            else:
                resposta = fb_ag.get("erro") or resposta

    # Evita respostas que ensinam nomes de tools
    low = resposta.lower()
    if any(
        x in low
        for x in (
            "tocar_musica",
            "pausar_musica",
            "continuar_musica",
            "reiniciar_musica",
            "ajustar_volume",
            "definir_volume",
            "guardar_preferencia",
            "obter_perfil",
        )
    ):
        if player_control == "pausar":
            resposta = "Música em pausa. Diz “continua” quando quiseres retomar."
        elif player_control == "continuar":
            resposta = "A continuar a música de onde parou."
        elif player_control == "reiniciar":
            resposta = "A reiniciar a música do começo."
        elif volume_delta is not None:
            sentido = "mais baixo" if volume_delta < 0 else "mais alto"
            resposta = f"Volume {sentido}."
        elif volume_nivel is not None:
            resposta = f"Volume em {int(volume_nivel * 100)}%."
        elif player:
            resposta = (
                f"A tocar: {player['titulo']} "
                f"({music.nome_genero(player['genero'])})."
            )
        elif any(a.get("acao") == "guardar_preferencia" and a.get("ok") for a in acoes):
            pref = next(
                a["preferencia"]
                for a in acoes
                if a.get("acao") == "guardar_preferencia" and a.get("ok")
            )
            resposta = f"Guardei: {pref['chave']} = {pref['valor']}."

    try:
        db.adicionar_mensagem("user", mensagem)
        db.adicionar_mensagem("assistant", resposta)
    except ValueError:
        pass

    return {
        "resposta": resposta,
        "acoes": acoes,
        "player": player,
        "player_control": player_control,
        "volume_delta": volume_delta,
        "volume_nivel": volume_nivel,
        "perfil": db.obter_perfil(),
        "modelo": DEFAULT_MODEL,
        "ollama": True,
    }


def frase_aviso(titulo: str, tipo: str, hora: str) -> str:
    prompt = (
        "Escreve UMA frase curta em português de Portugal para avisar um lembrete. "
        "Sem diagnósticos. Sem aspas. Máximo 25 palavras.\n"
        f"Lembrete: {titulo}. Tipo: {tipo}. Hora: {hora}."
    )
    try:
        data = _chat_ollama(
            [
                {
                    "role": "system",
                    "content": "És o RIC. Respostas muito curtas e claras.",
                },
                {"role": "user", "content": prompt},
            ],
            usar_tools=False,
        )
        texto = ((data.get("message") or {}).get("content") or "").strip()
        texto = texto.strip(" \"'")
        return texto or f"É a hora: {titulo}"
    except Exception:  # noqa: BLE001
        return f"É a hora: {titulo}"
