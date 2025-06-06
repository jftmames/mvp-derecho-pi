# File: cd_modules/core/contextual_generator.py

from cd_modules.core.pathrag_pi import recuperar_fragmentos
from cd_modules.core.validador_epistemico import validar_contexto

# Imports para la integración con OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser


def generar_contexto(nodo: str, openai_api_key: str) -> dict:
    """
    Genera el contexto legal para un nodo.
    Primero intenta un pipeline RAG. Si no encuentra fragmentos,
    recurre al conocimiento general de OpenAI como fallback.

    :param nodo: Subpregunta o concepto a contextualizar.
    :param openai_api_key: La clave de API para autenticarse con OpenAI.
    :return: Diccionario con el contexto generado, la fuente y la validación.
    """
    # 1. INTENTO DE RECUPERACIÓN (RAG)
    frags = recuperar_fragmentos(nodo, top_k=2)
    
    # Inicializamos el modelo de OpenAI para usarlo en cualquiera de los dos casos
    modelo = ChatOpenAI(temperature=0.2, model="gpt-4o", openai_api_key=openai_api_key)

    if frags:
        # --- CASO 1: ÉXITO EN RAG (HAY FRAGMENTOS) ---
        
        # Preparamos el contexto recuperado para pasarlo al modelo
        contexto_rag = "\n\n".join([f"Fuente: {f['titulo']}\nFragmento: {f['fragmento']}" for f in frags])
        fuentes_combinadas = ", ".join([f['titulo'] for f in frags])
        urls = frags[0]['url'] # Tomamos la primera URL como referencia principal

        # Definimos la plantilla del prompt para RAG
        template_rag = """
        Eres un asistente legal experto en Derecho de la Propiedad Intelectual en España.
        Tu tarea es responder a la pregunta del usuario de forma clara, técnica y concisa.
        Usa EXCLUSIVAMENTE la información proporcionada en los siguientes "Fragmentos de fuentes".
        No añadas ninguna información que no provenga directamente de estos textos.
        Si los fragmentos no son suficientes para responder, indícalo explícitamente.

        Fragmentos de fuentes:
        {contexto_rag}

        Pregunta del usuario:
        {pregunta}

        Respuesta:
        """
        prompt = PromptTemplate(
            input_variables=["contexto_rag", "pregunta"],
            template=template_rag
        )

        chain = prompt | modelo | StrOutputParser()

        contexto_generado = chain.invoke({
            "contexto_rag": contexto_rag,
            "pregunta": nodo
        })

        # Realizamos la validación sobre el texto original recuperado
        validacion = validar_contexto(nodo, contexto_rag)

        return {
            "contexto": contexto_generado,
            "fuente": f"{fuentes_combinadas} (vía {urls})",
            "validacion": validacion,
            "camino": [f['titulo'] for f in frags]
        }
    else:
        # --- CASO 2: FALLO EN RAG (NO HAY FRAGMENTOS) -> FALLBACK A IA GENERAL ---
        
        # Definimos una plantilla de prompt diferente para el modo de conocimiento general
        template_no_rag = """
        Eres un asistente legal experto en Derecho de la Propiedad Intelectual en España.
        No se han encontrado fuentes específicas en la base de datos para la siguiente pregunta.
        Por favor, responde a la pregunta basándote en tu conocimiento general sobre el tema.
        Al final de tu respuesta, añade una nota de advertencia que diga: 
        "Nota: Esta respuesta se basa en conocimiento general y no ha sido verificada contra el corpus documental específico de esta aplicación."

        Pregunta del usuario:
        {pregunta}

        Respuesta:
        """
        prompt = PromptTemplate(
            input_variables=["pregunta"],
            template=template_no_rag
        )

        chain = prompt | modelo | StrOutputParser()
        
        contexto_generado = chain.invoke({
            "pregunta": nodo
        })

        return {
            "contexto": contexto_generado,
            "fuente": "Conocimiento General de OpenAI (No Verificado)",
            "validacion": "no validada",
            "camino": []
        }
