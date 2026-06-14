import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import asdict

def save_experiment_results(
    experiment_name: str,
    definition: Dict[str, Any],
    plan: Optional[List],
    planner_stats: Optional[Any],
    sim_result: Optional[Any],
    evaluation: Optional[str],
    elapsed_time: float,
    output_dir: Path = Path("experiments/results"),
) -> Path:
    """
    Guarda los resultados de un experimento en un archivo JSON.

    Args:
        experiment_name: Nombre único del experimento.
        definition: Diccionario con la definición del experimento.
        plan: Lista de objetos Course (o None).
        planner_stats: Estadísticas del planificador (o None).
        sim_result: Resultado de simulación (o None).
        evaluation: Evaluación del LLM (o None).
        elapsed_time: Tiempo de ejecución en segundos.
        output_dir: Directorio donde guardar el JSON.

    Returns:
        Ruta al archivo JSON guardado.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Construir diccionario de resultados
    results = {
        "experiment_name": experiment_name,
        "timestamp": datetime.now().isoformat(),
        "definition": definition,
        "plan": {
            "course_ids": [c.id for c in plan] if plan else [],
            "courses": [
                {
                    "id": c.id,
                    "name": c.name,
                    "preconditions": list(c.preconditions),
                    "adds": list(c.add_effects),
                    "level": c.level.value,
                    "duration": c.duration,
                    "difficulty_score": c.difficulty_score,
                    "description": c.description,
                }
                for c in plan
            ] if plan else [],
        },
        "planner_stats": asdict(planner_stats) if planner_stats else None,
        "simulation_stats": asdict(sim_result) if sim_result else None,
        "llm_evaluation": evaluation,
        "elapsed_time_seconds": elapsed_time,
    }

    out_file = output_dir / f"{experiment_name}_result.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    return out_file
