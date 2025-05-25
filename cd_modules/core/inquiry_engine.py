# cd_modules/core/inquiry_engine.py

import random

class InquiryEngine:
    def __init__(self, pregunta, max_depth=2, max_width=2):
        self.pregunta = pregunta
        self.max_depth = max_depth
        self.max_width = max_width

    def _expand(self, nodo, depth):
        if depth >= self.max_depth:
            return {}

        ejemplos = [
            "¿Qué requisitos legales se aplican?",
            "¿Existen excepciones jurisprudenciales?",
            "¿Qué doctrina relevante se ha pronunciado?",
            "¿Qué dice la legislación europea?",
            "¿Cómo lo regula la Ley de Propiedad Intelectual?",
            "¿Qué derechos derivan de esta situación?"
        ]

        hijos = {}
        opciones = random.sample(ejemplos, k=min(self.max_width, len(ejemplos)))
        for i, ejemplo in enumerate(opciones):
            subpregunta = f"{ejemplo} ({nodo})"
            hijos[subpregunta] = self._expand(subpregunta, depth + 1)
        return hijos

    def generate(self):
        return {self.pregunta: self._expand(self.pregunta, 0)}
