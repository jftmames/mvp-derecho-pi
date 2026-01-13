import json
import os
from openai import OpenAI
# Importamos el motor RAGA que creaste en el Sprint 1
from cd_modules.core.raga_engine import RAGAEngine

class InquiryEngine:
    def __init__(self, topic, max_depth=2, max_width=2, raga_engine=None):
        """
        :param topic: Pregunta inicial del usuario.
        :param raga_engine: Instancia de RAGAEngine ya cargada con datos.
        """
        self.topic = topic
        self.max_depth = max_depth
        self.max_width = max_width
        self.tree = {}
        # Si no nos pasan un motor, intentamos inicializar uno por defecto
        self.raga = raga_engine if raga_engine else RAGAEngine()
        
        # Configuración del cliente OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def _get_raga_context(self, query):
        """Recupera fragmentos de ley reales para fundamentar la pregunta."""
        if not self.raga or not self.raga.vector_store:
            return "No hay base de conocimientos cargada. Usa conocimiento general."
        
        results = self.raga.retrieve(query, k=2) # Recuperamos los 2 fragmentos más relevantes
        context_str = "\n".join([f"- (Fuente: {r['source']}): {r['content']}" for r in results])
        return context_str

    def _generate_subquestions(self, parent_question, current_depth):
        """Genera sub-preguntas BASADAS en el contexto legal recuperado."""
        if not self.client:
            return ["(Error: Sin API Key)"]

        # PASO CRÍTICO: GROUNDING (Anclaje)
        # Antes de preguntar a GPT, le damos la ley.
        contexto_legal = self._get_raga_context(parent_question)

        prompt = f"""
        Actúa como un Auditor Jurídico experto en AI Act.
        
        OBJETIVO: Desglosar la pregunta "{parent_question}" en {self.max_width} sub-preguntas lógicas para una auditoría.
        
        CONTEXTO LEGAL OBLIGATORIO (RAGA):
        {contexto_legal}
        
        REGLAS:
        1. Las sub-preguntas deben verificar si se cumple lo que dice el texto legal arriba citado.
        2. No inventes normas. Básate solo en el contexto provisto.
        3. Salida estrictamente en formato JSON: {{ "questions": ["¿Pregunta 1?", "¿Pregunta 2?"] }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", # O gpt-3.5-turbo si prefieres ahorrar
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2 # Baja temperatura para mayor rigor
            )
            data = json.loads(response.choices[0].message.content)
            return data.get("questions", [])
        except Exception as e:
            print(f"Error generando subpreguntas: {e}")
            return []

    def build_tree(self, current_node, depth):
        """Construye el árbol recursivamente usando RAGA en cada nodo."""
        if depth >= self.max_depth:
            return {}

        subquestions = self._generate_subquestions(current_node, depth)
        branches = {}
        
        for sq in subquestions:
            # Recursividad: Para cada respuesta, profundizamos
            branches[sq] = self.build_tree(sq, depth + 1)
            
        return branches

    def generate(self):
        """Método principal para lanzar la generación."""
        print(f"🌳 Iniciando Deliberación RAGA sobre: {self.topic}")
        self.tree = {self.topic: self.build_tree(self.topic, 0)}
        return self.tree
