import json
import re
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set
from src.model.skill import Skill
from src.utils.utils import skill_dict
from src.utils.logger import default_logger

class DatasetGenerator:
    """Generador de datasets a partir de archivo de conocimiento del dominio."""

    def __init__(self,
                 total_courses: int = 30,
                 max_skills_per_course: int = 3,
                 allow_adjacent_levels: bool = True,
                 seed: int = 42):
        
        self.total_courses = total_courses
        self.max_skills_per_course = max_skills_per_course
        self.allow_adjacent_levels = allow_adjacent_levels
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def generate(self, knowledge_path: str, output_dir: str = "data") -> None:
        """Genera el dataset completo (skills.json y courses.json) en output_dir/<domain>."""

        default_logger.info(f"Iniciando generación de dataset desde {knowledge_path} con {self.total_courses} cursos objetivo.")

        domain_knowledge = self._load_knowledge(knowledge_path)
        domain = self._extract_domain(domain_knowledge)

        output_path = Path(output_dir) / domain
        output_path.mkdir(parents=True, exist_ok=True)

        skills = self._build_and_save_skills(domain_knowledge["skills"], output_path)
        skills_dict = skill_dict(skills)
        skill_groups = domain_knowledge.get("skill_groups", [])
        skill_groups_slug = [[self._slugify(s) for s in group] for group in skill_groups]

        self._build_and_save_courses(skills_dict, skill_groups_slug, output_path)
        default_logger.info(f"Dataset generado en: {output_path}")

    def _load_knowledge(self, path: str) -> dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            default_logger.error(f"Archivo de conocimiento no encontrado: {path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            default_logger.error(f"El archivo de conocimiento no es un JSON válido: {e}")
            sys.exit(1)

    def _extract_domain(self, domain_knowledge: dict) -> str:
        return domain_knowledge["domain"].replace(" ", "_").lower()

    def _slugify(self, name: str) -> str:
        name = name.lower().strip()
        name = re.sub(r'[áä]', 'a', name)
        name = re.sub(r'[éë]', 'e', name)
        name = re.sub(r'[íï]', 'i', name)
        name = re.sub(r'[óö]', 'o', name)
        name = re.sub(r'[úü]', 'u', name)
        name = re.sub(r'[^a-z0-9\s]', '', name)
        name = re.sub(r'\s+', '_', name)
        return name
    
    # Habilidades
    def _build_and_save_skills(self, skills_data: List[dict], output_path: Path) -> List[Skill]:
        skills = []
        for skill_info in skills_data:
            skill_id = self._slugify(skill_info["name"])
            # Convertir los nombres de los prerrequisitos a slugs
            req_slugs = [self._slugify(req) for req in skill_info.get("requires", [])]
            skill = Skill(
                id=skill_id,
                name=skill_info["name"],
                level=skill_info["level"],
                requires=req_slugs,
                description=skill_info["description"]
            )
            skills.append(skill)
        skills_json = {"skills": [s.to_dict() for s in skills]}
        with open(output_path / "skills.json", "w", encoding="utf-8") as f:
            json.dump(skills_json, f, indent=2, ensure_ascii=False)
        return skills

    # Cursos
    def _build_and_save_courses(self, skills_dict: Dict[str, Skill],
                                skill_groups: List[List[str]],
                                output_path: Path) -> None:
        skills_by_level = self._group_skills_by_level(skills_dict)
        courses = self._generate_courses(skills_dict, skills_by_level, skill_groups)
        with open(output_path / "courses.json", "w", encoding="utf-8") as f:
            json.dump({"courses": courses}, f, indent=2, ensure_ascii=False)

    def _group_skills_by_level(self, skills_dict: Dict[str, Skill]) -> Dict[int, List[str]]:
        grouped = defaultdict(list)
        for skill_id, skill in skills_dict.items():
            grouped[skill.level].append(skill_id)
        return dict(grouped)

    def _generate_courses(self, skills_dict: Dict[str, Skill],
                      skills_by_level: Dict[int, List[str]],
                      skill_groups: List[List[str]]) -> List[dict]:
        """
        Genera una lista de cursos según los parámetros de configuración.
        """
        courses = []                             # lista de cursos generados
        attempts = 0                             # contador de intentos totales
        max_attempts = self.total_courses * 2    # límite para evitar bucles infinitos

        while len(courses) < self.total_courses and attempts < max_attempts:
            attempts += 1

            # Seleccionar nivel aleatorio de habilidad
            available_levels = list(skills_by_level.keys())
            if not available_levels:
                break                     # no hay habilidades, salir
            seed_level = self.rng.choice(available_levels)

            # Elegir una habilidad semilla (principal) de ese nivel 
            seed_skills = skills_by_level[seed_level]                
            seed = self.rng.choice(seed_skills)

            # Determinar niveles permitidos para habilidades adicionales
            allowed_levels = self._allowed_levels(seed_level, skills_by_level)

            # Obtener habilidades candidatas (adicionales) según grupos y niveles
            candidate_skills = self._get_candidates(seed, allowed_levels, skill_groups, skills_dict)

            # Decidir cuántas habilidades adicionales enseñará este curso
            max_extra = min(self.max_skills_per_course - 1, len(candidate_skills))
            if max_extra < 0:
                # no caben habilidades adicionales, el curso será solo la semilla
                chosen_skills = [seed]
            else:
                num_extra = self.rng.integers(0, max_extra, endpoint=True)   # número de habilidades extra
                if num_extra == 0:
                    chosen_skills = [seed]
                else:
                    chosen_others = self.rng.choice(candidate_skills, size=num_extra, replace=False)
                    chosen_skills = [seed] + list(chosen_others)

            # Construir la entrada del curso (diccionario con metadatos) 
            course = self._build_course_entry(chosen_skills, skills_dict, len(courses) + 1)
            if course:
                courses.append(course)

        if len(courses) < self.total_courses:
            default_logger.warning(f"Solo se pudieron generar {len(courses)} cursos (límite de intentos).")
        return courses

    def _allowed_levels(self, seed_level: int,
                        skills_by_level: Dict[int, List[str]]) -> Set[int]:
        levels = {seed_level}
        if self.allow_adjacent_levels:
            if seed_level - 1 in skills_by_level:
                levels.add(seed_level - 1)
            if seed_level + 1 in skills_by_level:
                levels.add(seed_level + 1)
        return levels

    def _get_candidates(self, seed: str, allowed_levels: Set[int],
                        skill_groups: List[List[str]],
                        skills_dict: Dict[str, Skill]) -> List[str]:
        candidates = []
        if not skill_groups:
            return candidates

        for group in skill_groups:
            if seed in group:
                for other in group:
                    if other != seed and other in skills_dict:
                        if skills_dict[other].level in allowed_levels:
                            candidates.append(other)
        return list(set(candidates))

    def _build_course_entry(self, chosen: List[str],
                            skills_dict: Dict[str, Skill],
                            course_index: int) -> dict:
        
        chosen_levels = [skills_dict[s].level for s in chosen]
        primary_level = max(chosen_levels)

        # Duración
        duration = self._compute_duration(primary_level, len(chosen))

        # Nivel
        level_str = {0: "Beginner", 1: "Intermediate", 2: "Advanced", 3: "Expert"}.get(primary_level, "Intermediate")

        # Prerrequisitos
        pre_set = set()
        for skill_id in chosen:
            pre_set.update(skills_dict[skill_id].requires)
        pre_set -= set(chosen)
        preconditions_slug = [s for s in pre_set if s in skills_dict]

        # Descripción
        adds_names = [skills_dict[s].name for s in chosen]
        pre_names = [skills_dict[s].name for s in preconditions_slug]

        pre_text = "Requiere: " + ", ".join(pre_names) + ". " if pre_names else "No requiere prerrequisitos. "
        teach_text = "Enseña: " + ", ".join(adds_names) + "."
        description = pre_text + teach_text

        # Nombre
        course_name = f"Curso de {self._format_skill_list(adds_names)}"

        # Dificultad
        difficulty = self._compute_difficulty(chosen_levels, self.max_skills_per_course, max_level=3)

        return {
            "id": f"course_{course_index}",
            "name": course_name,
            "preconditions": preconditions_slug,
            "adds": chosen,
            "duration": int(duration),
            "level": level_str,
            "difficulty_score": float(difficulty),
            "description": description
        }
    
    def _compute_duration(self, primary_level: int, num_skills: int) -> int:
        base = {0: 30, 1: 60, 2: 100, 3: 150}.get(primary_level, 60)
        noise = self.rng.integers(-10, 10, endpoint=True)  
        duration = base + noise + num_skills * 10
        return max(20, min(300, duration))
    
    def _compute_difficulty(self, adds_levels: List[int], max_skills: int, max_level: int) -> float:
        if not adds_levels:
            return 0.0
        total_load = sum((lvl + 1) ** 2 for lvl in adds_levels)
        max_load = max_skills * ((max_level + 1) ** 2)
        raw = total_load / max_load
        noise = self.rng.uniform(-0.15, 0.15)
        difficulty = raw * (1 + noise)
        return max(0.05, min(0.95, difficulty))
    
    def _format_skill_list(self, skills: List[str]) -> str:
        return ", ".join(skills)
    