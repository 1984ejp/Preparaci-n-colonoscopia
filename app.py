import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Asistente de Endoscopía - Francisco", page_icon="🏥", layout="wide")

# Estilos CSS para personalización y optimización (Basado en tu última versión de 5kb)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    .stAlert { border-radius: 12px; }
    .instruccion-card { background: white; padding: 20px; border-radius: 15px; border-left: 5px solid #007bff; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE CONTENIDO ---

def mostrar_antes_estudio():
    st.markdown("## 📋 Antes de mi Endoscopía")
    
    st.info("⚠️ **IMPORTANTE:** Solo podrá realizar el estudio si cumple con los siguientes 4 ítems:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="instruccion-card">
        <b>1. Medicación y Coagulación</b><br>
        Si toma medicación que altere la coagulación de la sangre (anticoagulantes/antiagregantes) debe recordárselo a su médico con anticipación y consultarlo con su hematólogo. 🩸
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="instruccion-card">
        <b>2. Documentación</b><br>
        Debe traer la orden del estudio vigente y debidamente autorizada si corresponde. 📄
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="instruccion-card">
        <b>3. Acompañamiento</b><br>
        Debe concurrir acompañado obligatoriamente. No podrá retirarse solo. 👥
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="instruccion-card">
        <b>4. Ayuno y Líquidos</b><br>
        8 hs antes del estudio suspenda todo alimento sólido y lácteo. Puede continuar con agua y/o Gatorade (sabor manzana o limón) hasta 4 hs antes del procedimiento. 💧
        </div>
        """, unsafe_allow_html=True)

    st.warning("⚡ **REGLAS DE SEGURIDAD FÍSICA:**")
    c1, c2 = st.columns(2)
    c1.error("💅 **UÑAS:** NO debe concurrir con las uñas pintadas o esmaltadas.")
    c2.error("💍 **ACCESORIOS:** DEBE quitarse anillos, aros y/o piercings antes del estudio.")

    with st.expander("🔍 TENER EN CUENTA (Información Médica y Logística)"):
        st.write("""
        * **Logística:** Esta preparación produce una diarrea intensa por lo que debe realizarla en su domicilio y no en su ámbito laboral. 🏠
        * **Procedimiento:** Durante el estudio se pueden extraer pólipos y tomar biopsias.
        * **Riesgos:** Entre los riesgos potenciales está la perforación microscópica y/o completa del Intestino Grueso. 
          - En Colonoscopía Terapéutica: oscila entre 0.15% y 2.14%.
          - En Colonoscopía Diagnóstica: la incidencia es de aproximadamente 1 por cada 2000 exploraciones.
        """)

def mostrar_preparacion(tipo):
    st.markdown(f"## 💊 Preparación con {tipo}")
    # Aquí iría la lógica de preparación según el medicamento elegido (Fosfatos, Picosulfato, etc.)
    st.write(f"Instrucciones específicas para la toma de {tipo}...")

# --- INTERFAZ PRINCIPAL ---

def main():
    # Header con el Asistente
    col_img, col_txt = st.columns([1, 4])
    with col_txt:
        st.title("Asistente Virtual de Endoscopía")
        st.write("¡Hola! Soy Francisco. Te ayudaré con las instrucciones para tu estudio.")

    # Pestañas de Navegación
    tab1, tab2, tab3 = st.tabs(["🗓️ Antes del Estudio", "🥤 Mi Preparación", "📄 Descargar PDF"])

    with tab1:
        mostrar_antes_estudio()

    with tab2:
        tipo_prep = st.selectbox("Seleccione el medicamento recetado:", 
                                ["FOSFATOS", "PICOSULFATO", "PEG (Polietilenglicol)", "OTROS"])
        mostrar_preparacion(tipo_prep)

    with tab3:
        st.subheader("Generar Instrucciones en PDF")
        st.write("Presione el botón para descargar un resumen de estas indicaciones.")
        if st.button("Generar Documento"):
            st.success("Generando PDF... (Función lista para conectar con FPDF)")

if __name__ == "__main__":
    main()