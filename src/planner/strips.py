"""
Módulo STRIPS para planificación clásica.
"""

from typing import Optional, Set, List

class STRIPSAction:
    """
    Acción STRIPS.

    Atributos:
        name (str): Identificador único de la acción (ej. 'python101').
        preconditions (Set[str]): Conjunto de literales que deben ser verdaderos para aplicar la acción.
        add_effects (Set[str]): Conjunto de literales que se vuelven verdaderos tras ejecutar la acción.
    """
    def __init__(self, name: str, preconditions: Set[str], add_effects: Set[str]):
        self.name = name
        self.preconditions = preconditions
        self.add_effects = add_effects

    def is_applicable(self, state: Set[str]) -> bool:
        return self.preconditions.issubset(state)

    def apply(self, state: Set[str]) -> Set[str]:
        if not self.is_applicable(state):
            raise ValueError(f"Acción {self.name} no aplicable en el estado {state}")
        return state.union(self.add_effects)

class STRIPSProblem:
    """
    Problema de planificación STRIPS.

    Atributos:
        initial (Set[str]): Estado inicial (conjunto de habilidades verdaderas).
        goal (Set[str]): Estado objetivo (habilidades que deben ser verdaderas al final).
        actions (List[STRIPSAction]): Lista de acciones disponibles.
        all_skills (Set[str]): Conjunto de todas las habilidades posibles.
            Si no se proporciona, se calcula automáticamente a partir del estado inicial,
            objetivo y acciones.
    """
    def __init__(self, initial_state: Set[str], goal_state: Set[str], actions: List[STRIPSAction],
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
    