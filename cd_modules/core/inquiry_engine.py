import json
import os
from openai import OpenAI
from cd_modules.core.raga_engine import RAGAEngine


class InquiryEngine:
    """Generador de árboles de indagación con grounding legal."""

    def __init__(
        self,
        topic: str,
        max_depth: int = 2,
        max_width: int = 2,
        raga_engine: RAGAEngine | None = None,
    ) -> None:
        """
        :param topic: Pregunta inicial del usuario.
        :param max_depth: Nivel máximo de profundidad del árbol.
        :param max_width: Número máximo de sub‑preguntas por nodo.
        :param raga_engine: Instancia de ``RAGAEngine`` ya cargada con datos.
        """
        self.topic = topic
        self.max_depth = max_depth
        self.max_width = max_width
        self.tree: dict[str, dict] = {}
        # Si no nos pasan un motor, intentamos inicializar uno por defecto
        self.raga = raga_engine if raga_engine else RAGAEngine()

        # Configuración del cliente OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def _get_raga_context(self, query: str) -> str:
        """
        Recupera fragmentos de ley reales para fundamentar la pregunta.

        :param query: Pregunta a contrastar con la base legal.
        :return: Cadena con contexto legal formateado.
        """
        if not self.raga or not self.raga.vector_store:
            return "No hay base de conocimientos cargada. Usa conocimiento general."

        results = self.raga.retrieve(query, k=2)  # Recuperamos los 2 fragmentos más relevantes
        context_str = "\n".join(
            [f"- (Fuente: {r['source']}): {r['content']}" for r in results]
        )
        return context_str

    def _generate_subquestions(self, parent_question: str, current_depth: int) -> list[str]:
        """
        Genera sub‑preguntas basadas en el contexto legal recuperado.

        :param parent_question: Pregunta desde la que se desprenden las sub‑preguntas.
        :param current_depth: Nivel actual en el árbol.
        :return: Lista de sub‑preguntas.
        """
        if not self.client:
            return ["(Error: Sin API Key)"]

        # PASO CRÍTICO: GROUNDING (Anclaje)
        # Antes de preguntar a GPT, le damos la ley.
        contexto_legal = self._get_raga_context(parent_question)

        prompt = f"""
        Actúa como un Auditor Jurídico experto en AI Act.

        OBJETIVO: Desglosar la pregunta "{parent_question}" en {self.max_width} sub‑preguntas lógicas para una auditoría.

        CONTEXTO LEGAL OBLIGATORIO (RAGA):
        {contexto_legal}

        REGLAS:
        1. Las sub‑preguntas deben verificar si se cumple lo que dice el texto legal arriba citado.
        2. No inventes normas. Básate solo en el contexto provisto.
        3. Salida estrictamente en formato JSON: {{ "questions": ["¿Pregunta 1?", "¿Pregunta 2?"] }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # O gpt-3.5-turbo si prefieres ahorrar
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,  # Baja temperatura para mayor rigor
            )
            data = json.loads(response.choices[0].message.content)
            return data.get("questions", [])
        except Exception as e:
            print(f"Error generando subpreguntas: {e}")
            return []

    def build_tree(self, current_node: str, depth: int) -> dict:
        """
        Construye el árbol de indagación de manera recursiva.

        :param current_node: Pregunta actual desde la que generar ramas.
        :param depth: Profundidad actual.
        :return: Diccionario representando las ramas hijas de ``current_node``.
        """
        if depth >= self.max_depth:
            return {}

        subquestions = self._generate_subquestions(current_node, depth)
        branches: dict[str, dict] = {}

        for sq in subquestions:
            # Recursividad: Para cada sub‑pregunta, profundizamos
            branches[sq] = self.build_tree(sq, depth + 1)

        return branches

    def generate(self) -> dict:
        """
        Método principal para lanzar la generación de árbol.
        
        :return: Árbol de deliberación completo con ``self.topic`` como raíz.
        """
        print(f"🌳 Iniciando Deliberación RAGA sobre: {self.topic}")
        self.tree = {self.topic: self.build_tree(self.topic, 0)}
        return self.tree
