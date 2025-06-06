# File: cd_modules/core/contextual_generator.py

# Se elimina la importación de 'recuperar_fragmentos' y 'validar_contexto' ya que no se usarán.

# Imports para la integración con OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser


def generar_contexto(nodo: str, openai_api_key: str) -> dict:
    """
    Genera el contexto legal para un nodo usando directamente el conocimiento
    general de un modelo de OpenAI.

    :param nodo: Subpregunta o concepto a contextualizar.
    :param openai_api_key: La clave de API para autenticarse con OpenAI.
    :return: Diccionario con el contexto generado por la IA.
    """
    
    # Se define la plantilla del prompt para que la IA responda desde su conocimiento general.
    template = """
    Eres un asistente legal experto en Derecho de la Propiedad Intelectual en España.
    Responde a la siguiente pregunta basándote en tu conocimiento general sobre el tema de forma clara, técnica y concisa.

    Pregunta del usuario:
    {pregunta}

    Respuesta:
    """
    prompt = PromptTemplate(
        input_variables=["pregunta"],
        template=template
    )

    # Inicializamos el modelo de OpenAI
    # Usamos una temperatura de 0.2 para un equilibrio entre creatividad y objetividad.
    modelo = ChatOpenAI(temperature=0.2, model="gpt-4o", openai_api_key=openai_api_key)

    # Creamos el pipeline (chain) de LangChain
    chain = prompt | modelo | StrOutputParser()

    # Invocamos la cadena con la pregunta del usuario
    contexto_generado = chain.invoke({
        "pregunta": nodo
    })
    
    # Como la respuesta no se basa en un documento, la fuente y la validación son fijas.
    return {
        "contexto": contexto_generado,
        "fuente": "Conocimiento General de OpenAI",
        "validacion": "no validada",
        "camino": []
    }
