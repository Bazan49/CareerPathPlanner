"""
Pipeline completo de planificación, simulación y evaluación.
"""

import time
from pathlib import Path
from typing import List, Optional, Tuple, Any
from src.llm.llm_client import LLMClient
from src.llm.goal_interpreter import interpret_goal
from src.data_management.dataset_loader import DatasetLoader
from src.model.course import Course
from src.model.skill import Skill
from src.model.strips import STRIPSProblem
from src.planner.a_star_planner import a_star_maxmin_planner, a_star_basic_planner
from src.planner.ucs_planner import ucs_planner
from src.simulation.montecarlo import simulate_plan, SimulationParams, SimulationResult
from src.llm.trajectory_evaluator import evaluate_trajectory
from src.utils.logger import default_logger as logger
from src.utils.utils import skill_ids, skill_dict

def build_action_cost(courses: List[Course]) -> dict:
    """Construye el diccionario de coste (duración) para cada curso."""
    return {c.id: c.duration for c in courses}

def run_planning_pipeline(
    user_text: str,
    dataset_path: Path,
    planner_name: str = "a_star_maxmin",
    return_stats: bool = True,
    run_simulation: bool = True,
    run_evaluation: bool = True,
    sim_params: Optional[SimulationParams] = None
) -> Tuple[Optional[List[Course]], Optional[Any], Optional[SimulationResult], Optional[dict]]:
    """
    Ejecuta el pipeline completo:
    - Interpretación del objetivo con LLM
    - Carga de dataset
    - Planificación (UCS, A* básico o A* max-min)
    - Simulación Monte Carlo (opcional)
    - Evaluación con LLM (opcional)
    
    Returns:
        (plan, planner_stats, sim_result, evaluation)
        - plan: lista de objetos Course o None
        - planner_stats: objeto SearchStats o None (solo si return_stats=True)
        - sim_result: SimulationResult o None
        - evaluation: evaluación del LLM o None
    """

    logger.info("=== Inicio del pipeline de planificación ===")
    logger.debug(f"Texto del usuario: {user_text}")
    logger.info(f"Dataset: {dataset_path} | Planificador: {planner_name}")

    # Inicializar LLM
    llm_client = LLMClient()

    # Cargar datos del dominio
    loader = DatasetLoader(dataset_path)
    skills: List[Skill] = loader.load_skills()
    courses: List[Course] = loader.load_courses()
    all_skills = skill_ids(skills)

    # Interpretar objetivo con LLM
    logger.info("Interpretando objetivo con LLM...")

    interpretation = interpret_goal(user_text, all_skills, llm_client)
    current_skills = set(interpretation["current_skills"])
    goal_skills = set(interpretation["goal_skills"])

    logger.info(f"Habilidades iniciales detectadas: {current_skills}")
    logger.info(f"Habilidades objetivo detectadas: {goal_skills}")

    if not goal_skills:
        logger.error("No se detectaron habilidades objetivo en la descripción del usuario.")
        raise ValueError("No se detectaron habilidades objetivo en la descripción del usuario.")

    # Crear problema STRIPS
    problem = STRIPSProblem(current_skills, goal_skills, courses, all_skills=all_skills)

    # Construir action_cost (coste = duración del curso)
    action_cost = build_action_cost(courses)

    # Seleccionar planificador
    planner = planner_name.lower()
    if planner == "ucs":
        result = ucs_planner(problem, action_cost, return_stats=return_stats)
    elif planner == "a_star_basic":
        result = a_star_basic_planner(problem, action_cost, return_stats=return_stats)
    elif planner == "a_star_maxmin":
        result = a_star_maxmin_planner(problem, action_cost, return_stats=return_stats)
    else:
        raise ValueError(f"Planificador desconocido: {planner_name}")

    if return_stats:
        plan, planner_stats = result
    else:
        plan = result
        planner_stats = None

    logger.info(f"Planificación finalizada")

    # Verificar si hay plan antes de continuar
    if not plan:
        logger.warning("Plan vacío. Se omite simulación y evaluación.")
        return plan, planner_stats, None, None

    # Simulación Monte Carlo (opcional)
    sim_result = None
    if run_simulation:
        logger.info("Iniciando simulación Monte Carlo...")
        if sim_params is None:
            sim_params = SimulationParams()
        sim_result = simulate_plan(plan, sim_params)  

    # Evaluación con LLM (opcional)
    evaluation = None
    if run_evaluation:
        logger.info("Iniciando evaluación con LLM...")
        # Calcular habilidades finales a partir del plan
        state = set(problem.initial)
        for course in plan:
            state = course.apply(state)
        final_skill_ids = state
        skill_dict_map = skill_dict(skills)
        final_skills = [skill_dict_map[sid] for sid in final_skill_ids if sid in skill_dict_map]
        initial_skills = [skill_dict_map[sid] for sid in problem.initial if sid in skill_dict_map]

        evaluation = evaluate_trajectory(
            user_objective=user_text,
            initial_skills=initial_skills,
            plan=plan,
            final_skills=final_skills,
            llm_client=llm_client,
            sim_result=sim_result
        )

    logger.info("=== Pipeline completado ===")
    return plan, planner_stats, sim_result, evaluation
