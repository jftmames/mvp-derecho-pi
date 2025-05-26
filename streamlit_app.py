# ... (código anterior de mostrar_detalle) ...
            with st.container():
                c1, c2 = st.columns([9,1])
                c1.markdown(f"{margen}🔹 **{nodo}**")
                if data:
                    # --- INICIO BLOQUE 'IF DATA' ---
                    c2.markdown(badge_validacion(data["Validación"]), unsafe_allow_html=True)

                # Colocar el botón y la info dentro del margen
                st.markdown(f"{margen}---") # Separador visual
                if data:
                    # --- INICIO SEGUNDO BLOQUE 'IF DATA' ---
                    st.info(f"{margen}📘 *{data['Contexto']}*")

                    # --- CÓDIGO A VERIFICAR/CORREGIR --- 
                    fuente_texto = data.get('Fuente', '') # Usamos .get para más seguridad
                    if fuente_texto and fuente_texto.startswith("http"):
                        st.markdown(f"{margen}🔗 **Fuente:** [{fuente_texto}]({fuente_texto})")
                    elif fuente_texto:
                        st.markdown(f"{margen}🔗 **Fuente:** {fuente_texto}")
                    # --- FIN CÓDIGO A VERIFICAR/CORREGIR ---

                else:
                    # --- BLOQUE 'ELSE' ---
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
                            st.rerun() # Usamos rerun (más estándar ahora)
                st.markdown(f"{margen}---") # Separador visual
                # --- FIN BLOQUES 'IF/ELSE' ---
# ... (resto del código de mostrar_detalle) ...
