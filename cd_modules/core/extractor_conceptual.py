# File: cd_modules/core/extractor_conceptual.py

import re

# Lista ampliada de términos PI para una mejor extracción de conceptos.
KEYWORDS = [
    "patente", "software", "ia", "marca", "sonora", "diseño", "industrial",
    "derecho", "autor", "copyright", "ue", "españa", "cjeu", "boe", "oepm",
    "propiedad intelectual", "secreto industrial", "competencia desleal",
    "obra derivada", "convenio de berna", "tratado de la ompi", "obras huérfanas",
    "límites al derecho de autor", "copia privada"
]

def extraer_conceptos(texto: str) -> list[str]:
    """
    Extrae conceptos clave buscando keywords y tokens compuestos.
    La lista de keywords ha sido ampliada para mayor precisión.
    """
    texto_low = texto.lower()
    encontrados = set()

    # 1) Buscamos keywords de la lista ampliada
    for kw in KEYWORDS:
        if kw in texto_low:
            encontrados.add(kw)

    # 2) Buscamos términos compuestos que puedan ser relevantes
    # Esta expresión busca secuencias de 2 a 4 palabras que parezcan conceptos.
    for match in re.finditer(r"\b([a-záéíóúñ]{4,}(?:\s+(?:de|la|el|los|las)\s+)?[a-záéíóúñ]{4,}){1,2}\b", texto_low):
        token = match.group(1).strip()
        if token not in ("de", "la", "el", "y", "en", "para", "qué", "cómo", "cuándo"):
             # Filtro adicional para evitar frases demasiado largas o irrelevantes
            if len(token.split()) <= 4:
                encontrados.add(token)

    # Devuelve una lista única de conceptos encontrados
    return list(encontrados)
