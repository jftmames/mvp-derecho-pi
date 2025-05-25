# File: cd_modules/core/contextual_generator.py

from cd_modules.core.pathrag_pi import recuperar_fragmentos
from cd_modules.core.validador_epistemico import validar_contexto


def generar_contexto(nodo: str) -> dict:
    """
    Genera el contexto legal para un nodo concreto usando PathRAG y valida la coherencia.

    :param nodo: Subpregunta o concepto a contextualizar.
    :return: Diccionario con claves:
        - contexto: fragmento legal recuperado.
        - fuente: URL de la fuente oficial.
        - validacion: resultado de la validación epistémica.
        - camino: lista de títulos de fuentes consultadas.
    """
    # Recuperamos el fragmento más relevante
    frags = recuperar_fragmentos(nodo, top_k=1)
    if frags:
        frag = frags[0]
        contexto = frag.get("fragmento", "")
        fuente = frag.get("url", "")
        camino = [frag.get("titulo", nodo)]
    else:
        contexto = "No se encontró información relevante para este concepto."
        fuente = ""
        camino = []

    # Validación epistémica: comprueba respaldo en ontología/corpus
    validacion = validar_contexto(nodo, contexto)

    return {
        "contexto": contexto,
        "fuente": fuente,
        "validacion": validacion,
        "camino": camino
    }
