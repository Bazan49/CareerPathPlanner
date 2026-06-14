"""
Crea un nuevo archivo de definición de experimento en experiments/definitions/.
Uso: python scripts/create_experiment.py
"""

import json
import sys
from pathlib import Path

# Configuración
EXPERIMENTS_DIR = Path("experiments")
DEFINITIONS_DIR = EXPERIMENTS_DIR.joinpath("definitions")

# Valores por defecto
DEFAULT_DATASET = "data/ciencia_de_datos"
DEFAULT_PLANNER = "a_star_maxmin"
DEFAULT_RETURN_STATS = True
DEFAULT_RUN_SIMULATION = True
DEFAULT_RUN_EVALUATION = True

PLANNER_OPTIONS = {
    "1": "ucs",
    "2": "a_star_basic",
    "3": "a_star_maxmin"
}

def ensure_dirs():
    DEFINITIONS_DIR.mkdir(parents=True, exist_ok=True)

def get_non_empty_input(prompt: str, default: str = None) -> str:
    """Solicita entrada no vacía; si se proporciona default, se muestra entre corchetes."""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        if user_input:
            return user_input
        print("Este campo no puede estar vacío.")

def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Solicita respuesta s/n; devuelve True/False."""
    default_str = "s" if default else "n"
    while True:
        answer = input(f"{prompt} (s/n, default {default_str}): ").strip().lower()
        if not answer:
            return default
        if answer in ("s", "si", "y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Responda 's' o 'n'.")

def get_planner():
    """Muestra menú numérico y devuelve el nombre del planificador."""
    print("\nPlanificadores disponibles:")
    for num, name in PLANNER_OPTIONS.items():
        print(f"  {num}. {name}")
    while True:
        choice = input("Seleccione planificador (1, 2 o 3): ").strip()
        if choice in PLANNER_OPTIONS:
            return PLANNER_OPTIONS[choice]
        print("Opción inválida.")

def verify_dataset_path(path_str: str) -> Path:
    """Verifica que la ruta del dataset exista y contenga skills.json y courses.json."""
    path = Path(path_str)
    if not path.exists():
        print(f"Error: la ruta '{path}' no existe.")
        sys.exit(1)
    skills_file = path / "skills.json"
    courses_file = path / "courses.json"
    if not skills_file.exists():
        print(f"Error: no se encuentra {skills_file}")
        sys.exit(1)
    if not courses_file.exists():
        print(f"Error: no se encuentra {courses_file}")
        sys.exit(1)
    return path

def create_experiment():
    ensure_dirs()
    print("=== Crear nuevo experimento ===\n")

    # 1. Nombre (único)
    while True:
        name = get_non_empty_input("Nombre del experimento (sin espacios)")
        if " " in name:
            print("El nombre no puede contener espacios.")
            continue
        out_file = DEFINITIONS_DIR / f"{name}.json"
        if out_file.exists():
            print(f"Ya existe un experimento con el nombre '{name}'. Elija otro.")
            continue
        break

    # 2. Texto del usuario
    user_text = get_non_empty_input("Descripción del objetivo profesional")

    # 3. Ruta del dataset (con verificación)
    dataset_path_str = get_non_empty_input("Ruta al dataset", DEFAULT_DATASET)
    dataset_path = verify_dataset_path(dataset_path_str)

    # 4. Planificador (por número)
    planner = get_planner()

    # 5. Guardar estadísticas del planificador
    return_stats = get_yes_no("¿Guardar estadísticas del planificador?", DEFAULT_RETURN_STATS)

    # 6. Simulación Monte Carlo
    run_sim = get_yes_no("¿Ejecutar simulación Monte Carlo?", DEFAULT_RUN_SIMULATION)

    # 7. Evaluación con LLM
    run_eval = get_yes_no("¿Ejecutar evaluación con LLM?", DEFAULT_RUN_EVALUATION)

    # Mostrar resumen y confirmar
    print("\n--- Resumen del experimento ---")
    print(f"Nombre:           {name}")
    print(f"Objetivo:         {user_text}")
    print(f"Dataset:          {dataset_path}")
    print(f"Planificador:     {planner}")
    print(f"Guardar stats:    {'Sí' if return_stats else 'No'}")
    print(f"Simulación:       {'Sí' if run_sim else 'No'}")
    print(f"Evaluación LLM:   {'Sí' if run_eval else 'No'}")
    print("-----------------------------")

    confirm = get_yes_no("¿Guardar este experimento?", default=True)
    if not confirm:
        print("Cancelado.")
        return

    definition = {
        "name": name,
        "user_text": user_text,
        "dataset_path": str(dataset_path),
        "planner_name": planner,
        "return_stats": return_stats,
        "run_simulation": run_sim,
        "run_evaluation": run_eval
    }
    out_file = DEFINITIONS_DIR / f"{name}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(definition, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Definición guardada en {out_file}")

if __name__ == "__main__":
    create_experiment()