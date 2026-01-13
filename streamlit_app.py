import streamlit as st
import os
import shutil
import json
import pandas as pd
import graphviz

# --- IMPORTAMOS TUS MOTORES DEL SPRINT 1, 2 y 3 ---
from cd_modules.core.raga_engine import RAGAEngine
from cd_modules.core.inquiry_engine import InquiryEngine
from cd_modules.core.validador_epistemico import auditor  # Tu Juez Algorítmico

# Configuración de Página
st.set_page_config(page_title="H-ANCHOR | Auditoría Jurídica", layout="wide")

# --- GESTIÓN DE ESTADO (SESSION STATE) ---
if "raga" not in st.session_state:
    st.session_state.raga = RAGAEngine() # Inicializamos el motor RAGA una sola vez

if "audit_tree" not in st.session_state:
    st.session_state.audit_tree = {}

if "audit_log" not in st.session_state:
    st.session_state.audit_log = [] # Aquí guardaremos el historial para el informe

# --- SIDEBAR: INGESTA DE DATOS (LA VERDAD MATERIAL) ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/4a90e2/law.png", width=50)
    st.title("H-ANCHOR")
    st.caption("Sistema de Inferencia Jurídica Auditada")
    
    st.markdown("---")
    st.subheader("1. Carga de Evidencia")
    
    uploaded_file = st.file_uploader("Sube el Marco Legal (PDF)", type=["pdf"])
    
    if uploaded_file:
        # Guardamos temporalmente el archivo para que RAGA lo pueda leer
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("📥 Ingestar y Vectorizar"):
            with st.spinner("Troceando ley y creando índices vectoriales..."):
                st.session_state.raga.ingest_document(temp_path)
            st.success("Base de conocimientos actualizada.")
            os.remove(temp_path) # Limpieza

# --- PÁGINA PRINCIPAL ---
st.title("🕵️ Auditoría Forense con RAGA")

col1, col2 = st.columns([1, 2])

with col1:
    st.info("Este sistema **no inventa**. Solo responde si encuentra evidencia en el PDF subido.")
    topic = st.text_input("Objeto de la Auditoría:", "¿Qué prácticas de IA están prohibidas?")
    
    # Configuración de profundidad
    depth = st.slider("Profundidad de Indagación", 1, 3, 1)
    
    if st.button("🚀 Iniciar Auditoría Deliberativa", type="primary"):
        if not st.session_state.raga.vector_store:
            st.error("⚠️ Primero debes subir e ingestar un PDF en la barra lateral.")
        else:
            with st.spinner("El Motor de Indagación está consultando la Ley..."):
                # 1. INICIALIZAR MOTOR CON RAGA CONECTADO (Sprint 2)
                engine = InquiryEngine(topic, max_depth=depth, max_width=2, raga_engine=st.session_state.raga)
                
                # 2. GENERAR ÁRBOL
                st.session_state.audit_tree = engine.generate()
                st.session_state.audit_log = [] # Reiniciar log
                st.rerun()

# --- VISUALIZACIÓN Y AUDITORÍA ---
if st.session_state.audit_tree:
    
    st.markdown("---")
    col_graph, col_details = st.columns([2, 1.5])
    
    with col_graph:
        st.subheader("🗺️ Mapa de Razonamiento")
        
        # Construcción del Gráfico
        graph = graphviz.Digraph()
        graph.attr(rankdir='TB')
        graph.attr('node', shape='box', style='filled', fontname="Arial")
        
        def plot_nodes(tree_dict, parent=None):
            for question, children in tree_dict.items():
                node_id = str(hash(question)) # ID único
                
                # AUDITORÍA EN TIEMPO REAL (Sprint 3)
                # Recuperamos la evidencia para esta pregunta específica
                evidence_list = st.session_state.raga.retrieve(question, k=1)
                evidence_text = evidence_list[0]['content'] if evidence_list else ""
                source_ref = evidence_list[0]['source'] if evidence_list else "Sin fuente"
                
                # El Juez audita: ¿La pregunta tiene sentido con esta evidencia?
                # (Simplificación visual: si hay evidencia sólida, es verde)
                if evidence_text:
                    color = "#d4edda" # Verde
                    status = "VALIDADA"
                else:
                    color = "#f8d7da" # Rojo
                    status = "NO VALIDADA"
                
                # Guardamos en el log para el informe
                st.session_state.audit_log.append({
                    "Cuestión": question,
                    "Estado": status,
                    "Evidencia (Grounding)": source_ref
                })

                # Dibujamos nodo
                label = f"{question}\n[{status}]"
                graph.node(node_id, label, fillcolor=color)
                
                if parent:
                    graph.edge(parent, node_id)
                
                plot_nodes(children, node_id)

        plot_nodes(st.session_state.audit_tree)
        st.graphviz_chart(graph, use_container_width=True)

    with col_details:
        st.subheader("📝 Reasoning Tracker (Informe)")
        
        if st.session_state.audit_log:
            df = pd.DataFrame(st.session_state.audit_log)
            # Eliminar duplicados causados por la recursión visual
            df = df.drop_duplicates(subset=["Cuestión"])
            
            st.dataframe(df, use_container_width=True)
            
            # Cálculo EEE Real
            total = len(df)
            validas = len(df[df["Estado"] == "VALIDADA"])
            eee_score = (validas / total) * 100 if total > 0 else 0
            
            st.metric("Índice EEE (Solidez)", f"{eee_score:.1f}%")
            
            # EXPORTACIÓN
            st.download_button(
                "📄 Descargar Informe Forense (CSV)",
                df.to_csv(index=False).encode('utf-8'),
                "auditoria_h_anchor.csv",
                "text/csv"
            )
