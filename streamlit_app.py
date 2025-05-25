import streamlit as st
import pandas as pd
import json
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
    if tipo == "validada":
        return '<span style="color: white; background-color: #28a745; padding: 3px 8px; border-radius: 6px;">✅ Validada</span>'
    elif tipo == "parcial":
        return '<span style="color: black; background-color: #ffc107; padding: 3px 8px; border-radius: 6px;">⚠️ Parcial</span>'
    else:
        return '<span style="color: white; background-color: #dc3545; padding: 3px 8px; border-radius: 6px;">❌ No validada</span>'

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

# --- Renderizado de la App ---
# 1) Conceptos
st.subheader("🧩 Conceptos extraídos (NLP)")
st.write(conceptos or "—")

# 2) Fragmentos RAG
st.subheader("🔍 Fragmentos recuperados (PathRAG)")
if frags:
    for f in frags:
        with st.expander(f["titulo"]):
            st.markdown(f"> {f['fragmento']}")
            st.markdown(f"[Ver fuente]({f['url']})")
else:
    st.info("No se recuperaron fragmentos relevantes.")

# 3) Árbol de razonamiento
st.subheader("🔍 Árbol de razonamiento jurídico")
for raiz, hijos in tree.items():
    def mostrar(nodo, sub, nivel=0):
        margen = "  " * nivel
        data = next((x for x in st.session_state.tracker if x["Subpregunta"] == nodo), None)
        with st.container():
            c1, c2 = st.columns([9,1])
            c1.markdown(f"{margen}🔹 **{nodo}**")
            if data:
                c2.markdown(badge_validacion(data["Validación"]), unsafe_allow_html=True)
            if data:
                st.info(f"{margen}📘 *{data['Contexto']}*")
                st.markdown(f"{margen}🔗 **Fuente:** {data['Fuente']}")
            else:
                if st.button(f"🧠 Generar contexto", key=f"gen_{nodo}"):
                    nuevo = generar_contexto(nodo)
                    st.session_state.tracker.append({
                        "Subpregunta": nodo,
                        "Contexto": nuevo["contexto"],
                        "Fuente": nuevo["fuente"],
                        "Validación": nuevo.get("validacion","no validada")
                    })
                    st.experimental_rerun()
        for h, s in sub.items():
            mostrar(h, s, nivel+1)
    mostrar(raiz, hijos)

# 4) Barra de progreso y botón global
total = contar_nodos(tree)
resp = contar_respondidos()
colp, _ = st.columns([5,5])
colp.progress(resp/total if total else 0, text=f"Progreso: {resp}/{total}")
dummy, colb = st.columns([6,4])
with colb:
    st.button("🧠 Generar TODO el contexto", on_click=lambda: generar_todo(tree), type="primary")

# 5) Tracker y descargas
st.subheader("🧾 Reasoning Tracker")
if resp > 0:
    df = pd.DataFrame(st.session_state.tracker)
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode()
    st.download_button("📥 CSV", data=csv, file_name="tracker.csv", mime="text/csv")
    md = "# Informe de Razonamiento\n" + "\n".join(
        f"- **{r['Subpregunta']}**: {r['Contexto']} (Fuente: {r['Fuente']}, Val: {r['Validación']})"
        for r in st.session_state.tracker
    )
    st.download_button("📥 MD", data=md, file_name="informe.md", mime="text/markdown")
    if HTML:
        html = "<html><body>" + md.replace("\n","<br>") + "</body></html>"
        pdf = HTML(string=html).write_pdf()
        st.download_button("📥 PDF", data=pdf, file_name="informe.pdf", mime="application/pdf")
    js = json.dumps(st.session_state.tracker, indent=2, ensure_ascii=False)
    st.download_button("📥 JSON", data=js, file_name="logs.json", mime="application/json")
else:
    st.info("Aún no hay pasos registrados.")

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
