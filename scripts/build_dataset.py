import json
import random
import sys
import re
from pathlib import Path
from collections import defaultdict

random.seed(42)  # Para reproducibilidad

def slugify(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r'[áä]', 'a', name)
    name = re.sub(r'[éë]', 'e', name)
    name = re.sub(r'[íï]', 'i', name)
    name = re.sub(r'[óö]', 'o', name)
    name = re.sub(r'[úü]', 'u', name)
    name = re.sub(r'[^a-z0-9\s]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name

def compute_duration(primary_level: int, num_skills: int) -> int:
    base = {0: 30, 1: 60, 2: 100, 3: 150}.get(primary_level, 60)
    noise = random.randint(-10, 10)
    duration = base + noise + num_skills * 10
    return max(20, min(300, duration))

def compute_success_prob(primary_level: int, num_skills: int = 1) -> float:
    base = {0: 0.95, 1: 0.85, 2: 0.75, 3: 0.65}.get(primary_level, 0.8)
    noise = random.uniform(-0.05, 0.05)
    prob = base + noise - (num_skills - 1) * 0.02
    return max(0.1, min(0.99, prob))

def format_skill_list(skills):
    """Formatea una lista de habilidades separadas por comas."""
    return ", ".join(skills)

def generate_courses_from_knowledge(knowledge_path: str, output_dir: str = "data",
                                    total_courses: int = 30,
                                    max_skills_per_course: int = 3,
                                    allow_adjacent_levels: bool = True,
                                    use_skill_groups: bool = True):
    """
    Genera un dataset de cursos a partir de un archivo de conocimiento del dominio.
    El archivo debe tener las claves "domain", "skills" y opcionalmente "skill_groups".
    """
    with open(knowledge_path, 'r', encoding='utf-8') as f:
        domain_knowledge = json.load(f)

    domain = domain_knowledge['domain'].replace(' ', '_').lower()
    skills_data = domain_knowledge['skills']
    skill_groups = domain_knowledge.get("skill_groups", []) if use_skill_groups else []

    output_path = Path(output_dir) / domain
    output_path.mkdir(parents=True, exist_ok=True)

    # Mapear información de cada habilidad
    skill_info = {}
    for skill in skills_data:
        name = skill['name']
        skill_info[name] = {
            'slug': slugify(name),
            'level': skill.get('level', 0),
            'requires': skill.get('requires', [])
        }

    # Exportar skills.json (lista de habilidades con slug)
    skills_export = [
        {"id": info['slug'], "name": name, "level": info['level']}
        for name, info in skill_info.items()
    ]
    with open(output_path / 'skills.json', 'w', encoding='utf-8') as f:
        json.dump({"skills": skills_export}, f, indent=2, ensure_ascii=False)

    # Agrupar habilidades por nivel
    skills_by_level = defaultdict(list)
    for name, info in skill_info.items():
        skills_by_level[info['level']].append(name)

    available_levels = list(skills_by_level.keys())
    if not available_levels:
        raise ValueError("No hay habilidades en la base de conocimiento")

    # Función para obtener habilidades del mismo grupo que la semilla
    def get_group_skills(seed, allowed_levels):
        candidates = []
        for group in skill_groups:
            if seed in group:
                for other in group:
                    if other != seed and skill_info[other]['level'] in allowed_levels:
                        candidates.append(other)
        return list(set(candidates))

    courses = []
    attempts = 0
    max_attempts = total_courses * 20

    while len(courses) < total_courses and attempts < max_attempts:
        attempts += 1
        # Elegir nivel semilla aleatorio
        seed_level = random.choice(available_levels)
        seed_skills = skills_by_level[seed_level]
        if not seed_skills:
            continue
        seed = random.choice(seed_skills)

        # Niveles permitidos para habilidades adicionales
        if allow_adjacent_levels:
            allowed_levels_set = {seed_level}
            if seed_level - 1 in skills_by_level:
                allowed_levels_set.add(seed_level - 1)
            if seed_level + 1 in skills_by_level:
                allowed_levels_set.add(seed_level + 1)
        else:
            allowed_levels_set = {seed_level}

        # Selección de candidatos 
        candidate_skills = []
        if use_skill_groups and skill_groups:
            # Priorizar habilidades del mismo grupo
            group_candidates = get_group_skills(seed, allowed_levels_set)
            if group_candidates:
                candidate_skills = group_candidates
            else:
                # Si la semilla no pertenece a ningún grupo, no añadir otras habilidades
                candidate_skills = []   
        else:
            # Sin grupos: todas las habilidades de niveles permitidos
            for lvl in allowed_levels_set:
                candidate_skills.extend(skills_by_level[lvl])
            candidate_skills = list(set(candidate_skills))

        # Eliminar la semilla de los candidatos
        candidate_skills = [s for s in candidate_skills if s != seed]

        max_extra = min(max_skills_per_course - 1, len(candidate_skills))
        if max_extra < 0:
            continue
        num_extra = random.randint(0, max_extra) if max_extra > 0 else 0

        # Seleccionar habilidades adicionales
        if num_extra > 0:
            chosen_others = random.sample(candidate_skills, num_extra)
        else:
            chosen_others = []

        chosen = [seed] + chosen_others

        chosen_levels = [skill_info[s]['level'] for s in chosen]
        primary_level = max(chosen_levels)
        num_skills = len(chosen)

        duration = compute_duration(primary_level, num_skills)
        success_prob = compute_success_prob(primary_level, num_skills)

        level_to_difficulty = {0: "Beginner", 1: "Intermediate", 2: "Advanced", 3: "Expert"}
        difficulty_str = level_to_difficulty.get(primary_level, "Intermediate")

        # Prerrequisitos: unión de requires, excluyendo habilidades enseñadas
        pre_set = set()
        for s in chosen:
            pre_set.update(skill_info[s]['requires'])
        pre_set -= set(chosen)
        preconditions_slug = [skill_info[p]['slug'] for p in pre_set if p in skill_info]
        adds_slug = [skill_info[s]['slug'] for s in chosen]

        slug_to_name = {info['slug']: name for name, info in skill_info.items()}
        pre_names = [slug_to_name.get(slug, slug) for slug in preconditions_slug]
        adds_names = [slug_to_name.get(slug, slug) for slug in adds_slug]

        pre_text = "Requiere: " + ", ".join(pre_names) + ". " if pre_names else "No requiere prerrequisitos. "
        teach_text = "Enseña: " + ", ".join(adds_names) + "."
        description = pre_text + teach_text

        course_name = f"Curso de {format_skill_list(adds_names)}"

        course = {
            "id": f"course_{len(courses)+1}",
            "name": course_name,
            "preconditions": preconditions_slug,
            "adds": adds_slug,
            "duration": duration,
            "success_prob": round(success_prob, 3),
            "difficulty": difficulty_str,
            "description": description
        }
        courses.append(course)

    if len(courses) < total_courses:
        print(f"Advertencia: solo se pudieron generar {len(courses)} cursos (límite de intentos).")

    # Guardar courses.json
    with open(output_path / 'courses.json', 'w', encoding='utf-8') as f:
        json.dump({"courses": courses}, f, indent=2, ensure_ascii=False)

    print(f"Dataset generado en: {output_path}")
    print(f"  - {len(skills_export)} habilidades")
    print(f"  - {len(courses)} cursos")
    if courses:
        print(f"  - Duración promedio: {sum(c['duration'] for c in courses)/len(courses):.1f}h")
        print(f"  - Éxito promedio: {sum(c['success_prob'] for c in courses)/len(courses):.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python build_dataset_from_knowledge.py <ruta_conocimiento> [directorio_salida] [total_cursos]")
        sys.exit(1)
    knowledge_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "data"
    total = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    generate_courses_from_knowledge(knowledge_path, output_dir, total_courses=total)