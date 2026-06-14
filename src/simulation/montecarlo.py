import math
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np
from collections import defaultdict
from src.model.course import Course
from src.simulation.simulation_result import SimulationResult

@dataclass
class SimulationParams:
    seed: int = 42
    max_attempts: int = 3
    dropout_prob: float = 0.05
    max_dropout_prob: float = 0.95
    duration_noise: float = 0.20
    theta_min: float = -3.0
    theta_max: float = 3.0
    theta_mean: float = 0.0
    theta_std: float = 1.0
    failure_learning_gain: float = 0.02
    success_learning_gain: float = 0.08
    min_difficulty: float = 1e-4
    max_difficulty: float = 1 - 1e-4
    num_simulations: int = 10000

def simulate_plan(
    plan: list[Course],
    sim_params: SimulationParams
) -> SimulationResult:
    """
    Ejecuta múltiples simulaciones de estudiantes y devuelve estadísticas agregadas.
    """
    # Inicializar generador de números aleatorios con la semilla fija para reproducibilidad
    rng = np.random.default_rng(sim_params.seed)

    # Contadores acumuladores
    successes = 0                     # número de estudiantes que completan todo el plan
    times_success = []                # tiempos totales de los estudiantes exitosos 
    all_attempts = defaultdict(list)  # lista de intentos por curso (para promedio)
    reached_counts = defaultdict(int) # cuántos estudiantes llegaron a cada curso
    success_counts = defaultdict(int) # cuántos aprobaron el curso (entre los que llegaron)

    for _ in range(sim_params.num_simulations):
        # Simular un estudiante con el plan actual
        total_time, success, attempts, approved= simulate_student(plan, rng, sim_params)

        # Registrar intentos y llegadas/aprobaciones
        for cid, att in attempts.items():
            all_attempts[cid].append(att)           # guardar número de intentos para este curso
            reached_counts[cid] += 1                # incrementar contador de llegadas
            if approved.get(cid, False):
                success_counts[cid] += 1            # incrementar contador de aprobados

        if success:
            successes += 1
            times_success.append(total_time)        # solo guardamos tiempos de los exitosos

    success_rate = successes / sim_params.num_simulations

    # Intervalo de confianza de Wilson para la tasa de éxito (95%)
    success_ci_95 = calculate_wilson_ci(successes, sim_params.num_simulations)

    # Estadísticas de tiempo (solo para estudiantes exitosos)
    if times_success:
        mean_time = float(np.mean(times_success))   # media
        median_time = float(np.median(times_success)) # mediana
    else:
        mean_time = median_time = None

    # Probabilidad de llegar a cada curso (proporción de estudiantes que alcanzan ese curso)
    reach_probability = {}
    for course in plan:
        cid = course.id
        reached = reached_counts.get(cid, 0)
        reach_probability[cid] = reached / sim_params.num_simulations

    # Probabilidad de aprobar cada curso condicionada a haber llegado
    success_probability = {}
    for course in plan:
        cid = course.id
        reached = reached_counts.get(cid, 0)
        succeeded = success_counts.get(cid, 0)
        success_probability[cid] = succeeded / reached if reached > 0 else 0.0

    # Número medio de intentos por curso (considerando todos los estudiantes)
    avg_attempts = {cid: float(np.mean(vals)) for cid, vals in all_attempts.items() if vals}

    return SimulationResult(
        success_rate=success_rate,
        success_ci_95=success_ci_95,
        mean_time=mean_time,
        median_time=median_time,
        reach_probability=reach_probability,
        success_probability=success_probability,
        avg_attempts_per_course=avg_attempts,
    )

def simulate_student(
    plan: list[Course],
    rng: np.random.Generator,
    params: SimulationParams
) -> tuple[float, bool, Dict[str, int], Dict[str, bool]]:
    """
    Simula un estudiante completando el plan.
    Retorna:
        total_time (float)
        success (bool)
        attempts_per_course (dict): {course_id: número de intentos}
        approved_per_course (dict): {course_id: True si aprobó, False si no (solo para cursos a los que llegó)}
    """
    # 1. Generar habilidad latente θ del estudiante (distribución normal)
    theta = calculate_student_theta(rng, params)
    theta = bound_theta(theta, params.theta_min, params.theta_max)

    total_time = 0.0
    attempts_per_course = {}    # almacena intentos por curso
    approved_per_course = {}    # almacena si aprobó cada curso (solo para los que llegó)

    # 3. Recorrer los cursos en el orden del plan
    for course in plan:

        # Convertir difficulty_score a parámetro b del modelo Rasch (logit)
        b = calculate_course_b(course, params)
        attempts = 0
        approved = False

        # Intentos para aprobar este curso (máximo max_attempts)
        while attempts < params.max_attempts:
            attempts += 1

            # Duración real del intento (con ruido)
            duration = calculate_real_course_duration(course, rng, params.duration_noise)
            total_time += duration

            # Probabilidad de aprobar según modelo logístico
            p = calculate_prob(theta, b)

            # Decidir si aprueba o no
            if rng.random() < p:
                approved = True
                # Aprendizaje por éxito (aumenta θ según dificultad del curso)
                theta += params.success_learning_gain * course.difficulty_score
                theta = bound_theta(theta, params.theta_min, params.theta_max)
                break

            #  No aprueba: aprendizaje por fracaso
            theta += params.failure_learning_gain * course.difficulty_score
            theta = bound_theta(theta, params.theta_min, params.theta_max)

            # Posibilidad de abandono (probabilidad aumenta con intentos y dificultad)
            dropout_p = min(params.max_dropout_prob, params.dropout_prob * attempts * course.difficulty_score)
            if rng.random() < dropout_p:
                break

        # Registrar resultados de este curso
        attempts_per_course[course.id] = attempts
        approved_per_course[course.id] = approved

        # Si no aprobó, el estudiante abandona el plan
        if not approved:
            return total_time, False, attempts_per_course, approved_per_course

    # El estudiante completó todos los cursos con éxito
    return total_time, True, attempts_per_course, approved_per_course

def calculate_student_theta(rng: np.random.Generator, params: SimulationParams) -> float:
    return float(rng.normal(params.theta_mean, params.theta_std))

def calculate_course_b(course: Course, params: SimulationParams) -> float:
    d = float(course.difficulty_score)
    d = min(max(d, params.min_difficulty), params.max_difficulty)
    return math.log(d / (1 - d))

def calculate_prob(theta: float, b: float) -> float:
    x = theta - b
    if x > 30:
        return 1.0
    if x < -30:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))

def calculate_real_course_duration(course: Course, rng: np.random.Generator, noise: float) -> float:
    base = float(course.duration)
    duration = rng.normal(base, base * noise)
    return max(0.5, float(duration))

def bound_theta(theta: float, theta_min: float, theta_max: float) -> float:
    return max(theta_min, min(theta_max, theta))

def calculate_wilson_ci(
        successes: int,
        total: int,
        z: float = 1.96
    ) -> tuple[float, float]:
    """
    Intervalo de confianza de Wilson para una proporción.

    Args:
        successes: número de éxitos.
        total: número total de ensayos.
        z: valor z (1.96 para 95%).

    Returns:
        (lower_bound, upper_bound)
    """
    if total == 0:
        return (0.0, 0.0)

    p = successes / total
    denominator = 1 + (z ** 2) / total
    center = (
        p + (z ** 2) / (2 * total)
    ) / denominator
    margin = (
        z
        * math.sqrt(
            (p * (1 - p) / total)
            + (z ** 2) / (4 * total ** 2)
        )
    ) / denominator
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return lower, upper
