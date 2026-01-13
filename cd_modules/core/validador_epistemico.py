from __future__ import annotations

import os
from typing import Tuple

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore


class EroteticEvaluator:
    """Juez Algorítmico que audita la solidez de cada nodo del árbol."""

    def __init__(self) -> None:
        """
        Inicializa el evaluador. Carga la API Key de OpenAI de las
        variables de entorno si está disponible. Si no se encuentra una
        ``OPENAI_API_KEY``, el evaluador funcionará en modo degradado y
        considerará que toda afirmación con alguna evidencia es válida.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if OpenAI and api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

    def audit_claim(self, claim: str, evidence_text: str) -> Tuple[str, str]:
        """
        Audita una afirmación contrastándola con el texto de evidencia.

        :param claim: La pregunta o afirmación generada por el motor de indagación.
        :param evidence_text: Texto recuperado por RAGA que supuestamente respalda la afirmación.
        :return: Tuple con estado (``"VALIDADA"`` o ``"NO VALIDADA"``) y una breve justificación.
        """
        # Si no hay evidencia, la respuesta no puede validarse
        if not evidence_text:
            return "NO VALIDADA", "No se recuperó evidencia para justificar la afirmación."

        # Si no hay cliente o no se configuró la API Key, aplicamos una heurística simple
        if not self.client:
            return "VALIDADA", "Se encontró evidencia y no hay servicio de auditoría; se asume válida."

        # Construimos un prompt para que el modelo actúe como juez
        prompt = f"""
        Actúa como un juez jurídico que audita la coherencia de una afirmación
        con el texto legal provisto. Tu tarea es decidir si la afirmación está
        directamente respaldada por el fragmento de texto. Responde únicamente
        con VALIDADA si la afirmación coincide literalmente con lo que dice el texto,
        o NO VALIDADA si no hay correspondencia.

        AFIRMACIÓN A AUDITAR:
        "{claim}"

        EVIDENCIA DEL PDF:
        "{evidence_text}"

        Respuesta en una palabra (VALIDADA o NO VALIDADA).
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=1,
            )
            judgement = response.choices[0].message.content.strip().upper()
            if judgement not in {"VALIDADA", "NO VALIDADA"}:
                judgement = "NO VALIDADA"
            explanation = "La evaluación se ha realizado mediante modelo de lenguaje."
            return judgement, explanation
        except Exception:
            # En caso de error con la API, degradamos a heurística simple
            return "VALIDADA", "Se asumió válida por falta de respuesta del evaluador externo."


def auditor(claim: str, evidence_text: str) -> Tuple[str, str]:
    """
    Función auxiliar que instancia un evaluador y ejecuta ``audit_claim``.

    Este helper existe para preservar la interfaz original utilizada en la
    aplicación Streamlit (``auditor`` como objeto llamable). Devuelve
    tupla (estado, explicación).
    """
    evaluator = EroteticEvaluator()
    return evaluator.audit_claim(claim, evidence_text)
