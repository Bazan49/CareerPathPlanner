from dataclasses import dataclass
from typing import Set, Dict, Any
from enum import Enum

class CourseLevel(Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"

@dataclass
class Course:
    id: str
    name: str
    preconditions: Set[str]
    add_effects: Set[str]
    level: CourseLevel
    duration: int               # horas            
    difficulty_score: float     # 0..1
    description: str = ""

    def is_applicable(self, state: Set[str]) -> bool:
        return self.preconditions.issubset(state)

    def apply(self, state: Set[str]) -> Set[str]:
        if not self.is_applicable(state):
            raise ValueError(f"Course {self.id} not applicable in state {state}")
        return state.union(self.add_effects)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario listo para serialización JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "preconditions": sorted(list(self.preconditions)),   
            "adds": sorted(list(self.add_effects)),
            "level": self.level.value,
            "duration": self.duration,
            "difficulty_score": self.difficulty_score,
            "description": self.description
        }
    