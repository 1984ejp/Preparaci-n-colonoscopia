import streamlit as st
import base64
from docx import Document
import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT

st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --------------------------------------------------
# FUNCIONES
# --------------------------------------------------

def reiniciar():
    st.session_state.clear()
    st.rerun()

def obtener_ruta_completa(ruta_relativa):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, ruta_relativa)

def texto_docx(ruta):
    try:
        doc = Document(obtener_ruta_completa(ruta))
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    except:
        return ""

# --------------------------------------------------
# PDF
# --------------------------------------------------

def generar_pdf_profesional(titulo_plan, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=18)
    estilo_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=14)
    estilo_texto = ParagraphStyle('Texto', parent=styles['Normal'], fontSize=11, alignment=TA_LEFT)

    elementos = []
    elementos.append(Paragraph(f"PLAN: {titulo_plan}", estilo_titulo))

    for nombre, contenido in secciones.items():
        if contenido:
            elementos.append(Spacer(1, 10))
            elementos.append(Paragraph(nombre, estilo_subtitulo))

            for linea in contenido.split("\n"):
                if linea.strip():
                    elementos.append(Paragraph(linea, estilo_texto))

    doc.build(elementos)
    return tmp.name

# --------------------------------------------------
# UI DOCX
# --------------------------------------------------

def mostrar_docx(ruta):
    try:
        doc = Document(obtener_ruta_completa(ruta))
        for p in doc.paragraphs:
            if p.text.strip():
                st.markdown(f"- {p.text}")
    except:
        st.warning(f"No se pudo cargar: {ruta}")

# --------------------------------------------------
# UI
# --------------------------------------------------

st.title("Asistente de Preparación Endoscópica")

opcion = st.radio(
    "Elegí una opción:",
    ["ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"]
)

if st.button("🔄 Reiniciar"):
    reiniciar()

st.divider()

# --------------------------------------------------
# ANTES
# --------------------------------------------------

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.header("Alertas Generales")
    mostrar_docx("textos/Alertas Generales a todas las preparaciones.docx")

# --------------------------------------------------
# PREPARACIÓN
# --------------------------------------------------

elif opcion == "MI PREPARACIÓN":

    familia = st.selectbox(
        "Tipo de preparación",
        ["FOSFATOS", "PICOSULFATO", "POLIETILENGLICOL", "BAREX KIT"]
    )

    franja = st.radio(
        "Horario del estudio",
        ["7 A 12", "12 A 16", "16 A 19"]
    )

    # Archivo
    if familia == "BAREX KIT":
        archivo_prep = f"textos/BAREX KIT DE {'7 A 12' if franja=='7 A 12' else '12 A 19'}.docx"
    elif familia == "POLIETILENGLICOL":
        archivo_prep = f"textos/POLIETILENGLICOL 4 litros de {franja}HS.docx"
    else:
        archivo_prep = f"textos/{familia} DE {franja}.docx"

    st.divider()

    st.subheader("1. Alertas")
    mostrar_docx("textos/Alertas Generales a todas las preparaciones.docx")

    st.subheader("2. Dieta")
    mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

    st.subheader("3. Preparación")
    mostrar_docx(archivo_prep)

    st.subheader("4. Ayuno")
    mostrar_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx")

    st.subheader("5. Después del estudio")
    mostrar_docx("textos/despues de mi endoscopia.docx")

    st.divider()

    # PDF
    if st.button("📄 Generar PDF"):

        datos_pdf = {
            "Alertas": texto_docx("textos/Alertas Generales a todas las preparaciones.docx"),
            "Dieta": texto_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx"),
            "Preparación": texto_docx(archivo_prep),
            "Ayuno": texto_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx"),
            "Después": texto_docx("textos/despues de mi endoscopia.docx")
        }

        ruta_pdf = generar_pdf_profesional(f"{familia} {franja}", datos_pdf)

        with open(ruta_pdf, "rb") as f:
            st.download_button(
                "⬇️ Descargar PDF",
                f.read(),
                file_name="plan_endoscopia.pdf",
                mime="application/pdf"
            )

# --------------------------------------------------
# DESPUÉS
# --------------------------------------------------

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("Indicaciones")
    mostrar_docx("textos/despues de mi endoscopia.docx")