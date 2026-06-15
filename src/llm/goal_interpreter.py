import json
import logging
from typing import Set
from src.llm.llm_client import LLMClient
from src.utils.logger import default_logger as logger

SYSTEM_PROMPT_TEMPLATE = """
Eres un asistente de planificación profesional. Tu tarea es inferir, a partir de la descripción del usuario, dos conjuntos de habilidades:

1. **current_skills** – Habilidades que el usuario YA POSEE (se indica claramente que domina).  
   - Incluye solo si el usuario menciona explícitamente que ya las tiene.  
   - Si el usuario menciona que posee cierto perfil técnico (ej. "soy graduado en matemáticas", "tengo experiencia en análisis de datos"), PUEDES inferir las habilidades fundamentales que normalmente acompañan a ese perfil e incluirlas en current_skills, pero NUNCA incluyas una habilidad que el usuario diga explícitamente que necesita aprender o mejorar. 

2. **goal_skills** – Habilidades que el usuario DESEA ALCANZAR, mejorar o aprender.  
   - Cualquier habilidad que el usuario mencione como “quiero aprender”, “necesito”, “me gustaría dominar”, etc.  
   - Si el objetivo profesional (ej. “ser analista de datos”) requiere habilidades que no se mencionan, PUEDES inferir las indispensables para cumplir su objetivo, pero solo si no contradice el texto del usuario.

Responde ÚNICAMENTE con un JSON válido, sin texto adicional:

{{
  "current_skills": ["habilidad1", "habilidad2"],
  "goal_skills": ["habilidad3", "habilidad4"]
}}

- Las habilidades deben coincidir EXACTAMENTE con los nombres de la lista proporcionada.  
- Si una habilidad inferida no está en la lista, omítela.  
- Si el usuario no menciona ninguna habilidad actual u objetivo, devuelve lista vacía.

Lista de habilidades disponibles:
{skills_list}

"""

def interpret_goal(user_text: str, available_skills: Set[str], llm_client: LLMClient) -> dict:
    skills_str = ", ".join(sorted(available_skills))
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(skills_list=skills_str)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text}
    ]
    response_text = llm_client.generate_answer(messages)
    current, goal = parse_output(response_text, available_skills)  
    return {"current_skills": current, "goal_skills": goal}

def parse_output(response_text: str, available_skills: Set[str]):
    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = response_text[start:end]
            data = json.loads(json_str)
        else:
            raise ValueError("No se encontró JSON")
    except Exception as e:
        logger.error(f"Error parseando JSON: {e}\nRespuesta: {response_text}")
        return [], []   # devolver tupla de listas vacías
    
    current = [s for s in data.get("current_skills", []) if s in available_skills]
    goal = [s for s in data.get("goal_skills", []) if s in available_skills]
    
    if len(current) != len(data.get("current_skills", [])):
        logger.warning("Algunas habilidades actuales no estaban en la lista disponible")
    if len(goal) != len(data.get("goal_skills", [])):
        logger.warning("Algunas habilidades objetivo no estaban en la lista disponible")
    
    return current, goal
