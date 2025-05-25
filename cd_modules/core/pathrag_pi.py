# cd_modules/core/pathrag_pi.py

def recuperar_nodo_relevante(pregunta):
    """
    Simula búsqueda en grafo PI. Devuelve 'nodo' y ruta conceptual.
    """
    if "autor" in pregunta.lower():
        return {
            "nodo": "Autoría en PI",
            "camino": ["Propiedad Intelectual", "Derechos de autor", "Sujetos"]
        }
    elif "obra colectiva" in pregunta.lower():
        return {
            "nodo": "Obra colectiva",
            "camino": ["Obras", "Clasificación", "Obra colectiva"]
        }
    else:
        return {
            "nodo": "Concepto general de PI",
            "camino": ["Propiedad Intelectual", "Conceptos generales"]
        }
