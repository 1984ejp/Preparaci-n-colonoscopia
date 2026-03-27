import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Asistente de Endoscopía", page_icon="🏥", layout="wide")

# Estilos optimizados
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stAlert { border-radius: 10px; }
    .card-requisito { 
        background: #ffffff; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 5px solid #007bff; 
        margin-bottom: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .titulo-seccion { color: #1e3a8a; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

def mostrar_antes_estudio():
    st.markdown("<h2 class='titulo-seccion'>📋 ANTES DE MI ENDOSCOPÍA</h2>", unsafe_allow_html=True)
    
    st.success("✅ **PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS SIGUIENTES 4 ÍTEMS:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card-requisito">
        <b>1. Medicación</b><br>
        Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo. 🩸
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card-requisito">
        <b>2. Documentación</b><br>
        Debe traer la orden del estudio vigente y debidamente autorizada si corresponde. 📄
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card-requisito">
        <b>3. Acompañante</b><br>
        Debe concurrir acompañado. 👥
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card-requisito">
        <b>4. Ayuno Crítico</b><br>
        8 hs antes del estudio suspende todo alimento sólido y lácteo. Puede continuar con agua y/o Gatorade (manzana o limón) hasta 4 hs antes del procedimiento. 💧
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Reglas de ingreso a sala
    st.markdown("### 🚫 REGLAS DE SEGURIDAD")
    c1, c2 = st.columns(2)
    with c1:
        st.error("**UÑAS:** NO debe concurrir con las uñas pintadas o esmaltadas. 💅")
    with c2:
        st.error("**ACCESORIOS:** DEBE quitarse los anillos, aros y/o piercings antes del estudio. 💍")

    st.divider()

    # Información Médica Obligatoria
    st.markdown("### ⚠️ TENER EN CUENTA")
    
    with st.container():
        st.info("""
        * **Logística:** Esta preparación produce una **diarrea intensa** por lo que debe realizarla en su domicilio y no en su ámbito laboral. 🏠
        * **Procedimiento:** Durante el estudio se pueden extraer pólipos y tomar biopsias.
        * **Riesgos:** Existe riesgo de perforación (0.15% - 2.14% en terapéutica). En colonoscopía diagnóstica, la complicación es de aprox. 1 cada 2000 exploraciones. 🩺
        """)

def main():
    # Header simple y profesional
    st.title("Asistente Virtual")
    st.write("Hola! Soy Francisco. Estas son las indicaciones necesarias para tu estudio.")
    
    # Navegación
    tab1, tab2 = st.tabs(["🗓️ Indicaciones Previas", "📄 Generar PDF"])
    
    with tab1:
        mostrar_antes_estudio()
        
    with tab2:
        st.subheader("Descargar Resumen")
        if st.button("Descargar Instrucciones en PDF"):
            st.info("Generando documento con los puntos solicitados...")

if __name__ == "__main__":
    main()