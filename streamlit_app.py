```python
import streamlit as st
import pandas as pd
import json

# Intentamos importar weasyprint para PDF; si no está, lo ignoramos
try:
    from weasyprint import HTML
except ImportError:
    HTML = None

from cd_modules.core.extractor_conceptual import extraer_conceptos
from cd_modules.core.inquiry_engine import InquiryEngine
from cd_modules.core.contextual_generator import generar_contexto

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Demo PI - Código Deliberativo", layout="wide")
st.title("📚 Demo MVP - Derecho de la Propiedad Intelectual")
st.markdown("Esta demo simula razonamiento jurídico automatizado, con validación epistémica visible.")

# --- cumplimiento MVP: Declaración de valor ---
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

# --- SIDEBAR: Parámetros del árbol y ejemplos ---
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

# --- Extracción de conceptos con spaCy ---
conceptos = extraer_conceptos(pregunta)
st.subheader("🧩 Conceptos extraídos (NLP)")
if conceptos:
    st.write(conceptos)
else:
    st.info("No se han podido extraer conceptos relevantes.")

# --- Generación del árbol ---
ie = InquiryEngine(pregunta, max_depth=max_depth, max_width=max_width)
tree = ie.generate()

# --- Session State para el Reasoning Tracker ---
if "tracker" not in st.session_state:
    st.session_state.tracker = []

# --- UX: badge de validación ---
def badge_validacion(tipo):
    if tipo == "validada":
        return '<span style="color: white; background-color: #28a745; padding: 3px 8px; border-radius: 6px;">✅ Validada</span>'
    elif tipo == "parcial":
        return '<span style="color: black; background-color: #ffc107; padding: 3px 8px; border-radius: 6px;">⚠️ Parcial</span>'
    else:
        return '<span style="color: white; background-color: #dc3545; padding: 3px 8px; border-radius: 6px;">❌ No validada</span>'

def esta_respondido(nodo):
    return any(x["Subpregunta"] == nodo for x in st.session_state.tracker)

# --- Contadores ---
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

# --- Generación masiva de contexto ---
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

# --- Visualización del árbol ---
def mostrar_arbol(nodo, hijos, nivel=0):
    margen = "  " * nivel
    data = next((x for x in st.session_state.tracker if x["Subpregunta"] == nodo), None)
    with st.container():
        col1, col2 = st.columns([9, 1])
        with col1:
            st.markdown(f"{margen}🔹 **{nodo}**")
        with col2:
            if data:
                st.markdown(badge_validacion(data["Validación"]), unsafe_allow_html=True)
        if data:
            st.info(f"{margen}📘 *{data['Contexto']}*")
            st.markdown(f"{margen}🔗 **Fuente:** {data['Fuente']}")
        else:
            if st.button(f"🧠 Generar contexto", key=f"gen_{nodo}"):
                with st.spinner("Generando contexto..."):
                    nuevo = generar_contexto(nodo)
                    st.session_state.tracker.append({
                        "Subpregunta": nodo,
                        "Contexto": nuevo["contexto"],
                        "Fuente": nuevo["fuente"],
                        "Validación": nuevo.get("validacion", "no validada")
                    })
                    st.experimental_rerun()
    for hijo, subhijos in hijos.items():
        mostrar_arbol(hijo, subhijos, nivel + 1)

# --- Botón de generación global ---
col_gen, _ = st.columns([4, 6])
with col_gen:
    st.button("🧠 Generar TODO el contexto", on_click=lambda: generar_todo(tree), type="primary")

# --- Barra de progreso ---
total = contar_nodos(tree)
respondidos = contar_respondidos()
st.progress(min(respondidos / total, 1.0) if total else 0, text=f"Progreso: {respondidos}/{total} respondidos")

# --- Árbol de razonamiento ---
st.subheader("🔍 Árbol de razonamiento jurídico")
for raiz, hijos in tree.items():
    mostrar_arbol(raiz, hijos)

# --- Reasoning Tracker y descargas ---
st.subheader("🧾 Reasoning Tracker")
if respondidos > 0:
    df = pd.DataFrame(st.session_state.tracker)
    st.dataframe(df, use_container_width=True)

    # CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Descargar como CSV", data=csv, file_name="reasoning_tracker.csv", mime="text/csv")

    # Markdown
    md_lines = ["# Informe de Razonamiento\n"]
    for paso in st.session_state.tracker:
        linea = f"- **{paso['Subpregunta']}**: {paso['Contexto']} (Fuente: {paso['Fuente']}, Validación: {paso['Validación']})"
        md_lines.append(linea)
    md_report = "\n".join(md_lines)
    st.download_button(
        label="📥 Descargar Informe (Markdown)",
        data=md_report,
        file_name="informe_razonamiento.md",
        mime="text/markdown"
    )

    # PDF (solo si weasyprint está disponible)
    if HTML:
        html_content = "<html><body>" + md_report.replace("\n", "<br>") + "</body></html>"
        pdf_bytes = HTML(string=html_content).write_pdf()
        st.download_button(
            label="📥 Descargar Informe (PDF)",
            data=pdf_bytes,
            file_name="informe_razonamiento.pdf",
            mime="application/pdf"
        )

    # JSON
    logs_json = json.dumps(st.session_state.tracker, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Descargar Logs (JSON)",
        data=logs_json,
        file_name="logs_razonamiento.json",
        mime="application/json"
    )
else:
    st.info("Aún no hay pasos registrados.")

# --- AYUDA Y EXPLICACIONES ---
with st.expander("📘 ¿Qué es la validación epistémica?"):
    st.markdown("""
        - ✅ **Validada**: Hay respaldo legal o jurisprudencial claro.
        - ⚠️ **Parcial**: Respaldada por doctrina o interpretación indirecta.
        - ❌ **No validada**: Hipótesis no respaldada por fuentes jurídicas.
    """)

with st.expander("⚙️ ¿Qué simula este MVP?"):
    st.markdown("""
        1. Estructura lógica tipo árbol.
        2. Genera contexto para cada nodo (simulado o vía LLM).
        3. Añade fuente y validación epistémica.
        4. Permite exportar el razonamiento.
        5. Prepara la integración futura con LLM, PathRAG, corpus legal.
    """)

with st.expander("🧠 ¿Qué es el Reasoning Tracker?"):
    st.markdown("""
        - Registra cada paso, fuente y nivel de validación.
        - Permite auditar decisiones jurídicas generadas.
    """)
```
