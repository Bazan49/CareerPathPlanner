from src.planner.search import search
from src.model.strips import STRIPSProblem

def a_star_basic_planner(problem: STRIPSProblem, action_cost: dict, return_stats=True):
    """
    A* con heurística básica: cantidad de habilidades objetivo faltantes.
    """
    def h_basic(state):
        return len(problem.goal - state)
    return search(problem, action_cost, heuristic=h_basic, return_stats=return_stats)

def a_star_maxmin_planner(problem: STRIPSProblem, action_cost: dict, return_stats=True):
    """
    A* con heurística max-min: máximo de los costes mínimos de los cursos que enseñan
    cada habilidad faltante (ignorando prerequisitos, admisible).
    """
    # Precomputar coste mínimo por habilidad
    min_cost_for_skill = {}
    for skill in problem.all_skills:
        best = float('inf')
        for action in problem.actions:
            if skill in action.add_effects:
                cost = action_cost.get(action.name, float('inf'))
                if cost < best:
                    best = cost
        min_cost_for_skill[skill] = best

    def h_max_min(state):
        missing = problem.goal - state
        if not missing:
            return 0.0
        return max(min_cost_for_skill[s] for s in missing)

    return search(problem, action_cost, heuristic=h_max_min, return_stats=return_stats)