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
# REINICIAR Y UTILIDADES
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
# ESTILO CSS (TU DISEÑO ORIGINAL)
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
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# FUNCIONES DE DIAGRAMACIÓN (ANTES Y DESPUÉS)
# --------------------------------------------------
def mostrar_alertas():
    # TEXTOS COMPLETOS RESTAURADOS
    alertas = [
        ("⚠️", "Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo."),
        ("📄", "Debe traer la orden del estudio vigente y debidamente autorizada si corresponde."),
        ("👥", "Debe concurrir acompañado."),
        ("✅", "PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS 4 ÍTEMS ANTERIORES."),
        ("⏰", "8 hs antes del estudio suspende todo alimento sólido y lácteo. Puede continuar con agua y/o Gatorade (sabor manzana o limón) hasta 4 hs antes del procedimiento."),
        ("🚫", "NO debe concurrir con las uñas pintadas o esmaltadas."),
        ("🚫", "DEBE quitarse los anillos, aros y/o piercings antes del estudio."),
        ("💧", "Esta preparación produce una diarrea intensa, por lo que debe realizarla en su domicilio y no en su ámbito laboral."),
        ("⚠️", "Es importante que sepa que durante el estudio se pueden extraer pólipos y tomar biopsias. Entre los riesgos potenciales del método está la perforación microscópica o completa del intestino grueso.")
    ]
    for icono, texto in alertas:
        st.markdown(f"""
        <div style="background:white; padding:24px; border-radius:16px; margin-bottom:18px; border-left:8px solid #4da6ff; box-shadow:0px 6px 16px rgba(0,0,0,0.07); line-height:1.7; font-size:24px;">
        <b>{icono}</b> {texto}
        </div>""", unsafe_allow_html=True)

def mostrar_post_endoscopia(ruta):
    if not os.path.exists(ruta): 
        st.error("No se encontró el archivo post-endoscopía.")
        return
    doc = Document(ruta)
    parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip() != ""]
    
    orden_secciones = [
        "1. Observaciones iniciales", "2. Cuidados en el domicilio", 
        "3. Signos de alarma – acudir de inmediato", "4. Contacto de urgencia", 
        "5. Indicaciones primeras 12 horas", "6. Toma de muestras – Anatomía Patológica"
    ]
    
    bloques = {titulo: "" for titulo in orden_secciones}
    titulo_actual = None

    for p in parrafos:
        p_low = p.lower()
        if "observaciones iniciales" in p_low: titulo_actual = "1. Observaciones iniciales"
        elif "cuidados en el domicilio" in p_low: titulo_actual = "2. Cuidados en el domicilio"
        elif "signos de alarma" in p_low: titulo_actual = "3. Signos de alarma – acudir de inmediato"
        elif "contacto de urgencia" in p_low: titulo_actual = "4. Contacto de urgencia"
        elif "12 horas" in p_low: titulo_actual = "5. Indicaciones primeras 12 horas"
        elif "anatomía patológica" in p_low: titulo_actual = "6. Toma de muestras – Anatomía Patológica"
        elif titulo_actual: bloques[titulo_actual] += p + " "

    for titulo in orden_secciones:
        contenido = bloques[titulo].strip()
        if contenido:
            color = "#ff4d4d" if "alarma" in titulo.lower() else "#4da6ff"
            st.markdown(f"""
            <div style="background:white; padding:20px; border-radius:12px; margin-bottom:15px; border-left:8px solid {color}; box-shadow:0px 4px 10px rgba(0,0,0,0.05);">
                <b style="font-size:22px;">{titulo}</b><br><span style="font-size:19px;">{contenido}</span>
            </div>""", unsafe_allow_html=True)

# --------------------------------------------------
# DETECTAR ICONOS (PARA MOSTRAR_DOCX EN PREPARACIÓN)
# --------------------------------------------------
def detectar_icono(texto):
    t = texto.lower()
    if any(x in t for x in ["no debe", "quitar", "suspenda", "🚫"]): return "🚫","#ffeaea","#ff4d4d"
    if any(x in t for x in ["riesgo", "perforación", "biopsia", "⚠️"]): return "⚠️","#fff7cc","#f0ad4e"
    return "✅","white","#4da6ff"

def mostrar_docx(ruta):
    if not os.path.exists(ruta): return
    doc = Document(ruta)
    for p in doc.paragraphs:
        if p.text.strip():
            ico, fondo,