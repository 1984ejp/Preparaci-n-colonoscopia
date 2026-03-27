import streamlit as st
import base64
from docx import Document
import os
import re
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT

st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --------------------------------------------------
# FUNCIONES DE UTILIDAD
# --------------------------------------------------

def reiniciar():
    st.session_state.clear()
    st.rerun()

def obtener_ruta_completa(ruta_relativa):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, ruta_relativa)

def texto_docx(ruta):
    ruta_abs = obtener_ruta_completa(ruta)
    if not os.path.exists(ruta_abs):
        return ""
    try:
        doc = Document(ruta_abs)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except:
        return ""

# --------------------------------------------------
# ESTILO CSS
# --------------------------------------------------
st.markdown("""
<style>
.stApp{ background:linear-gradient(180deg,#e9f0f7,#dfe8f3); }
html,body,[class*="css"]{ font-size:22px !important; }
h1{ font-size:52px !important; }
.stButton button{
    font-size:22px !important; padding:14px 26px; border-radius:14px;
    background:#4da6ff; color:white; border:none; width:100%;
}
.card{ background:white; padding:28px; border-radius:22px; box-shadow:0px 8px 24px rgba(0,0,0,0.08); }
@media (max-width: 768px){
    html,body,[class*="css"]{ font-size:18px !important; }
    h1{ font-size:32px !important; }
    .card{ padding:18px; }
    .stButton button{ font-size:18px !important; padding:12px; }
    .hide-mobile{ display:none; }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# GENERAR PDF PROFESIONAL
# --------------------------------------------------
def generar_pdf_profesional(titulo_plan, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor="#1a5c96")
    estilo_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=10, textColor="#4da6ff")
    estilo_texto = ParagraphStyle('Texto', parent=styles['Normal'], fontSize=11, leading=14, alignment=TA_LEFT, spaceAfter=8)

    elementos = []
    elementos.append(Paragraph(f"PLAN DE PREPARACIÓN: {titulo_plan}", estilo_titulo))
    
    for nombre_seccion, contenido in secciones.items():
        if contenido.strip():
            elementos.append(Paragraph(nombre_seccion.upper(), estilo_subtitulo))
            # Procesar saltos de línea para el PDF
            for linea in contenido.split('\n'):
                if linea.strip():
                    elementos.append(Paragraph(linea, estilo_texto))
            elementos.append(Spacer(1, 12))

    doc.build(elementos)
    return tmp.name

# --------------------------------------------------
# COMPONENTES DE INTERFAZ
# --------------------------------------------------
def detectar_icono(texto):
    t = texto.lower()
    if any(x in t for x in ["no debe", "quitar", "suspenda", "prohibido"]): return "🚫","#ffeaea","#ff4d4d"
    if any(x in t for x in ["riesgo", "perforación", "biopsia", "pólipo"]): return "⚠️","#fff7cc","#f0ad4e"
    if "hs" in t: return "⏰","white","#4da6ff"
    return "✅","white","#4da6ff"

def mostrar_docx_con_estilo(ruta):
    ruta_abs = obtener_ruta_completa(ruta)
    if not os.path.exists(ruta_abs):
        st.error(f"Archivo no encontrado: {ruta}")
        return
    
    doc = Document(ruta_abs)
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt:
            ico, fondo, color = detectar_icono(txt)
            st.markdown(f"""
            <div style="background:{fondo}; padding:20px; border-radius:15px; margin-bottom:15px; border-left:8px solid {color}; box-shadow:0px 4px 12px rgba(0,0,0,0.05);">
                <b>{ico}</b> {txt}
            </div>""", unsafe_allow_html=True)

# --------------------------------------------------
# LOGICA DE PANTALLA
# --------------------------------------------------
img_b64 = None
path_img = obtener_ruta_completa("francisco.png")
if os.path.exists(path_img):
    with open(path_img, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Hola, soy Francisco 👋")
    opcion = st.radio("Elegí una opción:", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    if st.button("🔄 REINICIAR"): reiniciar()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if img_b64:
        st.markdown(f'<div class="hide-mobile" style="text-align:center;"><img src="data:image/png;base64,{img_b64}" style="width:100%; max-width:400px; border-radius:24px;"></div>', unsafe_allow_html=True)

st.divider()

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.header("Alertas Generales")
    mostrar_docx_con_estilo("textos/Alertas Generales a todas las preparaciones.docx")

elif opcion == "MI PREPARACIÓN":
    familia = st.selectbox("Tipo de preparación indicada", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
    franja = st.radio("Franja horaria del estudio", ["7 A 12", "12 A 16", "16 A 19"])
    
# Definir archivo de preparación SIEMPRE (fuera del botón)
if familia == "BAREX KIT":
    archivo_prep = f"textos/BAREX KIT DE {'7 A 12' if franja=='7 A 12' else '12 A 19'}.docx"
elif familia == "POLIETILENGLICOL":
    archivo_prep = f"textos/POLIETILENGLICOL 4 litros de {franja}HS.docx"
else:
    archivo_prep = f"textos/{familia} DE {franja}.docx"

# Mostrar SIEMPRE el contenido
st.header("1. Alertas Antes del Estudio")
mostrar_docx_con_estilo("textos/Alertas Generales a todas las preparaciones.docx")

st.header("2. Dieta 3 días previos")
mostrar_docx_con_estilo("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

st.header("3. Instrucciones de Preparación")
mostrar_docx_con_estilo(archivo_prep)

st.header("4. Ayuno Final")
mostrar_docx_con_estilo("textos/AYUNO PARA TODAS LA PREPARACIONES.docx")

st.header("5. Después del Estudio")
mostrar_docx_con_estilo("textos/despues de mi endoscopia.docx")

st.divider()

# Botón AL FINAL (como pediste)
if st.button("📄 GENERAR PDF"):

    datos_pdf = {
        "Alertas Antes del Estudio": texto_docx("textos/Alertas Generales a todas las preparaciones.docx"),
        "Dieta 3 días previos": texto_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx"),
        "Instrucciones de Preparación": texto_docx(archivo_prep),
        "Ayuno": texto_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx"),
        "Después de la Endoscopía": texto_docx("textos/despues de mi endoscopia.docx")
    }

    nombre_plan = f"{familia} {franja}"
    ruta_pdf = generar_pdf_profesional(nombre_plan, datos_pdf)

    with open(ruta_pdf, "rb") as f:
        st.download_button(
            label="⬇️ Descargar PDF",
            data=f.read(),
            file_name=f"Plan_Endoscopia_{familia}_{franja.replace(' ','_')}.pdf",
            mime="application/pdf"
        )

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("Indicaciones después del estudio")
    mostrar_docx_con_estilo("textos/despues de mi endoscopia.docx")
