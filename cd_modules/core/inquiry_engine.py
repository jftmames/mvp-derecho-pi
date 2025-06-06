# cd_modules/core/inquiry_engine.py

from cd_modules.core.extractor_conceptual import extraer_conceptos
import itertools

# Plantillas de preguntas jurídicas para generar sub-preguntas contextualmente relevantes.
# Se sustituye la lista de ejemplos aleatorios por un sistema basado en plantillas y conceptos.
QUESTION_TEMPLATES = [
    "¿Cuál es la regulación específica para '{concept}' en la legislación española?",
    "¿Qué jurisprudencia relevante del Tribunal Supremo o del TJUE existe sobre '{concept}'?",
    "¿Qué requisitos específicos de protección se aplican a '{concept}'?",
    "¿Cuáles son las excepciones o límites aplicables a los derechos sobre '{concept}'?",
    "¿Cómo se protege un '{concept}' a nivel de la Unión Europea?",
    "¿Qué tratados internacionales firmados por España afectan a la regulación de '{concept}'?"
]

class InquiryEngine:
    def __init__(self, pregunta, max_depth=2, max_width=2):
        self.pregunta = pregunta
        self.max_depth = max_depth
        self.max_width = max_width

    def _expand(self, nodo: str, depth: int) -> dict:
        """
        Método de expansión mejorado.
        Extrae conceptos del nodo y genera preguntas específicas usando las plantillas.
        """
        if depth >= self.max_depth:
            return {}

        # 1. Extraer conceptos clave del nodo actual (pregunta)
        conceptos = extraer_conceptos(nodo)
        if not conceptos:
            return {} # Si no hay conceptos, no se puede expandir

        # 2. Generar todas las sub-preguntas posibles a partir de los conceptos y plantillas
        subpreguntas_generadas = []
        for concept in conceptos:
            for template in QUESTION_TEMPLATES:
                subpreguntas_generadas.append(template.format(concept=concept))
        
        # 3. Limitar el número de sub-preguntas según max_width para no saturar el árbol
        # Se usa un ciclo para tomar preguntas de forma distribuida entre los conceptos
        hijos = {}
        preguntas_finales = list(itertools.islice(itertools.cycle(subpreguntas_generadas), self.max_width))
        
        for subpregunta in sorted(list(set(preguntas_finales))): # Usamos set para evitar duplicados exactos
            hijos[subpregunta] = self._expand(subpregunta, depth + 1)
            
        return hijos

    def generate(self):
        """
        Genera el árbol de razonamiento completo a partir de la pregunta inicial.
        """
        return {self.pregunta: self._expand(self.pregunta, 0)}
