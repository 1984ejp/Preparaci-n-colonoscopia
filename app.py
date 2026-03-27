import streamlit as st

# Configuración y Estilos (Manteniendo tu estética previa)
st.set_page_config(page_title="Asistente de Endoscopía", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Encabezado del Asistente
    st.title("Hola! Soy Francisco.")
    st.write("Vamos a realizar las modificaciones sobre las indicaciones del estudio.")

    # Pestañas de Navegación originales
    tab1, tab2, tab3 = st.tabs(["🗓️ ANTES DE MI ENDOSCOPIA", "🥤 MI PREPARACION", "📄 GENERAR PDF"])

    with tab1:
        st.subheader("ANTES DE MI ENDOSCOPIA")
        
        # Puntos obligatorios tal cual los pasaste
        st.write("1. Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo. 🩸")
        st.write("2. Debe traer la orden del estudio vigente y debidamente autorizada si corresponde. 📄")
        st.write("3. Debe concurrir acompañado. 👥")
        st.write("4. 8 hs antes del estudio suspende todo alimento sólido y lácteo, continuar con agua y/o Gatorade (sabor manzana o limón) hasta 4hs antes del procedimiento. 💧")
        
        st.info("**PODRA REALIZAR EL ESTUDIO SI CUMPLE CON LOS 4 ITEMS ANTERIORES**")

        st.error("🚫 **NO** debe concurrir con las uñas pintadas o esmaltadas.")
        st.error("💍 **DEBE** quitarse los anillos, aros y/o piercings antes del estudio.")

        st.markdown("---")
        st.subheader("TENER EN CUENTA:")
        st.write("• Esta preparación produce una diarrea intensa por lo que debe realizarla en su domicilio y no en su ámbito laboral. 🏠")
        st.write("• Es importante que sepa que durante el estudio se pueden extraer pólipos y tomar biopsias. Entre los riesgos potenciales que presenta el método, está la perforación microscópica y/o completa del Intestino Grueso. La incidencia de perforación por Colonoscopía es más común después de una terapéutica; oscila del 0.15 y el 2.14% según las series publicadas. Para una Colonoscopía Diagnóstica, la presencia de complicaciones es de aproximadamente 1 por cada 2000 exploraciones. 🩺")

    with tab2:
        st.subheader("MI PREPARACION")
        tipo_prep = st.radio("Seleccione su preparación:", ["FOSFATOS", "PICOSULFATO", "PEG"])
        st.write(f"Instrucciones para {tipo_prep}...")

    with tab3:
        st.subheader("GENERAR PDF")
        if st.button("Descargar Instrucciones"):
            st.success("Preparando el archivo para descargar...")

if __name__ == "__main__":
    main()