import json
import logging
from typing import Set
from src.llm.llm_client import LLMClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """
Eres un asistente de planificación profesional. Tu tarea es inferir, a partir de la descripción del usuario, dos conjuntos de habilidades:

1. Habilidades que el usuario YA POSEE (current_skills).  
   - Infiere incluso si no las menciona explícitamente según tu conocimiento.  
   - Si no hay información, devuelve lista vacía.

2. Habilidades que el usuario DESEA ALCANZAR (goal_skills).  
   - Infiere a partir de aspiraciones si no las menciona explícitamente según tu conocimiento.    
   - Si no hay aspiraciones, devuelve lista vacía.
 
Debes responder ÚNICAMENTE con un objeto JSON válido, sin texto adicional, con esta estructura:

{{
  "current_skills": ["habilidad1", "habilidad2"],
  "goal_skills": ["habilidad3", "habilidad4"]
}}

Usa tu conocimiento para mapear términos comunes a las habilidades exactas de la lista que se te proporciona. 
Las habilidades deben coincidir EXACTAMENTE (incluyendo mayúsculas) con las de la lista de habilidades disponibles que se te proporciona abajo. Si una habilidad inferida no está en la lista, no la incluyas.

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