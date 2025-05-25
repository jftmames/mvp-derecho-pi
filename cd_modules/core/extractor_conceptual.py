# File: cd_modules/core/extractor_conceptual.py

import re

# Lista básica de términos PI (puedes ampliarla)
KEYWORDS = [
    "patente", "software", "ia", "marca", "sonora", "diseño", "industrial",
    "derecho", "autor", "copyright", "ue", "españa", "cjeu", "boe", "oepm"
]

def extraer_conceptos(texto: str) -> list[str]:
    """
    Extrae conceptos clave buscando keywords y tokens compuestos ligeros.
    Mucho más rápido y sin dependencias externas.
    """
    texto_low = texto.lower()
    encontrados = set()

    # 1) Buscamos keywords
    for kw in KEYWORDS:
        if kw in texto_low:
            encontrados.add(kw)

    # 2) Tokens de 2–3 palabras (e.g. 'reconocimiento de voz')
    for match in re.finditer(r"\b([a-záéíóúñ]+(?:\s+de)?(?:\s+[a-záéíóúñ]+)?)\b", texto_low):
        token = match.group(1).strip()
        if len(token) > 4 and token not in ("de", "la", "el", "y", "en", "para"):
            encontrados.add(token)

    return list(encontrados)
