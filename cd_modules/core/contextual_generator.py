# cd_modules/core/contextual_generator.py

from cd_modules.core.pathrag_pi import recuperar_nodo_relevante
from cd_modules.core.validador_epistemico import validar_contexto

def generar_contexto(nodo):
    """
    Simula la generación contextual legal.
    """
    info = recuperar_nodo_relevante(nodo)
    ejemplo = ""

    if info["nodo"] == "Autoría en PI":
        ejemplo = "Según la Ley de Propiedad Intelectual, puede ser autor cualquier persona física que cree una obra original."
    elif info["nodo"] == "Obra colectiva":
        ejemplo = "Una obra colectiva es aquella creada por iniciativa y bajo la coordinación de una persona física o jurídica."
    else:
        ejemplo = "La propiedad intelectual protege obras originales en el ámbito literario, artístico o científico."

    validacion = validar_contexto(nodo, ejemplo)

    return {
        "contexto": ejemplo,
        "fuente": f"Grafo PI → {' → '.join(info['camino'])}",
        "validacion": validacion
    }
