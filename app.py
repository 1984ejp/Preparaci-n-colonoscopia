import streamlit as st
import base64
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import tempfile

st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --------------------------------------------------
# FUNCIONES DE APOYO (RUTAS ORIGINALES)
# --------------------------------------------------

def obtener_ruta(nombre_archivo):
    """Busca el archivo en la raíz del proyecto."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, nombre_archivo)

def texto_docx(ruta_relativa):
    ruta_c = obtener_ruta(ruta_relativa)
    if not os.path.exists(ruta_c):
        return ""
    try:
        doc = Document(ruta_c)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except:
        return ""

def detectar_icono(texto):
    t = texto.lower()
    if any(x in t for x in ["no debe", "quitar", "prohibido"]): return "🚫", "#ffeaea", "#ff4d4d"
    if any(x in t for x in ["riesgo", "perforación", "biopsia", "pólipo", "atención", "importante"]): return "⚠️", "#fff7cc", "#f0ad4e"
    if "hs" in t or "hora" in t: return "⏰", "white", "#4da6ff"
    return "✅", "white", "#4da6ff"

def generar_pdf_completo(titulo_doc, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()
    style_title, style_header, style_body = styles["Heading1"], styles["Heading2"], styles["Normal"]
    style_title.alignment = TA_CENTER
    style_body.fontSize, style_body.leading = 11, 14
    
    story = [Paragraph(f"GUÍA DE ENDOSCOPÍA: {titulo_doc}", style_title), Spacer(1, 20)]
    for nombre_seccion, contenido in secciones:
        if contenido.strip():
            story.append(Paragraph(nombre_seccion, style_header))
            story.append(Spacer(1, 8))
            story.append(Paragraph(contenido.replace("\n", "<br/>"), style_body))
            story.append(Spacer(1, 15))
    doc.build(story)
    return tmp.name

def mostrar_docx_visual(ruta_relativa):
    ruta_c = obtener_ruta(ruta_relativa)
    if not os.path.exists(ruta_c):
        st.error(f"Archivo no encontrado: {ruta_relativa}")
        return
    doc = Document(ruta_c)
    for p in doc.paragraphs:
        texto = p.text.strip()
        if texto:
            icono, fondo, color = detectar_icono(texto)
            st.markdown(f'<div style="background:{fondo}; padding:18px; border-radius:12px; margin-bottom:12px; border-left:8px solid {color}; box-shadow:0px 4px 10px rgba(0,0,0,0.05);"><b style="font-size:20px;">{icono}</b> <span style="font-size:18px;">{texto}</span></div>', unsafe_allow_html=True)

# --------------------------------------------------
# INTERFAZ
# --------------------------------------------------

col1, col2 = st.columns([1.5, 1])
with col1:
    st.title("Hola, soy Francisco 👋")
    opcion = st.radio("¿Qué necesitas consultar?", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])

with col2:
    img = obtener_ruta("francisco.png")
    if os.path.exists(img): st.image(img, width=280)

st.divider()

if opcion == "ANTES DE MI ENDOSCOPIA":
    # NOTA: Estos archivos están en la raíz según tu primer código
    mostrar_docx_visual("Alertas Generales a todas las preparaciones.docx")
    st.subheader("Dieta de los 3 días previos")
    mostrar_docx_visual("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

elif opcion == "MI PREPARACIÓN":
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Horario:", ["7 A 12", "12 A 16", "16 A 19"])
    with c2:
        ant = st.multiselect("Antecedentes:", ["Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca", "Hipertensión"])
        med = st.multiselect("Medicación:", ["Aspirina", "Clopidogrel", "Sintrom", "Insulina", "Metformina"])

    if st.button("GENERAR GUÍA", use_container_width=True):
        # Rutas dentro de /textos
        if familia == "BAREX KIT":
            ruta_p = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        elif familia == "FOSFATOS":
            ruta_p = f"textos/FOSFATOS DE {franja}.docx"
        elif familia == "PICOSULFATO":
            ruta_p = f"textos/PICOSULFATO DE {franja}.docx"
        else:
            ruta_p = f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"
        
        mostrar_docx_visual(ruta_p)
        
        # PDF con archivos de raíz y de /textos
        info_med = f"ANTECEDENTES: {', '.join(ant)}\nMEDICACIÓN: {', '.join(med)}"
        secciones = [
            ("DATOS DEL PACIENTE", info_med),
            ("ALERTAS GENERALES", texto_docx("Alertas Generales a todas las preparaciones.docx")),
            ("PREPARACIÓN", texto_docx(ruta_p)),
            ("DESPUÉS DEL ESTUDIO", texto_docx("despues de mi endoscopia.docx"))
        ]
        path_pdf = generar_pdf_completo(f"{familia}_{franja}", secciones)
        with open(path_pdf, "rb") as f:
            st.download_button("📥 Descargar PDF", f, file_name=f"{familia}_{franja}.pdf", use_container_width=True)

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    # El archivo está en la raíz
    mostrar_docx_visual("despues de mi endoscopia.docx")