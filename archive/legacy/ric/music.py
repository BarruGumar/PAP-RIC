from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

MUSIC_DIR = Path(__file__).resolve().parent / "musica"
EXTENSOES = {".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"}

# Pastas = géneros. Chave = nome da pasta; valor = nome amigável para UI/LLM.
GENEROS_CONHECIDOS = {
    "pop": "Pop",
    "rock": "Rock",
    "hiphop": "Hip-Hop",
    "eletronica": "Eletrónica",
    "jazz": "Jazz",
    "blues": "Blues",
    "classica": "Clássica",
    "folk": "Folk",
    "country": "Country",
    "reggae": "Reggae",
    "metal": "Metal",
    "rb_soul": "R&B / Soul",
    "latina": "Latina",
    "fado": "Fado",
    "relaxamento": "Relaxamento",
    "infantil": "Infantil",
    "gospel": "Gospel",
    "soundtrack": "Bandas sonoras",
}


@dataclass(frozen=True)
class Faixa:
    id: str
    titulo: str
    genero: str
    ficheiro: str
    caminho: Path

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "genero": self.genero,
            "ficheiro": self.ficheiro,
            "url": f"/api/musica/{self.id}/stream",
        }


def _slug(texto: str) -> str:
    texto = texto.strip().lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto, flags=re.IGNORECASE)
    return texto.strip("-") or "faixa"


def nome_genero(pasta: str) -> str:
    return GENEROS_CONHECIDOS.get(pasta, pasta.replace("_", " ").title())


def garantir_pastas() -> None:
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    for genero in GENEROS_CONHECIDOS:
        pasta = MUSIC_DIR / genero
        pasta.mkdir(parents=True, exist_ok=True)
        # Mantém pasta no git mesmo sem áudio
        if not any(pasta.iterdir()):
            (pasta / ".gitkeep").touch()


def listar_biblioteca() -> list[Faixa]:
    garantir_pastas()
    faixas: list[Faixa] = []
    for pasta in sorted(MUSIC_DIR.iterdir()):
        if not pasta.is_dir() or pasta.name.startswith("_"):
            continue
        genero = pasta.name
        for ficheiro in sorted(pasta.iterdir()):
            if not ficheiro.is_file():
                continue
            if ficheiro.suffix.lower() not in EXTENSOES:
                continue
            if ficheiro.name.startswith("."):
                continue
            titulo = ficheiro.stem.replace("_", " ").replace("-", " ").strip()
            faixa_id = f"{_slug(genero)}__{_slug(ficheiro.stem)}"
            faixas.append(
                Faixa(
                    id=faixa_id,
                    titulo=titulo.title(),
                    genero=genero,
                    ficheiro=ficheiro.name,
                    caminho=ficheiro.resolve(),
                )
            )
    return faixas


def listar_generos() -> list[dict]:
    contagem: dict[str, int] = {}
    for faixa in listar_biblioteca():
        contagem[faixa.genero] = contagem.get(faixa.genero, 0) + 1
    # Inclui pastas vazias para o utilizador saber onde pôr ficheiros
    garantir_pastas()
    for pasta in MUSIC_DIR.iterdir():
        if pasta.is_dir() and not pasta.name.startswith(("_", ".")):
            contagem.setdefault(pasta.name, 0)
    return [
        {
            "genero": nome,
            "nome": nome_genero(nome),
            "quantidade": contagem[nome],
        }
        for nome in sorted(contagem, key=lambda g: nome_genero(g).lower())
    ]


def listar_por_genero(genero: str | None = None) -> list[Faixa]:
    faixas = listar_biblioteca()
    if not genero:
        return faixas
    g = genero.strip().lower()
    return [f for f in faixas if f.genero.lower() == g]


def obter(faixa_id: str) -> Faixa:
    for faixa in listar_biblioteca():
        if faixa.id == faixa_id:
            return faixa
    raise LookupError(f"Música '{faixa_id}' não encontrada na biblioteca local.")


def procurar(texto: str, genero: str | None = None) -> list[Faixa]:
    termo = (texto or "").strip().lower()
    candidatos = listar_por_genero(genero)
    if not termo:
        return candidatos
    return [
        f
        for f in candidatos
        if termo in f.titulo.lower()
        or termo in f.ficheiro.lower()
        or termo in f.genero.lower()
        or termo in f.id.lower()
    ]


def escolher_para_tocar(titulo: str | None = None, genero: str | None = None) -> Faixa:
    if titulo:
        # Aceita id completo (ex.: metal__the-emptiness-machine-linkin-park)
        try:
            if "__" in titulo:
                return obter(titulo.strip())
        except LookupError:
            pass
        achados = procurar(titulo, genero)
        if len(achados) == 1:
            return achados[0]
        if len(achados) > 1:
            # preferência: título mais curto / match mais próximo
            achados = sorted(achados, key=lambda f: len(f.titulo))
            return achados[0]
        raise LookupError(
            "Não encontrei essa música. Usa listar_musicas ou listar_generos."
        )

    faixas = listar_por_genero(genero)
    if not faixas:
        if genero:
            raise LookupError(f"Não há músicas no género '{genero}'.")
        raise LookupError("A biblioteca local está vazia.")
    return faixas[0]
