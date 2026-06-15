"""
Ejecuta un experimento definido en un archivo JSON y guarda los resultados.
Uso: python scripts/run_experiment.py [--name <nombre> | --definition <archivo.json>]
Si no se especifica, muestra lista interactiva.
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline import run_planning_pipeline
from src.simulation.montecarlo import SimulationParams
from src.utils.result_saver import save_experiment_results
from src.utils.logger import default_logger as logger

EXPERIMENTS_DIR = Path("experiments")
DEFINITIONS_DIR = EXPERIMENTS_DIR.joinpath("definitions")

def ensure_dirs():
    """Asegura que exista el directorio de definiciones."""
    DEFINITIONS_DIR.mkdir(parents=True, exist_ok=True)

def list_available_experiments():
    """Devuelve lista de nombres de experimentos disponibles."""
    ensure_dirs()
    return [f.stem for f in DEFINITIONS_DIR.glob("*.json")]

def select_experiment_interactive():
    """Muestra lista interactiva y devuelve el nombre seleccionado."""
    experiments = list_available_experiments()
    if not experiments:
        print("No hay experimentos definidos en experiments/definitions/.")
        sys.exit(1)
    print("Experimentos disponibles:")
    for i, name in enumerate(experiments, 1):
        print(f"  {i}. {name}")
    while True:
        try:
            choice = input("Seleccione el número del experimento: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(experiments):
                return experiments[idx]
            print("Número inválido.")
        except ValueError:
            print("Por favor ingrese un número.")

def run_experiment(experiment_name: str = None, definition_file: Path = None):
    """
    Carga la definición, ejecuta el pipeline y guarda los resultados.
    """
    ensure_dirs()

    # Determinar la ruta del archivo de definición
    if definition_file:
        def_path = Path(definition_file)
    elif experiment_name:
        def_path = DEFINITIONS_DIR.joinpath(f"{experiment_name}.json")
    else:
        experiment_name = select_experiment_interactive()
        def_path = DEFINITIONS_DIR.joinpath(f"{experiment_name}.json")

    if not def_path.exists():
        print(f"Error: Definición no encontrada: {def_path}")
        logger.error(f"Definición no encontrada: {def_path}")
        sys.exit(1)

    # Cargar definición
    with open(def_path, "r", encoding="utf-8") as f:
        definition = json.load(f)

    name = definition.get("name", def_path.stem)

    # Informar al usuario y al log
    print(f"Ejecutando experimento '{name}'...")
    logger.info(f"Ejecutando experimento '{name}'...")

    # Flags de ejecución (valores por defecto si no están presentes)
    return_stats = definition.get("return_stats", True)
    run_simulation = definition.get("run_simulation", True)
    run_evaluation = definition.get("run_evaluation", True)

    # Ejecutar pipeline
    start_time = time.perf_counter()
    plan, planner_stats, sim_result, evaluation, initial_skills, goal_skills = run_planning_pipeline(
        user_text=definition["user_text"],
        dataset_path=Path(definition["dataset_path"]),
        planner_name=definition["planner_name"],
        return_stats=return_stats,
        run_simulation=run_simulation,
        run_evaluation=run_evaluation,
    )
    elapsed = time.perf_counter() - start_time
    logger.info(f"Pipeline completado en {elapsed:.2f} segundos")  

    # Guardar resultados
    out_file = save_experiment_results(
        experiment_name=name,
        definition=definition,
        plan=plan,
        planner_stats=planner_stats,
        sim_result=sim_result,
        evaluation=evaluation,
        elapsed_time=elapsed,
        initial_skills=initial_skills,
        goal_skills=goal_skills
    )

    # Mostrar al usuario dónde se guardaron los resultados
    print(f"Resultados guardados en {out_file}")
    logger.info(f"Resultados guardados en {out_file}")

    # Mostrar plan y estadísticas en consola 
    if plan:
        print("\nPlan encontrado:")
        for i, c in enumerate(plan, 1):
            print(f"  {i}. {c.name}")

        if sim_result:
            print(f"\nResultados de simulación:")
            print(sim_result.__str__())

        if evaluation:
            print("\nEvaluación del LLM:")
            print(evaluation)
    else:
        print("No se encontró ningún plan.")
        logger.warning("No se encontró plan.")

def main():
    parser = argparse.ArgumentParser(description="Ejecutar experimento")
    parser.add_argument("--name", help="Nombre del experimento (en experiments/definitions/)")
    parser.add_argument("--definition", help="Ruta a un archivo JSON de definición")
    args = parser.parse_args()
    run_experiment(experiment_name=args.name, definition_file=args.definition)


if __name__ == "__main__":
    main()