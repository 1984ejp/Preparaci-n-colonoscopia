import streamlit as st
import base64
from docx import Document
import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Asistente Endoscopía - CEMIC", layout="wide")

# 2. COLORES Y TEXTOS INSTITUCIONALES
VERDE_CEMIC = "#2bb673"
VERDE_OSCURO = "#1e7d4f"
GRIS_SUAVE = "#f4f7f6"

TEXTO_ANTES = """
⚠️ Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo.
📄 Debe traer la orden del estudio vigente y debidamente autorizada si corresponde.
👥 Debe concurrir acompañado.
✅ PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS 4 ÍTEMS ANTERIORES.
⏰ 8 hs antes del estudio suspende todo alimento sólido y lácteo. Puede continuar con agua y/o Gatorade (sabor manzana o limón) hasta 4 hs antes del procedimiento.
🚫 NO debe concurrir con las uñas pintadas o esmaltadas.
🚫 DEBE quitarse los anillos, aros y/o piercings antes del estudio.
💧 Esta preparación produce una diarrea intensa, por lo que debe realizarla en su domicilio y no en su ámbito laboral.
"""

# 3. ESTILOS CSS (EMULACIÓN CEMIC)
st.markdown(f"""
<style>
    .stApp {{ background-color: {GRIS_SUAVE}; }}
    
    /* Eliminar espacios superiores de Streamlit */
    .block-container {{ padding-top: 0rem !important; }}
    
    /* Header Institucional */
    .header-cem {{
        background-color: {VERDE_CEMIC};
        padding: 15px 50px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }}

    /* Tarjeta Principal */
    .card-institucional {{
        background-color: white !important;
        padding: 35px;
        border-radius: 15px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.05);
        border-top: 10px solid {VERDE_CEMIC};
    }}

    h1 {{ color: {VERDE_CEMIC} !important; font-weight: 700; margin-top: 0; }}
    h3 {{ color: #444 !important; font-weight: 400; margin-bottom: 25px; }}

    /* Burbujas de texto */
    .burbuja {{
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        line-height: 1.6;
        font-size: 16px;
        border: 1px solid #eee;
    }}
    .burbuja-verde {{ background-color: {VERDE_CEMIC} !important; color: white !important; border: none; }}
    .burbuja-alerta {{ background-color: #fef9e7; border-left: 6px solid #f1c40f; color: #1a5c96; }}
    .burbuja-peligro {{ background-color: #fdedec; border-left: 6px solid #e74c3c; color: #1a5c96; }}

    /* Botones y Selectores */
    .stButton button {{
        background-color: {VERDE_CEMIC} !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 12px;
        font-weight: bold;
    }}
    div[role="radiogroup"] label {{ color: {VERDE_OSCURO} !important; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)

# 4. FUNCIONES DE APOYO
def get_img64(path):
    if not os.path.exists(path): return None
    with open(path, "rb") as f: return base64.b64encode(f.read()).decode()

def reiniciar():
    st.session_state.clear()
    st.rerun()

def mostrar_docx(ruta_relativa):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(base_dir, ruta_relativa)
    if os.path.exists(ruta_completa):
        doc = Document(ruta_completa)
        texto = "<br>".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
        st.markdown(f'<div class="burbuja" style="background:white;">{texto}</div>', unsafe_allow_html=True)

# 5. HEADER
st.markdown(f"""
<div class="header-cem">
    <div style="font-size: 28px; font-weight: bold; letter-spacing: 1px;">CEMIC</div>
    <div style="font-size: 12px; text-align: right; opacity: 0.9;">INSTITUCIONAL | DOCENCIA<br>INVESTIGACIÓN | ATENCIÓN MÉDICA</div>
</div>
""", unsafe_allow_html=True)

# 6. CUERPO PRINCIPAL
col1, col2 = st.columns([1.2, 0.8])

with col1:
    # Encapsulamos el saludo y las burbujas iniciales en la card blanca
    st.markdown(f"""
    <div class="card-institucional">
        <h1>Hola, soy Francisco 👋</h1>
        <h3>Tu asistente para estudios de Gastroenterología</h3>
        
        <div class="burbuja burbuja-verde">
            La Endoscopía representa hoy día, la mejor técnica para el diagnóstico y seguimiento de las enfermedades del Intestino Grueso, para la prevención del Cáncer de Colon y para el tratamiento de un variado número de lesiones.
        </div>
        <div class="burbuja" style="background-color: #f9f9f9;">
            Durante el estudio se pueden extraer pólipos y tomar biopsias.
        </div>
        <div class="burbuja burbuja-alerta">
            Entre los riesgos potenciales, está la perforación microscópica y/o completa del Intestino Grueso. La incidencia en estudios diagnósticos es de aprox. 1 por cada 2000 exploraciones.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    opcion = st.radio("POR FAVOR, SELECCIONE SU ETAPA ACTUAL:", 
                      ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    
    if st.button("🔄 REINICIAR CONSULTA"): reiniciar()

with col2:
    img = get_img64("francisco.png")
    if img:
        st.markdown(f"""
        <div style="display:flex; justify-content:center; padding-top:20px;">
            <img src="data:image/png;base64,{img}" style="width:100%; max-width:380px; border-radius:50%; border: 12px solid white; box-shadow: 0px 15px 35px rgba(0,0,0,0.1);">
        </div>
        """, unsafe_allow_html=True)

# 7. LÓGICA DE SECCIONES
st.markdown("---")

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.markdown(f"## <span style='color:{VERDE_CEMIC}'>📋 Instrucciones Previas</span>", unsafe_allow_html=True)
    st.markdown(f"""<div class="burbuja" style="background:white; border-left: 8px solid {VERDE_CEMIC};">{TEXTO_ANTES.replace(chr(10), "<br>")}</div>""", unsafe_allow_html=True)
    mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

elif opcion == "MI PREPARACIÓN":
    st.markdown(f"## <span style='color:{VERDE_CEMIC}'>🧪 Configuración de Preparación</span>", unsafe_allow_html=True)
    familia = st.selectbox("Tipo de preparación indicada:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
    franja = st.radio("Horario de su turno:", ["7 A 12", "12 A 16", "16 A 19"])
    
    if st.button("VER PLAN DE PREPARACIÓN"):
        archivo = f"textos/{familia} DE {franja}.docx"
        mostrar_docx(archivo)

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.markdown(f"## <span style='color:{VERDE_CEMIC}'>🏁 Recomendaciones Post-Estudio</span>", unsafe_allow_html=True)
    st.markdown("""
    <div class="burbuja" style="background:white;"><b>1. OBSERVACIONES:</b> Permanecer en recuperación hasta el alta médica. No conducir por 12 hs.</div>
    <div class="burbuja" style="background:white;"><b>2. DIETA:</b> Iniciar con líquidos y luego dieta liviana según tolerancia.</div>
    <div class="burbuja burbuja-peligro"><b>3. ALERTA:</b> Si presenta dolor abdominal fuerte o fiebre, contacte a Urgencias CEMIC inmediatamente.</div>
    <div class="burbuja burbuja-verde"><b>4. CONTACTO:</b> Gastroenterología (08 a 20hs): 11 5596 2440.</div>
    """, unsafe_allow_html=True)