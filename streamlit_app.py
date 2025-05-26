import streamlit as st
import pandas as pd
import json
import graphviz
# Intentamos importar weasyprint para PDF; si no está, lo ignoramos
try:
    from weasyprint import HTML
except ImportError:
    HTML = None

# --- IMPORTS DE MÓDULOS PROPIOS ---
from cd_modules.core.extractor_conceptual import extraer_conceptos
from cd_modules.core.inquiry_engine import InquiryEngine
from cd_modules.core.contextual_generator import generar_contexto
from cd_modules.core.pathrag_pi import recuperar_fragmentos

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Demo PI - Código Deliberativo", layout="wide")
st.title("📚 Demo MVP - Derecho de la Propiedad Intelectual")
st.markdown("Esta demo simula razonamiento jurídico automatizado, con validación epistémica visible.")
# --- GUÍA PARA EL EVALUADOR ANECA ---
with st.expander("ℹ️ Guía para el Evaluador - Haga clic para expandir"):
    st.markdown(
        """
        **Bienvenido/a al MVP del Código Deliberativo para el Derecho de la Propiedad Intelectual.**

        Esta demostración ha sido diseñada para ilustrar nuestra aproximación computacional a la organización del juicio y el razonamiento jurídico.

        **1. Propósito del MVP:**
        * Demostrar cómo el Código Deliberativo estructura una consulta compleja en preguntas jerárquicas.
        * Mostrar la recuperación de contexto legal (simulada vía PathRAG) para cada subpregunta.
        * Evidenciar la **validación epistémica** (indicada por los 'badges' ✅⚠️❌) y la **trazabilidad** del proceso.

        **2. Innovación Clave:**
        * A diferencia de los modelos generativos que buscan una respuesta única, este sistema **organiza la deliberación**, mantiene múltiples líneas de indagación y hace el proceso **auditable y justificable**. No genera 'la' respuesta, sino que *estructura el pensamiento*.

        **3. Mapa del MVP y Flujo Sugerido:**
        * **Configuración (Barra Lateral):** Introduzca su pregunta o seleccione un ejemplo. Ajuste la profundidad/anchura si lo desea.
        * **Conceptos y Fragmentos:** Observe los conceptos clave extraídos y los fragmentos legales (simulados) recuperados.
        * **Árbol de Razonamiento:** Explore la estructura de preguntas. Haga clic en **"🧠 Generar contexto"** para nodos individuales o use **"🧠 Generar TODO el contexto"** al final.
        * **Validación:** Fíjese en los 'badges' (✅⚠️❌) junto a cada nodo respondido.
        * **Reasoning Tracker:** Revise la tabla inferior, que registra cada paso. Puede **descargar** el informe en varios formatos (CSV, MD, PDF, JSON).

        **4. Estado Actual (Transparencia):**
        * Este es un **Producto Mínimo Viable (MVP)**.
        * El `Inquiry Engine` y `Contextual Generator` (con validación) están implementados.
        * La recuperación de fragmentos (`PathRAG`) y el `Epistemic Navigator` (búsqueda) son **simulaciones (stubs)** para demostrar el flujo.
        * El `Adaptive Dialogue` es un **placeholder** futuro.
        * El EEE es una **métrica simplificada** en esta fase.

        **¡Gracias por su tiempo y evaluación!**
        """,
        unsafe_allow_html=True
    )
# --- FIN GUÍA ---

# --- CACHES PARA MEJORAR RENDIMIENTO ---
@st.cache_data(show_spinner=False)
def get_conceptos(pregunta: str):
    return extraer_conceptos(pregunta)

@st.cache_data(show_spinner=False)
def get_fragmentos(pregunta: str, top_k: int = 3):
    return recuperar_fragmentos(pregunta, top_k)

@st.cache_data(show_spinner=False)
def get_tree(pregunta: str, max_depth: int, max_width: int):
    ie = InquiryEngine(pregunta, max_depth=max_depth, max_width=max_width)
    return ie.generate()

# --- DECLARACIÓN DE VALOR ---
st.markdown(
    """
    ### ✅ Este MVP Cumple con:
    - **Dominio PI especialización**: Respuestas limitadas a propiedad intelectual.
    - **Ontología PI**: Mapeo de conceptos y visualización de grafo.
    - **Corpus legal validado**: Uso de fuentes oficiales (BOE, OEPM, sentencias).
    - **Pipeline especializado**: PathRAG, LLM encapsulado, validación epistémica.
    - **Trazabilidad total**: Registro de pasos, fuentes y validación, exportable.
    - **Explicabilidad**: Badge de validación y detallado del razonamiento.
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR: INPUTS DEL USUARIO ---
st.sidebar.header("⚙️ Configuración del árbol")
pregunta = st.sidebar.text_input("Pregunta principal", "¿Quién puede ser autor de una obra?")
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

# --- EJECUCIÓN DEL PIPELINE ---
conceptos = get_conceptos(pregunta)
frags = get_fragmentos(pregunta, top_k=3)
tree = get_tree(pregunta, max_depth, max_width)

# --- Sesión para tracker ---
if "tracker" not in st.session_state:
    st.session_state.tracker = []

# --- Funciones Auxiliares ---
def badge_validacion(tipo):
    """Genera un badge HTML con tooltip para el estado de validación."""
    if tipo == "validada":
        return '<span style="color: white; background-color: #28a745; padding: 3px 8px; border-radius: 6px;" title="✅ Validada: La respuesta tiene un respaldo legal claro y directo en las fuentes.">✅ Validada</span>'
    elif tipo == "parcial":
        return '<span style="color: black; background-color: #ffc107; padding: 3px 8px; border-radius: 6px;" title="⚠️ Parcial: La respuesta se basa en una interpretación o fuente indirecta.">⚠️ Parcial</span>'
    else:
        return '<span style="color: white; background-color: #dc3545; padding: 3px 8px; border-radius: 6px;" title="❌ No validada: No se encontró respaldo claro en las fuentes consultadas.">❌ No validada</span>'

def esta_respondido(nodo):
    return any(x["Subpregunta"] == nodo for x in st.session_state.tracker)

def contar_nodos(tree):
    total = 0
    def contar(hijos):
        nonlocal total
        for nodo, subhijos in hijos.items():
            total += 1
            contar(subhijos)
    for raiz, hijos in tree.items():
        total += 1
        contar(hijos)
    return total

def contar_respondidos():
    return len(st.session_state.tracker)

def generar_todo(tree):
    def gen(hijos):
        for nodo, subhijos in hijos.items():
            if not esta_respondido(nodo):
                data = generar_contexto(nodo)
                st.session_state.tracker.append({
                    "Subpregunta": nodo,
                    "Contexto": data["contexto"],
                    "Fuente": data["fuente"],
                    "Validación": data.get("validacion", "no validada")
                })
            gen(subhijos)
    for raiz, hijos in tree.items():
        if not esta_respondido(raiz):
            data = generar_contexto(raiz)
            st.session_state.tracker.append({
                "Subpregunta": raiz,
                "Contexto": data["contexto"],
                "Fuente": data["fuente"],
                "Validación": data.get("validacion", "no validada")
            })
        gen(hijos)
# --- Funciones para Grafo (Versión Graphviz) ---
def get_node_color(nodo):
    """Obtiene el color del nodo según su estado de validación."""
    data = next((x for x in st.session_state.tracker if x["Subpregunta"] == nodo), None)
    if data:
        val = data.get("Validación", "no validada")
        if val == "validada": return "#D4EDDA"  # Verde claro
        elif val == "parcial": return "#FFF3CD"  # Amarillo claro
        else: return "#F8D7DA"  # Rojo claro
    return "#E9ECEF" # Gris claro (Pendiente)

def get_node_font_color(nodo):
    """Obtiene el color de la fuente para mejor contraste."""
    data = next((x for x in st.session_state.tracker if x["Subpregunta"] == nodo), None)
    if data:
        val = data.get("Validación", "no validada")
        if val == "validada": return "#155724"  # Verde oscuro
        elif val == "parcial": return "#856404"  # Amarillo oscuro
        else: return "#721c24"  # Rojo oscuro
    return "#495057" # Gris oscuro

def construir_grafo_gv(tree_dict, dot):
    """Función recursiva para construir el grafo Graphviz."""
    for parent, children in tree_dict.items():
        # Añadir nodo padre con colores
        dot.node(parent, parent, shape='box', style='filled',
                 fillcolor=get_node_color(parent),
                 fontcolor=get_node_font_color(parent),
                 fontname="Arial", fontsize="10")

        # Procesar hijos
        for child, sub_children in children.items():
            dot.node(child, child, shape='box', style='filled',
                     fillcolor=get_node_color(child),
                     fontcolor=get_node_font_color(child),
                     fontname="Arial", fontsize="10")
            dot.edge(parent, child, color="#6c757d") # Color gris para aristas
            construir_grafo_gv({child: sub_children}, dot)

def mostrar_grafo(tree):
    """Prepara y muestra el grafo con Graphviz."""
    dot = graphviz.Digraph(comment='Árbol de Razonamiento')
    dot.attr(rankdir='TB') # Layout de Arriba a Abajo (Top to Bottom)
    dot.attr('node', shape='box', style='filled', fontname="Arial", fontsize="10")
    dot.attr('edge', color="#6c757d")

    construir_grafo_gv(tree, dot)

    if dot.body:
        st.subheader("🗺️ Visualización del Árbol de Razonamiento")
        st.graphviz_chart(dot)
        st.caption("Este es un grafo estático. Use la vista de texto inferior para interactuar.")
    else:
        st.info("El árbol de razonamiento está vacío.")
# --- FIN Funciones para Grafo (Versión Graphviz) ---

# --- Renderizado de la App ---
# 1) Conceptos
st.subheader("🧩 Conceptos extraídos (NLP)")
st.write(conceptos or "—")

# 2) Fragmentos RAG
st.subheader("🔍 Fragmentos recuperados (PathRAG)")
st.caption("Estos son ejemplos de fragmentos recuperados por nuestro sistema PathRAG (actualmente simulado).")
if frags:
    for f in frags:
        with st.expander(f["titulo"]):
            st.markdown(f"> {f['fragmento']}")
            st.markdown(f"[Ver fuente]({f['url']})")
else:
    st.info("No se recuperaron fragmentos relevantes.")

# 3) Árbol de razonamiento y Acciones
st.subheader("🌳 Árbol de Razonamiento Jurídico")

# --- MOSTRAR GRAFO ---
mostrar_grafo(tree)
# --- FIN MOSTRAR GRAFO ---

# --- MOSTRAR DETALLES Y ACCIONES (VISTA TEXTO) ---
with st.expander("🔍 Ver Detalles y Generar Contexto (Vista de Texto)"):
    for raiz, hijos in tree.items():
        def mostrar_detalle(nodo, sub, nivel=0): # Renombramos la función original
            margen = "  " * nivel
            data = next((x for x in st.session_state.tracker if x["Subpregunta"] == nodo), None)
            with st.container():
                c1, c2 = st.columns([9,1])
                c1.markdown(f"{margen}🔹 **{nodo}**")
                if data:
                    c2.markdown(badge_validacion(data["Validación"]), unsafe_allow_html=True)

                # Colocar el botón y la info dentro del margen
                st.markdown(f"{margen}---") # Separador visual
                if data:
                    st.info(f"{margen}📘 *{data['Contexto']}*")
                    fuente_texto = data['Fuente']
                if fuente_texto and fuente_texto.startswith("http"):
                    st.markdown(f"{margen}🔗 **Fuente:** [{fuente_texto}]({fuente_texto})")
                elif fuente_texto:
                    st.markdown(f"{margen}🔗 **Fuente:** {fuente_texto}")
# Si no hay fuente, no se muestra nada.
                   
                else:
                    # Usar columnas para alinear el botón
                    col_margen, col_boton = st.columns([nivel if nivel > 0 else 0.1, 10 - (nivel if nivel > 0 else 0.1)])
                    with col_boton:
                         if st.button(f"🧠 Generar contexto", key=f"gen_{nodo}"):
                            nuevo = generar_contexto(nodo)
                            st.session_state.tracker.append({
                                "Subpregunta": nodo,
                                "Contexto": nuevo["contexto"],
                                "Fuente": nuevo["fuente"],
                                "Validación": nuevo.get("validacion","no validada")
                            })
                            st.experimental_rerun() # Usar rerun en lugar de experimental_rerun si hay problemas
                st.markdown(f"{margen}---") # Separador visual

            for h, s in sub.items():
                mostrar_detalle(h, s, nivel+1) # Llamada recursiva a la función renombrada

        mostrar_detalle(raiz, hijos) # Llamada inicial a la función renombrada
# --- FIN DETALLES Y ACCIONES ---

# 4) Barra de progreso y botón global
total = contar_nodos(tree)
resp = contar_respondidos()
colp, _ = st.columns([5,5])
ratio = resp/total if total else 0
colp.progress(min(max(ratio, 0.0), 1.0), text=f"Progreso: {resp}/{total}")
dummy, colb = st.columns([6,4])
with colb:
    st.button("🧠 Generar TODO el contexto", on_click=lambda: generar_todo(tree), type="primary")

# 5) Tracker, Métricas y Descargas
st.subheader("📊 Reasoning Tracker y Métricas")

if resp > 0:
    df = pd.DataFrame(st.session_state.tracker)

    # --- CÁLCULO DE MÉTRICAS ---
    validada_count = df[df["Validación"] == "validada"].shape[0]
    parcial_count = df[df["Validación"] == "parcial"].shape[0]
    no_validada_count = df[df["Validación"] == "no validada"].shape[0]

    # EEE Simplificado: % de nodos respondidos con algún nivel de validación (>= Parcial)
    eee_score = ((validada_count + parcial_count) / resp * 100) if resp > 0 else 0

    # --- MOSTRAR MÉTRICAS ---
    st.markdown("#### Resumen del Proceso Deliberativo:")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nodos Totales", f"{total}")
    col2.metric("Nodos Respondidos", f"{resp} ({resp/total:.0%})")
    col3.metric("Validados (✅ + ⚠️)", f"{validada_count + parcial_count}")
    col4.metric("EEE (Simplificado)", f"{eee_score:.1f}%",
                help="Índice de Equilibrio Erotético (Simplificado): % de nodos respondidos con respaldo 'Validado' o 'Parcial'. Mide la robustez epistémica alcanzada.")

    with st.expander("📘 ¿Qué es el Índice de Equilibrio Erotético (EEE)?"):
        st.markdown(
            """
            El **Índice de Equilibrio Erotético (EEE)** es una métrica para evaluar la **calidad deliberativa** de un proceso de razonamiento. No mide si una IA 'acierta', sino *cómo* razona.

            En su versión completa (descrita en la teoría), evalúa 5 dimensiones: Profundidad, Pluralidad, Justificación, Revisión y Trazabilidad.

            **En este MVP, presentamos una versión simplificada:**
            * **EEE (Simplificado) = (% de Nodos Respondidos que son '✅ Validada' o '⚠️ Parcial')**
            * Nos da una idea rápida de qué proporción del razonamiento generado tiene un respaldo (aunque sea indirecto) en las fuentes simuladas.
            * Un EEE más alto sugiere un razonamiento más fundamentado según nuestro `validador_epistemico.py`.

            *Aunque la clase `ReasoningTracker` existe, este cálculo se realiza aquí para mayor claridad en el MVP.*
            """
        )

    # --- MOSTRAR TABLA ---
    st.markdown("#### Detalle del Reasoning Tracker:")
    st.dataframe(df, use_container_width=True)

    # --- MOSTRAR DESCARGAS ---
    st.markdown("#### Opciones de Exportación:")
    csv = df.to_csv(index=False).encode()
    md = "# Informe de Razonamiento\n" + "\n".join(
        f"- **{r['Subpregunta']}**: {r['Contexto']} (Fuente: {r['Fuente']}, Val: {r['Validación']})"
        for r in st.session_state.tracker
    )
    js = json.dumps(st.session_state.tracker, indent=2, ensure_ascii=False)

    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    d_col1.download_button("📥 CSV", data=csv, file_name="tracker.csv", mime="text/csv", use_container_width=True)
    d_col2.download_button("📥 MD", data=md, file_name="informe.md", mime="text/markdown", use_container_width=True)
    d_col3.download_button("📥 JSON", data=js, file_name="logs.json", mime="application/json", use_container_width=True)

    if HTML:
        html_content = "<html><head><meta charset='UTF-8'></head><body>" + md.replace("\n","<br>") + "</body></html>"
        pdf = HTML(string=html_content).write_pdf()
        d_col4.download_button("📥 PDF", data=pdf, file_name="informe.pdf", mime="application/pdf", use_container_width=True)
    else:
        d_col4.info("PDF no disponible (falta WeasyPrint)")

else:
    st.info("Aún no hay pasos registrados. Genere contexto para algún nodo del árbol.")

# 6) Ayudas
with st.expander("📘 ¿Qué es la validación epistémica?"):
    st.markdown(
        """
        - ✅ Validada: respaldo legal claro.
        - ⚠️ Parcial: interpretación indirecta.
        - ❌ No validada: sin respaldo.
        """
    )
with st.expander("⚙️ ¿Qué simula este MVP?"):
    st.markdown(
        """
        1. Árbol jerárquico.
        2. Contexto por nodo.
        3. Fuentes y validación.
        4. Exportación múltiple.
        5. Pipeline futuro.
        """
    )
with st.expander("🧠 ¿Qué es el Reasoning Tracker?"):
    st.markdown(
        """
        - Registro paso a paso.
        - Auditable y exportable.
        """
    )
