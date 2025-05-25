class EpistemicNavigator:
    """
    Navegador epistémico stub: simula una búsqueda de fuentes jurídicas relevantes.
    Puede ampliarse con embeddings o integración real más adelante.
    """

    def __init__(self):
        # En el futuro: inicializa aquí la base de conocimiento o embeddings
        pass

    def search(self, query, k=3):
        """
        Simula la búsqueda de las k fuentes más relevantes para una consulta.
        Devuelve una lista de tuplas: (extracto/fragmento, score)
        """
        resultados = [
            (f"Extracto jurídico de ejemplo relacionado con: {query}", 0.92),
            (f"Otro fragmento relevante sobre: {query}", 0.85),
            (f"Jurisprudencia simulada para: {query}", 0.81)
        ]
        return resultados[:k]
