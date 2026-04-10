import streamlit as st
import base64
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import tempfile

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Asistente Endoscopía - Francisco", layout="wide")

# 2. TEXTOS FIJOS
TEXTO_ANTES = """
⚠️ Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo.
📄 Debe traer la orden del estudio vigente y debidamente autorizada si corresponde.
👥 Debe concurrir acompañado.
✅ PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS 4 ÍTEMS ANTERIORES.
⏰ 8 hs antes del estudio suspende todo alimento sólido y lácteo. Puede continuar con agua y/o Gatorade (sabor manzana o limón) hasta 4 hs antes del procedimiento.
🚫 NO debe concurrir con las uñas pintadas o esmaltadas.
🚫 DEBE quitarse los anillos, aros y/o piercings antes del estudio.
💧 Esta preparación produce una diarrea intensa, por lo que debe realizarla en su domicilio y no en su ámbito laboral.
⚠️ Es importante que sepa que durante el estudio se pueden extraer pólipos y tomar biopsias. Entre los riesgos potenciales del método está la perforación microscópica o completa del intestino grueso. La incidencia de perforación por colonoscopía oscila entre 0.15% y 2.14%. Para una colonoscopía diagnóstica la presencia de complicaciones es aproximadamente 1 cada 2000 exploraciones.
"""

# 3. FUNCIONES DE APOYO
def reiniciar():
    st.session_state.clear()
    st.rerun()

def texto_docx(ruta_relativa):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(base_dir, ruta_relativa)
    if not os.path.exists(ruta_completa):
        return f"[Archivo no encontrado: {ruta_relativa}]"
    doc = Document(ruta_completa)
    return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])

def mostrar_docx(ruta_relativa):
    texto = texto_docx(ruta_relativa)
    st.markdown(f"""
    <div style="background-color:white; padding:20px; border-radius:15px; border-left:8px solid #2bb673; margin-bottom:20px; font-size:20px; box-shadow:0px 4px 12px rgba(0,0,0,0.05); color: #333333 !important;">
    {texto.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

def generar_pdf_profesional(titulo_plan, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('T', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor="#1e7d4f")
    estilo_sub = ParagraphStyle('S', parent=styles['Heading2'], fontSize=14, spaceBefore=15, textColor="#2bb673")
    estilo_txt = ParagraphStyle('X', parent=styles['Normal'], fontSize=11, leading=14)

    elementos = [Paragraph(f"PLAN DE PREPARACIÓN: {titulo_plan}", estilo_titulo)]
    for nombre, contenido in secciones.items():
        elementos.append(Paragraph(nombre.upper(), estilo_sub))
        for linea in contenido.split('\n'):
            if linea.strip(): elementos.append(Paragraph(linea, estilo_txt))
        elementos.append(Spacer(1, 12))
    doc.build(elementos)
    return tmp.name

# 4. ESTILOS CSS (GAMA VERDE ESMERALDA)
st.markdown("""
<style>
.stApp { background-color: #f4f7f6; }

/* Ajuste de la tarjeta blanca */
.card { 
    background-color: white !important; 
    padding: 30px; 
    border-radius: 22px; 
    box-shadow: 0px 8px 24px rgba(0,0,0,0.06); 
    margin-top: 0px; 
    border-top: 10px solid #2bb673;
}

/* Colores de texto */
h1, h2, h3 { color: #2bb673 !important; }
p, span, label { color: #1e7d4f !important; }

.stButton button { 
    background-color: #2bb673 !important; 
    color: white !important; 
    border-radius: 12px; 
    font-size: 20px; 
    width: 100%; 
    border: none;
}

/* Burbujas de información */
.burbuja {
    padding: 18px; 
    border-radius: 15px; 
    margin-bottom: 12px;
    font-size: 16px; 
    line-height: 1.5; 
    display: block;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}
.burbuja-verde-solida { background-color: #2bb673 !important; color: white !important; }
.burbuja-clara { background-color: #eafaf1 !important; border-left: 6px solid #2bb673; color: #1e7d4f !important; }
.burbuja-amarilla { background-color: #fef9e7 !important; border-left: 6px solid #f1c40f; color: #1a5c96 !important; }
.burbuja-roja { background-color: #fdedec !important; border-left: 6px solid #e74c3c; color: #1a5c96 !important; }
.burbuja-gris { background-color: #f4f6f7 !important; border-left: 6px solid #95a5a6; color: #1a5c96 !important; }
</style>
""", unsafe_allow_html=True)

# 5. IMAGEN FRANCISCO
def get_img64(path):
    if not os.path.exists(path): return None
    with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
img = get_img64("francisco.png")

# 6. LAYOUT PRINCIPAL
col1, col2 = st.columns([1.1, 1])

with col1:
    # TODO EL SALUDO Y BURBUJAS DENTRO DE UN SOLO BLOQUE HTML
    st.markdown(f"""
    <div class="card">
        <h1 style="margin-top:0;">Hola, soy Francisco 👋</h1>