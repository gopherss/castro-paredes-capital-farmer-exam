import openai
import os
import json
from dotenv import load_dotenv
from typing import TypedDict, Union

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class AnalisisIA(TypedDict):
    complejidad: str
    ajuste_precio: int
    servicios_adicionales: list[str]
    propuesta: str

def analizar_con_ia(descripcion: str, tipo_servicio: str) -> Union[AnalisisIA, dict]:
    prompt = f"""
    Analiza este caso legal: {descripcion}
    Tipo de servicio: {tipo_servicio}

    Evalúa:
    1. Complejidad (Baja/Media/Alta)
    2. Ajuste de precio recomendado (0, 25, 50)
    3. Servicios adicionales necesarios
    4. Genera propuesta profesional para cliente

    Devuelve la respuesta en el siguiente formato JSON:

    {{
        "complejidad": "...",
        "ajuste_precio": 0,
        "servicios_adicionales": ["..."],
        "propuesta": "..."
    }}
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # <-- aquí el cambio
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6
        )

        content = response.choices[0].message.content
        if not content:
            return {"error": "La IA no devolvió contenido"}

        # Intentamos parsear el JSON devuelto
        try:
            parsed: AnalisisIA = json.loads(content)
            return parsed
        except json.JSONDecodeError as e:
            return {"error": f"Error al parsear JSON: {str(e)}", "respuesta_cruda": content}

    except Exception as e:
        return {"error": f"Error al llamar a OpenAI: {str(e)}"}
