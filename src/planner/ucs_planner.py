from planner.strips import STRIPSProblem
from src.planner.search import search

def ucs_planner(problem: STRIPSProblem, action_cost: dict, return_stats=True):
    return search(problem, action_cost, heuristic=None, return_stats=return_stats)
    