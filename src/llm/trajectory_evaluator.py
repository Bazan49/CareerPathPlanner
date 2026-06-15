from typing import List, Dict
from src.model.course import Course
from src.model.skill import Skill
from src.llm.llm_client import LLMClient
from src.utils.logger import default_logger as logger
from src.utils.utils import skill_dict

SYSTEM_PROMPT = """
Eres un asesor profesional experto en planificación de carreras y formación.
Debes EVALUAR LA CALIDAD DE LA TRAYECTORIA de cursos propuesta según los siguientes criterios, usando una escala de 1 a 5 (1=muy deficiente, 5=excelente).

ACLARACIONES FUNDAMENTALES:
- Todos los datos que recibirás (habilidades iniciales, cursos, habilidades finales) pertenecen a un catálogo CERRADO.
- La trayectoria respeta los prerrequisitos y el orden es correcto. No cuestiones la secuencia.
- Si el usuario solicita una herramienta o habilidad que no aparece en los datos, el sistema la ha sustituido por la habilidad más cercana disponible. No penalices al plan por ello; valora la equivalencia.

Criterios:
1. **Cumplimiento del objetivo del usuario**: ¿La trayectoria satisface lo que el usuario pidió? Valora si las habilidades finales coinciden con lo solicitado, si la duración total es razonable y si hay contenido no solicitado.
2. **Progreso profesional (crecimiento en conocimiento)**: Observa la evolución de las habilidades a lo largo de los pasos. Valora cómo aumentan y si el ritmo de avance es eficiente. 

Formato de respuesta (OBLIGATORIO):
- Escribe una línea por criterio con el siguiente formato exacto:
  **<nombre del criterio>: X/5** - Explicación breve, concisa y clara.
- Al final, añade una línea con la puntuación global:
  **Puntuación global: X/5**
- No incluyas ningún otro texto antes ni después.
- Responde ÚNICAMENTE en texto plano.
"""

def build_user_prompt(
    user_objective: str,
    initial_skills: List[Skill],
    plan: List[Course],
    total_planned_duration: float,
    skill_dict_map: Dict[str, Skill]
) -> str:
    # Habilidades iniciales
    init_skills_desc = "\n".join(
        [f"- {s.name}" for s in initial_skills]
    ) if initial_skills else "Ninguna"

    current_state = set(s.id for s in initial_skills)

    # Construir secuencia paso a paso: solo las novedades de cada curso
    steps_desc = []
    for i, c in enumerate(plan, 1):
        course_desc = (
            f"Curso {i}: {c.name} "
            f"(nivel {c.level.value}, dificultad {c.difficulty_score:.2f}, {c.duration}h, "
        )
        # Habilidades realmente nuevas (no presentes antes del curso)
        new_skills = [sid for sid in c.add_effects if sid not in current_state]
        if new_skills:
            new_desc = "\n".join(
                [f"- {skill_dict_map[sid].name}" 
                 for sid in new_skills]
            )
        else:
            new_desc = "Ninguna (ya poseía todas)"
        steps_desc.append(f"{course_desc}\nNuevas habilidades adquiridas en este curso:\n{new_desc}")
        current_state.update(c.add_effects)

    plan_text = "\n\n".join(steps_desc) if steps_desc else "Ningún curso."

    # Conjunto final de todas las habilidades
    final_skills = [skill_dict_map[sid] for sid in current_state]
    final_skills_desc = "\n".join(
        [f"- {s.name}" for s in final_skills]
    ) if final_skills else "Ninguna"

    prompt = f"""
        Objetivo profesional del usuario: "{user_objective}"

        Habilidades iniciales del estudiante:
        {init_skills_desc}

        Trayectoria de cursos propuesta (progreso paso a paso):
        {plan_text}

        Duración total planeada: {total_planned_duration} horas.

        Conjunto final de todas las habilidades tras completar el plan:
        {final_skills_desc}
    """

    return prompt

def evaluate_trajectory(
    user_objective: str,
    initial_skills: List[Skill],
    plan: List[Course],
    final_skills: List[Skill],
    llm_client: LLMClient,
) -> str:
    
    total_planned_duration = sum(c.duration for c in plan)
    skill_map = skill_dict(final_skills)
    user_prompt = build_user_prompt(
        user_objective, initial_skills, plan, total_planned_duration, skill_map
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    response = llm_client.generate_answer(messages)
   
    # Fallback si la respuesta está vacía o es None
    if not response or not response.strip():
        logger.warning("El LLM devolvió una respuesta vacía.")
        return "No se obtuvo respuesta del evaluador."

    # Fallback adicional por si la respuesta es excesivamente corta (poco probable que sea válida)
    if len(response.strip()) < 10:
        logger.warning("Respuesta del LLM demasiado corta, se devuelve mensaje por defecto.")
        return "No se pudo obtener una evaluación válida. Intente de nuevo más tarde."

    return response
