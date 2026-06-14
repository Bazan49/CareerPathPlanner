import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_management.dataset_generator import DatasetGenerator

def main():
    parser = argparse.ArgumentParser(description="Genera el dataset de cursos a partir de un dominio.")
    parser.add_argument(
        "knowledge_path",
        type=str,
        help="Ruta al archivo JSON de conocimiento del dominio (ej: data/cocina/conocimiento.json)"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data",
        help="Directorio de salida (por defecto: data)"
    )
    parser.add_argument(
        "--total_courses",
        type=int,
        default=30,
        help="Número de cursos a generar (por defecto: 30)"
    )
    parser.add_argument(
        "--max_skills",
        type=int,
        default=3,
        help="Máximo de habilidades por curso (por defecto: 3)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semilla aleatoria (por defecto: 42)"
    )
    parser.add_argument(
        "--adjacent_levels",
        action="store_true",
        default=True,
        help="Permitir niveles adyacentes en las habilidades adicionales"
    )

    args = parser.parse_args()

    # Instanciamos el generador de cursos
    generator = DatasetGenerator(
        total_courses=args.total_courses,
        max_skills_per_course=args.max_skills,
        allow_adjacent_levels=args.adjacent_levels,
        seed=args.seed,
    )

    # Generamos el dataset
    generator.generate(
        knowledge_path=args.knowledge_path,
        output_dir=args.output_dir
    )

if __name__ == "__main__":
    main()