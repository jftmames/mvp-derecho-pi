# File: cd_modules/core/pathrag_pi.py

def recuperar_fragmentos(pregunta: str, top_k: int = 3) -> list[dict]:
    """
    Stub que simula la recuperación RAG.
    Reemplázalo con la implementación real de PathRAG cuando esté disponible.
    :param pregunta: Texto de la consulta.
    :param top_k: Número de fragmentos a devolver.
    :return: Lista de diccionarios con keys 'titulo', 'fragmento', 'url'.
    """
    ejemplos = [
        {
            "titulo": "Ley 24/2015, Art. 4.5",
            "fragmento": "En España, el software como tal no es patentable salvo que aporte una contribución técnica.",
            "url": "https://www.boe.es/buscar/act.php?id=BOE-A-2015-5484"
        },
        {
            "titulo": "Sentencia CJEU 2014/C-406/13",
            "fragmento": "El CJEU aclara que la idea subyacente no es patentable si no cumple requisitos técnicos.",
            "url": "https://curia.europa.eu/juris/document/document.jsf?text=&docid=152062"
        },
        {
            "titulo": "OEPM - Guía de Patentes",
            "fragmento": "La Oficina Española de Patentes y Marcas establece que el software necesita elemento técnico adicional.",
            "url": "https://www.oepm.es/es/patentes"
        }
    ]
    return ejemplos[:top_k]
