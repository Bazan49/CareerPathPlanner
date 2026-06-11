import sys
import json
from pathlib import Path

# Añadir la raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.llm.generate_domain_knowledge import generate_domain_knowledge

def save_domain_knowledge(data: dict, output_dir: str = "domain_knowledge"):
    domain = data["domain"]
    domain_slug = domain.lower().replace(' ', '_')
    filename = f"{domain_slug}.json"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    filepath = output_path / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Base de conocimiento del dominio guardada en {filepath}")

if __name__ == "__main__":
    default_domain = "Cocina"
    default_num_skills = 20

    domain = sys.argv[1] if len(sys.argv) > 1 else default_domain
    num_skills = int(sys.argv[2]) if len(sys.argv) > 2 else default_num_skills

    print(f"Generando base de conocimiento para dominio '{domain}' con {num_skills} habilidades...")
    knowledge = generate_domain_knowledge(domain, num_skills)
    save_domain_knowledge(knowledge)