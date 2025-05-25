# File: cd_modules/core/extractor_conceptual.py

import spacy

# Carga el modelo pequeño de español
# (Se instalará desde requirements.txt)
nlp = spacy.load("es_core_news_sm")

def extraer_conceptos(texto: str) -> list[str]:
    """
    Extrae conceptos clave de un texto usando entidades nombradas y sustantivos.
    """
    doc = nlp(texto)
    conceptos = set()

    # Entidades nombradas
    for ent in doc.ents:
        conceptos.add(ent.text)

    # Sustantivos propios y comunes
    for token in doc:
        if token.pos_ in ("PROPN", "NOUN") and not token.is_stop and len(token.text) > 2:
            conceptos.add(token.lemma_)

    return list(conceptos)
