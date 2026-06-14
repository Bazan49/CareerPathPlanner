"""
Módulo STRIPS para planificación clásica.
"""

from typing import Optional, Set, List
from src.model.course import Course

class STRIPSProblem:
    """
    Problema de planificación STRIPS.

    Atributos:
        initial (Set[str]): Estado inicial (conjunto de habilidades verdaderas).
        goal (Set[str]): Estado objetivo (habilidades que deben ser verdaderas al final).
        actions (List[Course]): Lista de acciones disponibles.
        all_skills (Set[str]): Conjunto de todas las habilidades posibles.
            Si no se proporciona, se calcula automáticamente a partir del estado inicial,
            objetivo y acciones.
    """
    def __init__(self, initial_state: Set[str], goal_state: Set[str], actions: List[Course],
                 all_skills: Optional[Set[str]] = None):
        self.initial = initial_state
        self.goal = goal_state
        self.actions = actions
        if all_skills is None:
            self.all_skills = set(initial_state)
            self.all_skills.update(goal_state)
            for act in actions:
                self.all_skills.update(act.preconditions)
                self.all_skills.update(act.add_effects)
        else:
            self.all_skills = all_skills

    def is_goal(self, state: Set[str]) -> bool:
        return self.goal.issubset(state)
    