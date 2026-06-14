from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class SimulationResult:
    """
    Resultados de la simulación Monte Carlo de un plan de cursos.

    Attributes:
        success_rate: Proporción de estudiantes que completaron todo el plan.
        success_ci_95: Intervalo de confianza del 95% para success_rate (método de Wilson).
        mean_time: Tiempo medio (horas) de los estudiantes que tuvieron éxito (None si ningún éxito).
        median_time: Tiempo mediano (horas) de los estudiantes exitosos (None si ningún éxito).
        reach_probability: Diccionario {course_id: probabilidad de llegar a ese curso (iniciarlo)}.
        success_probability: Diccionario {course_id: probabilidad de aprobar el curso condicionada a haber llegado}.
        avg_attempts_per_course: Diccionario {course_id: número promedio de intentos por curso (incluye todos los estudiantes)}.
    """
    success_rate: float
    success_ci_95: tuple[float, float]
    mean_time: Optional[float]
    median_time: Optional[float]
    reach_probability: Dict[str, float]
    success_probability: Dict[str, float]
    avg_attempts_per_course: Dict[str, float]

    def __str__(self) -> str:
        lines = [f"Tasa de éxito: {self.success_rate:.2%}"]
        lines.append(f"Intervalo de confianza 95%: ({self.success_ci_95[0]:.2%}, {self.success_ci_95[1]:.2%})")
        if self.mean_time is not None and self.median_time is not None:
            lines.append(f"Tiempo (solo éxitos): media = {self.mean_time:.1f} h, mediana = {self.median_time:.1f} h")
        else:
            lines.append("Tiempo: sin datos de éxitos")
        if self.avg_attempts_per_course:
            # Curso con mayor promedio de intentos
            most_attempts = max(self.avg_attempts_per_course.items(), key=lambda x: x[1])
            lines.append(f"Curso con mayor promedio de intentos: {most_attempts[0]} -> {most_attempts[1]:.2f} intentos")
        return "\n".join(lines)
    