# File: cd_modules/core/extractor_conceptual.py

import spacy

# Cargamos el modelo pequeño de español
# (asegúrate de haberlo instalado: python -m spacy download es_core_news_sm)
nlp = spacy.load("es_core_news_sm")

def extraer_conceptos(texto: str) -> list[str]:
    """
    Extrae conceptos clave de un texto usando entidades nombradas.
    :param texto: La pregunta o enunciado en español.
    :return: Lista de conceptos (palabras o entidades) relevantes para PI.
    """
    doc = nlp(texto)
    conceptos = set()

    # Entidades nombradas
    for ent in doc.ents:
        conceptos.add(ent.text)

    # Sustantivos propios y comunes (pos_tag PROPN y NOUN)
    for token in doc:
        if token.pos_ in ("PROPN", "NOUN") and not token.is_stop and len(token.text) > 2:
            conceptos.add(token.lemma_)

    # Devuelve una lista ordenada
    return list(conceptos)
