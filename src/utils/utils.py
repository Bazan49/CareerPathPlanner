from typing import Set, Dict, List
from src.model.skill import Skill
from src.model.course import Course

def skill_ids(skills: List[Skill]) -> Set[str]:
    """Devuelve el conjunto de IDs de las habilidades."""
    return {s.id for s in skills}

def course_dict(courses: List[Course]) -> Dict[str, Course]:
    """Devuelve un diccionario {course.name: course}."""
    return {c.name: c for c in courses}

def skill_dict(skills: List[Skill]) -> Dict[str, Skill]:
    """Devuelve un diccionario {skill.id: skill}."""
    return {s.id: s for s in skills}
