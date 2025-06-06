# File: cd_modules/core/contextual_generator.py

from cd_modules.core.pathrag_pi import recuperar_fragmentos
from cd_modules.core.validador_epistemico import validar_contexto

# Imports para la integración con OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser


def generar_contexto(nodo: str, openai_api_key: str) -> dict:
    """
    Genera el contexto legal para un nodo usando un pipeline RAG con OpenAI.

    :param nodo: Subpregunta o concepto a contextualizar.
    :param openai_api_key: La clave de API para autenticarse con OpenAI.
    :return: Diccionario con el contexto generado por la IA, la fuente y la validación.
    """
    # 1. RECUPERACIÓN (Retrieval): Obtenemos los fragmentos de nuestra base de datos simulada.
    frags = recuperar_fragmentos(nodo, top_k=2) # Recuperamos 2 para dar más contexto
    
    if frags:
        # Preparamos el contexto recuperado para pasarlo al modelo
        contexto_rag = "\n\n".join([f"Fuente: {f['titulo']}\nFragmento: {f['fragmento']}" for f in frags])
        fuentes_combinadas = ", ".join([f['titulo'] for f in frags])
        urls = frags[0]['url'] # Tomamos la primera URL como referencia principal
    else:
        # Si no hay fragmentos, no podemos generar un contexto fundamentado
        return {
            "contexto": "No se encontró información relevante en las fuentes para responder a esta pregunta.",
            "fuente": "",
            "validacion": "no validada",
            "camino": []
        }

    # 2. GENERACIÓN (Generation): Usamos LangChain y OpenAI para generar la respuesta.

    # Definimos la plantilla del prompt. Es una instrucción clara para la IA.
    template = """
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
        template=template
    )

    # Inicializamos el modelo de OpenAI
    # Usamos una temperatura de 0.0 para que sea lo más determinista y objetivo posible
    modelo = ChatOpenAI(temperature=0.0, model="gpt-4o", openai_api_key=openai_api_key)

    # Creamos el pipeline (chain) de LangChain
    chain = prompt | modelo | StrOutputParser()

    # Invocamos la cadena con la pregunta y el contexto recuperado
    contexto_generado = chain.invoke({
        "contexto_rag": contexto_rag,
        "pregunta": nodo
    })

    # 3. VALIDACIÓN: Realizamos la validación sobre el texto original recuperado, no sobre el generado.
    # Esto mantiene la objetividad de la validación sobre la fuente.
    validacion = validar_contexto(nodo, contexto_rag)

    return {
        "contexto": contexto_generado,
        "fuente": f"{fuentes_combinadas} (vía {urls})",
        "validacion": validacion,
        "camino": [f['titulo'] for f in frags]
    }
