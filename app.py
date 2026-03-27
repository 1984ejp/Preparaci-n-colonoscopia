def mostrar_antes_estudio():
    st.markdown("### 📋 Antes de mi Endoscopía")
    
    # Requisitos fundamentales
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("1. **Medicación:** Si toma anticoagulantes, avise a su médico y consulte con su hematólogo. 🩸")
        st.info("2. **Documentación:** Traiga la orden vigente y autorizada. 📄")
        
    with col2:
        st.info("3. **Acompañante:** Es obligatorio concurrir acompañado. 👥")
        st.success("**IMPORTANTE:** Podrá realizar el estudio solo si cumple con estos requisitos.")

    st.divider()

    # Instrucciones de ayuno y preparación física
    st.warning("#### ⚠️ Instrucciones Críticas")
    
    st.markdown("""
    * **Ayuno:** 8 hs antes suspenda sólidos y lácteos. Puede tomar agua o Gatorade (manzana/limón) hasta 4 hs antes. 💧
    * **Estética:** NO concurrir con uñas pintadas o esmaltadas. 💅🚫
    * **Objetos:** DEBE quitarse anillos, aros y piercings antes del estudio. 💍🚫
    """)

    # Sección de Advertencias y Riesgos
    with st.expander("🔍 TENER EN CUENTA (Información Importante)"):
        st.write("""
        * **Logística:** La preparación produce diarrea intensa; realícela en su domicilio, no en el trabajo. 🏠
        * **Procedimiento:** Durante el estudio se pueden extraer pólipos y tomar biopsias.
        * **Riesgos:** Existe riesgo de perforación (0.15% - 2.14% en terapéutica). En colonoscopía diagnóstica, la complicación es de aprox. 1 cada 2000 exploraciones.
        """)