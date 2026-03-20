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
    doc = Document(ruta)
    return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])

# --------------------------------------------------
# ESTILO CSS ORIGINAL
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
# DETECTAR ICONOS Y MOSTRAR DOCX (ESTÉTICA ORIGINAL)
# --------------------------------------------------
def detectar_icono(texto):
    t = texto.lower()
    if "no debe" in t or "quitar" in t or "suspenda" in t: return "🚫","#ffeaea","#ff4d4d"
    if "riesgo" in t or "perforación" in t or "biopsia" in t or "pólipo" in t: return "⚠️","#fff7cc","#f0ad4e"
    if "hs" in t: return "⏰","white","#4da6ff"
    return "✅","white","#4da6ff"

def mostrar_docx(ruta):
    if not os.path.exists(ruta):
        st.error(f"No se encontró: {ruta}")
        return
    doc = Document(ruta)
    for p in doc.paragraphs:
        texto = p.text.strip()
        if texto:
            icono, fondo, color = detectar_icono(texto)
            st.markdown(f"""
            <div style="background:{fondo}; padding:24px; border-radius:16px; margin-bottom:18px; 
            line-height:1.7; font-size:24px; box-shadow:0px 6px 16px rgba(0,0,0,0.07); border-left:8px solid {color};">
            <b>{icono}</b> {texto}
            </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------
# FUNCIONES ESPECÍFICAS DE DIAGRAMACIÓN
# --------------------------------------------------
def mostrar_alertas():
    alertas = [
        ("⚠️","Si toma medicación que altere la coagulación..."),
        ("📄","Debe traer la orden del estudio vigente..."),
        ("👥","Debe concurrir acompañado."),
        ("✅","PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS 4 ÍTEMS ANTERIORES."),
        ("⏰","8 hs antes del estudio suspende todo alimento sólido..."),
        ("🚫","NO debe concurrir con las uñas pintadas..."),
        ("🚫","DEBE quitarse los anillos, aros y/o piercings..."),
        ("💧","Esta preparación produce una diarrea intensa..."),
        ("⚠️","Es importante que sepa que durante el estudio se pueden extraer pólipos...")
    ]
    for icono, texto in alertas:
        st.markdown(f"""
        <div style="background:white; padding:24px; border-radius:16px; margin-bottom:18px; border-left:8px solid #4da6ff; box-shadow:0px 6px 16px rgba(0,0,0,0.07);">
        <b>{icono}</b> {texto}
        </div>""", unsafe_allow_html=True)

def mostrar_post_endoscopia(ruta):
    if not os.path.exists(ruta): return
    doc = Document(ruta)
    parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip() != ""]
    orden = ["1. Observaciones iniciales", "2. Cuidados en el domicilio", "3. Signos de alarma", "4. Contacto de urgencia", "5. Indicaciones primeras 12 horas", "6. Toma de muestras"]
    bloques = {t: "" for t in orden}
    curr = None
    for p in parrafos:
        for t in orden:
            if t.lower() in p.lower(): curr = t
        if curr: bloques[curr] += p + " "

    for titulo in orden:
        cont = bloques[titulo].strip()
        if cont:
            color = "#ff4d4d" if "alarma" in titulo.lower() else "#4da6ff"
            st.markdown(f"""
            <div style="background:white; padding:20px; border-radius:12px; margin-bottom:15px; border-left:8px solid {color}; box-shadow:0px 4px 10px rgba(0,0,0,0.05);">
                <b style="font-size:22px;">{titulo}</b><br><span style="font-size:19px;">{cont}</span>
            </div>""", unsafe_allow_html=True)

# --------------------------------------------------
# PDF Y IMAGEN
# --------------------------------------------------
def generar_pdf_completo(titulo, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"PLAN: {titulo}", styles["Heading1"]), Spacer(1, 20)]
    for nom, cont in secciones:
        if cont.strip():
            story.append(Paragraph(nom, styles["Heading2"]))
            story.append(Paragraph(cont.replace("\n", "<br/>"), styles["Normal"]))
    doc.build(story)
    return tmp.name

def get_img64(path):
    if not os.path.exists(path): return None
    with open(path,"rb") as f: return base64.b64encode(f.read()).decode()

# --------------------------------------------------
# INTERFAZ
# --------------------------------------------------
img = get_img64("francisco.png")
col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Hola, soy Francisco 👋")
    opcion = st.radio("Elegí una opción:", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    if st.button("🔄 REINICIAR"): reiniciar()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if img: st.markdown(f'<div class="hide-mobile" style="text-align:center;"><img src="data:image/png;base64,{img}" style="width:100%; border-radius:24px;"></div>', unsafe_allow_html=True)

st.divider()

if opcion == "ANTES DE MI ENDOSCOPIA":
    mostrar_alertas()
    st.header("Dieta 3 días previos")
    mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

elif opcion == "MI PREPARACIÓN":
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Horario:", ["7 A 12", "12 A 16", "16 A 19"])
    with c2:
        ant = st.multiselect("Antecedentes:", ["Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca"])
    
    if familia == "FOSFATOS" and any(x in ant for x in ["Insuficiencia Renal", "Insuficiencia Cardíaca"]):
        st.error("🚨 Contraindicado: Los FOSFATOS no son seguros para sus antecedentes.")
    elif st.button("GENERAR PLAN"):
        archs = {"BAREX KIT": f"textos/BAREX KIT DE {'7 A 12' if franja=='7 A 12' else '12 A 19'}.docx", "FOSFATOS": f"textos/FOSFATOS DE {franja}.docx", "PICOSULFATO": f"textos/PICOSULFATO DE {franja}.docx", "POLIETINELGLICOL": f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"}
        ruta_p = archs.get(familia)
        mostrar_docx(ruta_p)
        
        sec_pdf = [("ANTES", texto_docx("textos/Alertas Generales a todas las preparaciones.docx")), ("PREPARACIÓN", texto_docx(ruta_p)), ("POST", texto_docx("textos/despues de mi endoscopia.docx"))]
        path_pdf = generar_pdf_completo(familia, sec_pdf)
        with open(path_pdf, "rb") as f:
            st.download_button("📥 Descargar Guía Completa", f, file_name="Plan.pdf")

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("Indicaciones después del estudio")
    mostrar_post_endoscopia("textos/despues de mi endoscopia.docx")