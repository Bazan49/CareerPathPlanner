import json
from src.llm.llm_client import LLMClient

PROMPT = """
Eres un experto en planificación educativa. Genera una base de conocimientos del dominio profesional: "{domain}". 
Debes generar exactamente {num_skills} habilidades relevantes para este dominio.

Para cada habilidad, proporciona:
- name: nombre exacto de la habilidad.
- level: número entero (0 = básico, 1 = intermedio, 2 = avanzado, 3 = experto).
- requires: lista de nombres de habilidades que son prerequisitos directos (subconjunto de las habilidades generadas, con nivel estrictamente menor). Las habilidades de nivel 0 tienen lista vacía.
- description: breve descripción (opcional, máximo 80 caracteres).

Además, debes incluir un campo "skill_groups": una lista de listas de nombres de habilidades que tienen sentido enseñar juntas en un mismo curso (por ejemplo, porque son complementarias o suelen aparecer juntas en programas de estudio reales).

Asegúrate de que la estructura sea jerárquica, sin ciclos, y que los grupos sean coherentes con los niveles y prerequisitos. Responde ÚNICAMENTE con un objeto JSON válido con esta estructura:

{{
  "domain": "{domain}",
  "skills": [
    {{"name": "...", "level": 0, "requires": [], "description": "..."}},
    ...
  ],
  "skill_groups": [
    ["habilidadA", "habilidadB"],
    ["habilidadC", "habilidadD", "habilidadE"],
    ...
  ]
}}
"""

def generate_domain_knowledge(domain: str, num_skills: int = 20) -> dict:
    prompt =  PROMPT.format(domain=domain, num_skills=num_skills)
    llm = LLMClient()
    response = llm.generate_answer([{"role": "user", "content": prompt}])
    # Extraer JSON
    print("Respuesta del LLM recibida. Procesando JSON...")
    start = response.find('{')
    end = response.rfind('}') + 1
    json_str = response[start:end]
    return json.loads(json_str)
