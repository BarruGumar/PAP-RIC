from __future__ import annotations

from dataclasses import dataclass


TIPOS_VALIDOS = ("medicamento", "consulta", "tarefa", "outro")
ESTADOS_ATIVOS = ("pendente", "adiado", "disparado")


@dataclass(frozen=True)
class Reminder:
    id: int
    titulo: str
    tipo: str
    critico: bool
    hora: str
    diario: bool
    estado: str
    proximo_em: str
    criado_por: str
    avisos_feitos: int
    criado_em: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "tipo": self.tipo,
            "critico": self.critico,
            "hora": self.hora,
            "diario": self.diario,
            "estado": self.estado,
            "proximo_em": self.proximo_em,
            "criado_por": self.criado_por,
            "avisos_feitos": self.avisos_feitos,
            "criado_em": self.criado_em,
        }
