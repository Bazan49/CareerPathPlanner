"""
Carga de datasets de habilidades y cursos desde archivos JSON generados por build_dataset_from_knowledge.py.
"""

import json
from pathlib import Path
from typing import List
from src.model.skill import Skill
from src.model.course import Course, CourseLevel
from src.utils.logger import default_logger

class DatasetLoader:
    def __init__(self, dataset_path: Path):
        self.dataset_path = Path(dataset_path).resolve()
        self.skills_file = self.dataset_path.joinpath("skills.json")
        self.courses_file = self.dataset_path.joinpath("courses.json")

        if not self.skills_file.exists():
            default_logger.error(f"No se encuentra {self.skills_file}")
            raise FileNotFoundError(f"No se encuentra {self.skills_file}")
        if not self.courses_file.exists():
            default_logger.error(f"No se encuentra {self.courses_file}")
            raise FileNotFoundError(f"No se encuentra {self.courses_file}")

    def load_skills(self) -> List[Skill]:
        default_logger.info(f"Cargando habilidades desde {self.skills_file}")
        with open(self.skills_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        skills = []
        for s in data["skills"]:
            skill = Skill(
                id=s["id"],
                name=s["name"],
                level=s["level"],
                requires=s.get("requires", []),
                description=s.get("description", "")
            )
            skills.append(skill)
        default_logger.info(f"Se cargaron {len(skills)} habilidades")
        return skills

    def load_courses(self) -> List[Course]:
        default_logger.info(f"Cargando cursos desde {self.courses_file}")
        with open(self.courses_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        courses = []
        for c in data["courses"]:
            level_str = c.get("level", "Beginner")   
            try:
                level_enum = CourseLevel[level_str.upper()]
            except KeyError:
                default_logger.warning(f"Nivel desconocido '{level_str}' para {c['id']}, se asigna Beginner")
                level_enum = CourseLevel.BEGINNER

            course = Course(
                id=c["id"],
                name=c["name"],
                preconditions=set(c["preconditions"]),
                add_effects=set(c["adds"]),
                level=level_enum,
                duration=c["duration"],
                difficulty_score=c["difficulty_score"],
                description=c.get("description", "")
            )
            courses.append(course)
        default_logger.info(f"Se cargaron {len(courses)} cursos")
        return courses
    