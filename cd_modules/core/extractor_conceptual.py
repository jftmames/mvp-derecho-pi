# File: cd_modules/core/extractor_conceptual.py

import re

# Lista muy básica de términos PI (puedes ampliarla)
KEYWORDS = [
    "patente", "software", "IA", "marca", "sonora", "diseño", "industrial",
    "derecho", "autor", "copyright", "UE", "España", "CJEU", "BOE", "OEPM"
]

def extraer_conceptos(texto: str) -> list[str]:
    """
    Extrae conceptos clave buscando keywords y sustantivos compuestos.
    Mucho más ligero que spaCy, ideal para despliegue rápido.
    """
    texto_lower = texto.lower()
    encontrados = set()

    # 1) Keywords explícitas
    for kw in KEYWORDS:
        if kw.lower() in texto_lower:
            encontrados.add(kw)

    # 2) Tokens compuestos (2–3 palabras) como "reconocimiento de voz"
    for match in re.finditer(r"\\b([a-záéíóúñ]+(?:\\s+de)?(?:\\s+[a-záéíóúñ]+)?)\\b", texto_lower):
        token = match.group(1).strip()
        # descartamos stopwords muy comunes
        if token not in ("de", "la", "el", "y", "en", "para") and len(token) > 4:
            encontrados.add(token)

    return list(encontrados)
