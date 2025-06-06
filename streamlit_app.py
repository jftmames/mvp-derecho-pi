import streamlit as st
import pandas as pd
import json
import graphviz

# ... (resto de imports sin cambios)
from cd_modules.core.extractor_conceptual import extraer_conceptos
from cd_modules.core.inquiry_engine import InquiryEngine
from cd_modules.core.contextual_generator import generar_contexto
from cd_modules.core.pathrag_pi import recuperar_fragmentos

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Demo PI - Código Deliberativo", layout="wide")
st.title("📚 Demo MVP - Derecho de la Propiedad Intelectual")
st.markdown("Esta demo simula razonamiento jurídico automatizado, con validación epistémica visible.")

# ... (Guía para el evaluador sin cambios)

# --- CACHES PARA MEJORAR RENDIMIENTO ---
# ... (get_conceptos, get_fragmentos, get_tree sin cambios)
@st.cache_data(show_spinner="Extrayendo conceptos...")
def get_conceptos(pregunta: str):
    return extraer_conceptos(pregunta)

@st.cache_data(show_spinner="Recuperando fragmentos...")
def get_fragmentos(pregunta: str, top_k: int = 3):
    return recuperar_fragmentos(pregunta, top_k)

@st.cache_data(show_spinner="Generando árbol de razonamiento...")
def get_tree(pregunta: str, max_depth: int, max_width: int):
    ie = InquiryEngine(pregunta, max_depth=max_depth, max_width=max_width)
    return ie.generate()


# --- DECLARACIÓN DE VALOR (sin cambios) ---
# ...

# --- SIDEBAR: INPUTS DEL USUARIO ---
st.sidebar.header("⚙️ Configuración del árbol")

# AÑADIDO: Campo para la clave de API de OpenAI
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Introduce tu clave de API de OpenAI para activar la generación de contexto.")

pregunta_input = st.sidebar.text_input("Pregunta principal", "¿Quién puede ser autor de una obra?")
max_depth = st.sidebar.slider("Profundidad", 1, 3, 2)
max_width = st.sidebar.slider("Anchura", 1, 4, 2)
example = st.sidebar.selectbox(
    "Ejemplos de consulta",
    ["Ninguno", "Patente software IA", "Marca sonora España", "Convenios internacionales derechos autor"]
)

if example != "Ninguno":
    templates = {
        "Patente software IA": "¿Es patentable un software de IA para reconocimiento de voz en España?",
        "Marca sonora España": "¿Qué protección tiene una marca sonora registrada en España?",
        "Convenios internacionales derechos autor": "¿Qué convenios internacionales regulan el derecho de autor en España?"
    }
    pregunta = templates[example]
else:
    pregunta = pregunta_input

# --- EJECUCIÓN DEL PIPELINE ---
conceptos = get_conceptos(pregunta)
frags = get_fragmentos(pregunta, top_k=3)
tree = get_tree(pregunta, max_depth, max_width)

# --- Sesión para tracker (sin cambios) ---
# ...

# --- Funciones Auxiliares (sin cambios) ---
# ...

def generar_todo(tree, api_key): # MODIFICADO: Acepta la API Key
    if not api_key:
        st.error("Por favor, introduce una clave de API de OpenAI para generar el contexto.")
        return
    with st.spinner("Generando contexto para TODOS los nodos con OpenAI..."):
        def gen(hijos):
            for nodo, subhijos in hijos.items():
                if not esta_respondido(nodo):
                    data = generar_contexto(nodo, openai_api_key=api_key) # MODIFICADO
                    st.session_state.tracker.append({
                        "Subpregunta": nodo,
                        "Contexto": data["contexto"],
                        "Fuente": data["fuente"],
                        "Validación": data.get("validacion", "no validada")
                    })
                gen(subhijos)
        for raiz, hijos in tree.items():
            if not esta_respondido(raiz):
                data = generar_contexto(raiz, openai_api_key=api_key) # MODIFICADO
                st.session_state.tracker.append({
                    "Subpregunta": raiz,
                    "Contexto": data["contexto"],
                    "Fuente": data["fuente"],
                    "Validación": data.get("validacion", "no validada")
                })
            gen(hijos)
    st.rerun()

# --- Funciones para Grafo (sin cambios) ---
# ...

# --- BOTÓN DE REINICIO (sin cambios) ---
# ...

# --- Renderizado de la App ---
st.divider()

col_izq, col_der = st.columns(2)
# ... (Conceptos y Fragmentos sin cambios)

st.divider()
st.subheader("🌳 Árbol de Razonamiento Jurídico")
mostrar_grafo(tree)

# --- MOSTRAR DETALLES Y ACCIONES (VISTA TEXTO) ---
with st.expander("🔍 Ver Detalles y Generar Contexto (Vista de Texto)"):
    for raiz, hijos in tree.items():
        def mostrar_detalle(nodo, sub, nivel=0):
            # ... (Lógica de visualización del nodo sin cambios)
            margen = "  " * nivel
            data = next((x for x in st.session_state.tracker if x["Subpregunta"] == nodo), None)
            with st.container():
                c1, c2 = st.columns([0.9, 0.1])
                c1.markdown(f"{margen}🔹 **{nodo}**")
                if data:
                    c2.markdown(badge_validacion(data["Validación"]), unsafe_allow_html=True)
                st.markdown(f"{margen}---")
                if data:
                    st.info(f"{margen}📘 *{data['Contexto']}*")
                    fuente_texto = data.get('Fuente', '')
                    if fuente_texto and fuente_texto.startswith("http"):
                        st.markdown(f"{margen}🔗 **Fuente:** [{fuente_texto}]({fuente_texto})")
                    elif fuente_texto:
                        st.markdown(f"{margen}🔗 **Fuente:** {fuente_texto}")
                else:
                    # MODIFICADO: Se deshabilita el botón si no hay API Key
                    if st.button(f"🧠 Generar contexto", key=f"gen_{nodo}", disabled=not openai_api_key):
                        with st.spinner(f"Generando contexto para '{nodo}' con OpenAI..."):
                            nuevo = generar_contexto(nodo, openai_api_key=openai_api_key) # MODIFICADO
                            st.session_state.tracker.append({
                                "Subpregunta": nodo,
                                "Contexto": nuevo["contexto"],
                                "Fuente": nuevo["fuente"],
                                "Validación": nuevo.get("validacion","no validada")
                            })
                        st.rerun()
                st.markdown(f"{margen}---")

            for h, s in sub.items():
                mostrar_detalle(h, s, nivel+1)
        mostrar_detalle(raiz, hijos)

# ... (Resto de la app con una modificación clave en el botón "Generar TODO")
st.divider()

total = contar_nodos(tree)
resp = contar_respondidos()
colp, colb = st.columns([6,4])
ratio = resp/total if total else 0
colp.progress(min(max(ratio, 0.0), 1.0), text=f"Progreso: {resp}/{total}")

# MODIFICADO: Se deshabilita el botón si no hay API Key y se le pasa la key
colb.button("🧠 Generar TODO el contexto", on_click=generar_todo, args=(tree, openai_api_key), type="primary", use_container_width=True, disabled=not openai_api_key)

st.divider()

# ... (El resto del fichero de la app no tiene más cambios)
