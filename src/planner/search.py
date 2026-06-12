import heapq
from dataclasses import dataclass
from typing import Optional, Callable
from src.planner.strips import STRIPSProblem

@dataclass
class SearchStats:
    expanded_nodes: int
    generated_total: int
    max_frontier_size: int

def search(
    problem: STRIPSProblem,
    action_cost: dict,
    heuristic: Optional[Callable] = None,
    return_stats: bool = True
):
    """
    Búsqueda con coste uniforme (UCS) si heuristic es None o siempre retorna 0.
    Búsqueda A* si heuristic es una función.
    
    Args:
        problem: Instancia de STRIPSProblem.
        action_cost: Diccionario {nombre_accion: coste} con costes positivos.
        heuristic: Función heurística opcional que recibe un estado (frozenset)
                   y devuelve una estimación del coste restante (float).
                   Si es None, se usa h=0 (UCS).
        return_stats: Booleano que indica si se deben devolver estadísticas de búsqueda.
    
    Returns:
        Si return_stats=True: (plan, stats)
            plan: Lista de nombres de acciones (plan) o None si no hay solución.
            stats: SearchStats con:
                - expanded_nodes: número de estados expandidos.
                - generated_total: número total de generaciones de estados
                  (incluyendo duplicados, el inicial cuenta como 1).
                - max_frontier_size: tamaño máximo de la cola de prioridad.
        Si return_stats=False: plan (lista o None).
    """

    if heuristic is None:
        def h(state):
            return 0.0
    else:
        h = heuristic

    start = frozenset(problem.initial)
    if problem.is_goal(start):
        stats = SearchStats(
            expanded_nodes=0,
            generated_total=1,
            max_frontier_size=1,
        )
        return ([], stats) if return_stats else []
    
    dist = {start: 0.0}
    closed = set()
    heap = [(h(start), 0.0, start, [])]
    heapq.heapify(heap)
    expanded = 0
    generated_total = 1  
    max_frontier = 1
    
    while heap:
        max_frontier = max(max_frontier, len(heap))
        f, g, state, plan = heapq.heappop(heap)
        
        if state in closed:
            continue
        
        closed.add(state)
        expanded += 1
        
        if problem.is_goal(state):
            stats = SearchStats(
                expanded_nodes=expanded,
                generated_total=generated_total,
                max_frontier_size=max_frontier,
            )
            return (plan, stats) if return_stats else plan
        
        for action in problem.actions:
            if action.is_applicable(state):
                new_state = action.apply(state)
                new_state_frozen = frozenset(new_state)
                new_g = g + action_cost.get(action.name, 0.0)
                generated_total += 1
                if new_g < dist.get(new_state_frozen, float('inf')):
                    dist[new_state_frozen] = new_g
                    new_f = new_g + h(new_state_frozen)
                    heapq.heappush(heap, (new_f, new_g, new_state_frozen, plan + [action.name]))
    
    stats = SearchStats(
        expanded_nodes=expanded,
        generated_total=generated_total,
        max_frontier_size=max_frontier,
    )
    return (None, stats) if return_stats else None
