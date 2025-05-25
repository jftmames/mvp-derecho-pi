# cd_modules/core/validador_epistemico.py

def validar_contexto(nodo, contexto):
    """
    Simula validación epistémica:
    - Si contiene 'Ley', se valida.
    - Si contiene 'según doctrina', parcial.
    - Si no, no validada.
    """
    if "Ley" in contexto:
        return "validada"
    elif "doctrina" in contexto.lower():
        return "parcial"
    else:
        return "no validada"
