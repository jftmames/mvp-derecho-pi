import os
import json
from openai import OpenAI

class EroteticEvaluator:
    def __init__(self):
        # Configuración del cliente (requiere OPENAI_API_KEY)
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def audit_claim(self, claim, evidence):
        """
        Audita una afirmación comparándola contra la evidencia RAGA.
        
        :param claim: La respuesta o afirmación generada por la IA.
        :param evidence: El texto real recuperado del PDF (contexto).
        :return: Dict con estado (validada/no_validada) y razón.
        """
        if not self.client:
            return {"status": "no validada", "reason": "Error: Sin API Key"}

        if not evidence or len(evidence) < 10:
            return {"status": "no validada", "reason": "Falta de evidencia documental (Grounding insuficiente)."}

        prompt = f"""
        Actúa como un Auditor Forense de IA (H-ANCHOR).
        Tu trabajo es detectar ALUCINACIONES o afirmaciones no soportadas.
        
        EVIDENCIA OFICIAL (GROUND TRUTH):
        \"\"\"{evidence}\"\"\"
        
        AFIRMACIÓN A AUDITAR:
        \"\"\"{claim}\"\"\"
        
        TAREA:
        Verifica si la afirmación está TOTALMENTE RESPALDADA por la evidencia oficial.
        - Si la afirmación menciona datos que NO están en la evidencia -> RECHAZAR (Rojo).
        - Si la afirmación es una inferencia lógica correcta del texto -> VALIDAR (Verde).
        - Si es ambigua -> PARCIAL (Amarillo).
        
        Salida JSON obligatoria:
        {{
            "status": "validada" | "parcial" | "no validada",
            "reason": "Breve explicación técnica de 1 frase."
        }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", 
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"status": "no validada", "reason": f"Error de auditoría: {str(e)}"}

# Instancia global para facilitar importación desde streamlit_app.py
auditor = EroteticEvaluator()
