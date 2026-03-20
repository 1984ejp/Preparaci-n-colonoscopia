import streamlit as st
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import tempfile

st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --- FUNCIONES ORIGINALES ---
def obtener_ruta(nombre_archivo):
    ruta_raiz = os.path.join(os.getcwd(), nombre_archivo)
    ruta_textos = os.path.join(os.getcwd(), "textos", nombre_archivo)
    if os.path.exists(ruta_raiz): return ruta_raiz
    return ruta_textos

def texto_docx(nombre_archivo):
    ruta = obtener_ruta(nombre_archivo)
    if not os.path.exists(ruta): return ""
    try:
        doc = Document(ruta)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except: return ""

def detectar_icono_original(texto):
    t = texto.lower()
    if any(x in t for x in ["no debe", "quitar", "suspenda", "🚫"]): return "🚫", "#ffeaea", "#ff4d4d"
    if any(x in t for x in ["riesgo", "perforación", "biopsia", "importante", "⚠️"]): return "⚠️", "#fff7cc", "#f0ad4e"
    if "hs" in t or "⏰" in t: return "⏰", "white", "#4da6ff"
    return "✅", "white", "#4da6ff"

def generar_pdf_clinico(titulo_doc, secciones, alertas):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()
    style_n = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=14)
    style_a = ParagraphStyle('Alert', parent=styles['Normal'], color='red', fontSize=12, leading=14)
    
    story = [Paragraph(f"PLAN DE ESTUDIO: {titulo_doc}", styles["Heading1"]), Spacer(1, 12)]
    
    if alertas:
        story.append(Paragraph("OBSERVACIONES MÉDICAS:", styles["Heading2"]))
        for a in alertas:
            story.append(Paragraph(f"• {a}", style_a))
        story.append(Spacer(1, 15))

    for nombre, contenido in secciones:
        if contenido.strip():
            story.append(Paragraph(nombre, styles["Heading2"]))
            story.append(Paragraph(contenido.replace("\n", "<br/>"), style_n))
            story.append(Spacer(1, 12))
            
    doc.build(story)
    return tmp.name

# --- INTERFAZ ---
col_txt, col_img = st.columns([1.5, 1])

with col_img:
    img_path = obtener_ruta("francisco.png")
    if os.path.exists(img_path):
        st.image(img_path, width=250)
    # BOTÓN REINICIAR ENTRE IMAGEN Y OPCIONES
    if st.button("🔄 REINICIAR TODO", use_container_width=True):
        st.rerun()

with col_txt:
    st.title("Hola, soy Francisco 👋")
    opcion = st.radio("Menú Principal:", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])

st.divider()

# --- LÓGICA DE SECCIONES BASADA EN TU PRIMER CÓDIGO ---

if opcion == "ANTES DE MI ENDOSCOPIA":
    archivo_antes = "Alertas Generales a todas las preparaciones.docx"
    ruta = obtener_ruta(archivo_antes)
    if os.path.exists(ruta):
        doc = Document(ruta)
        for i, p in enumerate(doc.paragraphs):
            if p.text.strip():
                ico, fnd, clr = detectar_icono_original(p.text)
                # Mantengo el diagramado original 1, 2, 3...
                st.markdown(f'<div style="background:{fnd}; padding:15px; border-radius:10px; margin-bottom:10px; border-left:8px solid {clr};">{i+1}. {ico} {p.text}</div>', unsafe_allow_html=True)

elif opcion == "MI PREPARACIÓN":
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Horario:", ["7 A 12", "12 A 16", "16 A 19"])
    with c2:
        ant = st.multiselect("Antecedentes:", ["Sin antecedentes", "Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca", "Hipertensión Arterial"])
        med = st.multiselect("Medicación:", ["Sin medicación", "Aspirina (AAS)", "Clopidogrel / Ticagrelor", "Sintrom / Anticoagulantes", "Insulina", "Metformina"])

    alertas_f = []
    # Validación FOSFATOS
    if familia == "FOSFATOS" and any(x in ant for x in ["Insuficiencia Renal", "Insuficiencia Cardíaca"]):
        st.error("🚨 CONTRAINDICACIÓN: Los FOSFATOS están contraindicados para sus antecedentes. CONSULTE A SU MÉDICO.")
    else:
        if "Sintrom / Anticoagulantes" in med: alertas_f.append("🩸 Anticoagulantes: Requiere planificación previa.")
        if "Insulina" in med: alertas_f.append("💉 Insulina: Ajustar dosis por ayuno.")
        for a in alertas_f: st.warning(a)

        if st.button("GENERAR MI PLAN Y PDF", use_container_width=True):
            if familia == "BAREX KIT":
                nombre_p = "BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "BAREX KIT DE 12 A 19.docx"
            else:
                mapping = {"FOSFATOS": "FOSFATOS", "PICOSULFATO": "PICOSULFATO", "POLIETINELGLICOL": "POLIETINELGLICOL 4 litros"}
                nombre_p = f"{mapping[familia]} de {franja if familia != 'POLIETINELGLICOL' else franja + 'HS'}.docx"
            
            prep_txt = texto_docx(nombre_p)
            if prep_txt:
                doc_p = Document(obtener_ruta(nombre_p))
                for p in doc_p.paragraphs:
                    if p.text.strip():
                        ico, fnd, clr = detectar_icono_original(p.text)
                        st.markdown(f'<div style="background:{fnd}; padding:15px; border-radius:10px; margin-bottom:10px; border-left:8px solid {clr};">{ico} {p.text}</div>', unsafe_allow_html=True)
                
                # PDF COMPLETO (Preparación + Antes + Después)
                secciones_pdf = [
                    ("PREPARACIÓN", prep_txt),
                    ("ALERTAS GENERALES", texto_docx("Alertas Generales a todas las preparaciones.docx")),
                    ("DESPUÉS DEL ESTUDIO", texto_docx("despues de mi endoscopia.docx"))
                ]
                pdf = generar_pdf_clinico(f"{familia} ({franja})", secciones_pdf, alertas_f)
                with open(pdf, "rb") as f:
                    st.download_button("📥 DESCARGAR PDF COMPLETO", f, file_name=f"Plan_{familia}_{franja}.pdf", use_container_width=True)

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    archivo_post = "despues de mi endoscopia.docx"
    ruta_p = obtener_ruta(archivo_post)
    if os.path.exists(ruta_p):
        doc = Document(ruta_p)
        for i, p in enumerate(doc.paragraphs):
            if p.text.strip():
                ico, fnd, clr = detectar_icono_original(p.text)
                st.markdown(f'<div style="background:{fnd}; padding:15px; border-radius:10px; margin-bottom:10px; border-left:8px solid {clr};">{i+1}. {ico} {p.text}</div>', unsafe_allow_html=True)