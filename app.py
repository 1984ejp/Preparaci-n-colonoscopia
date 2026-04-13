import streamlit as st
import base64
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import tempfile

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Asistente Endoscopía - Francisco", layout="wide")

# 2. TEXTOS FIJOS (RESTAURADOS ÍNTEGROS)
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
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_completa = os.path.join(base_dir, ruta_relativa)
        if not os.path.exists(ruta_completa):
            return f"[Archivo no encontrado: {ruta_relativa}]"
        doc = Document(ruta_completa)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except:
        return "[Error al leer el archivo Word]"

def mostrar_docx(ruta_relativa):
    texto = texto_docx(ruta_relativa)
    st.markdown(f"""
<div style="background-color:white; padding:20px; border-radius:15px; border-left:8px solid #2bb673; margin-bottom:20px; font-size:18px; box-shadow:0px 4px 12px rgba(0,0,0,0.05); color: #1a1a1a !important; line-height: 1.6;">
{texto.replace(chr(10), '<br>')}
</div>
""", unsafe_allow_html=True)

# 4. ESTILOS CSS (CORRECCIÓN DE VISIBILIDAD Y COLORES)
st.markdown("""
<style>
.stApp { background-color: #f4f7f6; }

/* Forzar color de texto para que sea visible sin remarcar */
.stMarkdown p, .stMarkdown span, .stMarkdown li, label, .stWidget label p {
    color: #1a1a1a !important;
}

.card { 
    background-color: white !important; 
    padding: 30px; 
    border-radius: 22px; 
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08); 
    border-top: 10px solid #2bb673;
}

h1, h2, h3 { color: #2bb673 !important; }

.stButton button { 
    background-color: #2bb673 !important; 
    color: white !important; 
    border-radius: 12px;