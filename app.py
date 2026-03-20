import streamlit as st
import base64
from docx import Document
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import tempfile

st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --------------------------------------------------
# FUNCIONES DE APOYO Y REINICIAR
# --------------------------------------------------

def reiniciar():
    st.session_state.clear()
    st.rerun()

def texto_docx(ruta):
    if not os.path.exists(ruta): return ""
    try:
        doc = Document(ruta)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except: return ""

# --------------------------------------------------
# ESTILO CSS (TAL CUAL TU CÓDIGO)
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
.card{
    background:white; padding:28px; border-radius:22px;
    box-shadow:0px 8px 24px rgba(0,0,0,0.08);
}
@media (max-width: 768px){
    html,body,[class*="css"]{ font-size:18px !important; }
    h1{ font-size:32px !important; }
    .card{ padding:18px; }
    .stButton button{ font-size:18px !important; padding:12px; }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DETECTAR ICONOS Y MOSTRAR DOCX
# --------------------------------------------------

def detectar_icono(texto):
    t = texto.lower()
    if any(x in t for x in ["no debe", "quitar", "suspenda", "🚫"]): return "🚫","#ffeaea","#ff4d4d"
    if any(x in t for x in ["riesgo", "perforación", "biopsia", "⚠️"]): return "⚠️","#fff7cc","#f0ad4e"
    if "hs" in t: return "⏰","white","#4da6ff"
    return "✅","white","#4da6ff"

def mostrar_docx_estilizado(ruta):
    if not os.path.exists(ruta):
        st.error(f"No se encontró: {ruta}")
        return
    doc = Document(ruta)
    for p in doc.paragraphs:
        texto = p.text.strip()
        if texto:
            ico, fondo, color = detectar_icono(texto)
            st.markdown(f"""
            <div style="background:{fondo}; padding:24px; border-radius:16px; margin-bottom:18px; 
            line-height:1.7; font-size:24px; box-shadow:0px 6px 16px rgba(0,0,0,0.07); border-left:8px solid {color};">
            <b>{ico}</b> {texto}
            </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------
# GENERAR PDF COMPLETO
# --------------------------------------------------

def generar_pdf_completo(titulo, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()
    style_h = styles["Heading2"]
    style_b = styles["Normal"]
    style_b.fontSize = 11
    
    story = [Paragraph(f"PLAN DE ENDOSCOPÍA: {titulo}", styles["Heading1"]), Spacer(1, 20)]
    for nom, cont in secciones:
        if cont.strip():
            story.append(Paragraph(nom, style_h))
            story.append(Paragraph(cont.replace("\n", "<br/>"), style_b))
            story.append(Spacer(1, 15))
    doc.build(story)
    return tmp.name

# --------------------------------------------------
# IMAGEN FRANCISCO
# --------------------------------------------------

def get_img64(path):
    if not os.path.exists(path): return None
    with open(path,"rb") as f: return base64.b64encode(f.read()).decode()

img = get_img64("francisco.png")

# --------------------------------------------------
# LAYOUT PRINCIPAL
# --------------------------------------------------

col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Hola, soy Francisco 👋")
    opcion = st.radio("Elegí una opción:", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    
    if st.button("🔄 REINICIAR"):
        reiniciar()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if img:
        st.markdown(f'<div class="hide-mobile" style="display:flex;justify-content:center;"><img src="data:image/png;base64,{img}" style="width:100%;max-width:400px;border-radius:24px;"></div>', unsafe_allow_html=True)

st.divider()

# --------------------------------------------------
# LÓGICA DE OPCIONES
# --------------------------------------------------

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.header("Indicaciones Generales")
    mostrar_docx_estilizado("textos/Alertas Generales a todas las preparaciones.docx")
    st.header("Dieta 3 días previos")
    mostrar_docx_estilizado("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

elif opcion == "MI PREPARACIÓN":
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Horario:", ["7 A 12", "12 A 16", "16 A 19"])
    with c2:
        ant = st.multiselect("Antecedentes:", ["Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca", "Hipertensión Arterial"])
        med = st.multiselect("Medicación:", ["Aspirina (AAS)", "Anticoagulantes", "Insulina"])

    # Validación de seguridad
    if familia == "FOSFATOS" and any(x in ant for x in ["Insuficiencia Renal", "Insuficiencia Cardíaca"]):
        st.error("🚨 Los FOSFATOS están contraindicados para usted. Consulte a su médico.")
    else:
        if st.button("GENERAR MI PLAN Y PDF"):
            archivos = {
                "BAREX KIT": f"textos/BAREX KIT DE {'7 A 12' if franja == '7 A 12' else '12 A 19'}.docx",
                "FOSFATOS": f"textos/FOSFATOS DE {franja}.docx",
                "PICOSULFATO": f"textos/PICOSULFATO DE {franja}.docx",
                "POLIETINELGLICOL": f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"
            }
            ruta_p = archivos.get(familia)
            
            st.header("Tu Instrucción de Preparación")
            mostrar_docx_estilizado(ruta_p)
            
            # PDF con secciones completas
            secciones = [
                ("ANTES DEL ESTUDIO", texto_docx("textos/Alertas Generales a todas las preparaciones.docx")),
                ("DIETA PREVIA", texto_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")),
                ("PREPARACIÓN", texto_docx(ruta_p)),
                ("DESPUÉS DEL ESTUDIO", texto_docx("textos/despues de mi endoscopia.docx"))
            ]
            pdf_path = generar_pdf_completo(f"{familia} - {franja}", secciones)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Descargar Guía Completa (PDF)", f, file_name=f"Plan_{familia}.pdf")

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("Cuidados Post-Estudio")
    mostrar_docx_estilizado("textos/despues de mi endoscopia.docx")