from dataclasses import dataclass

@dataclass
class Skill:
    id: str                     # slug (ej. "seguridad_alimentaria")
    name: str                   # nombre legible
    level: int                  # 0..3
    requires: list[str] = None  # nombre de habilidades requeridas
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "requires": self.requires,
            "description": self.description
        }
    