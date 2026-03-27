import streamlit as st
from docx import Document
import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT

# Configuración de página
st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --------------------------------------------------
# FUNCIONES DE UTILIDAD
# --------------------------------------------------

def reiniciar():
    st.session_state.clear()
    st.rerun()

def obtener_ruta_completa(ruta_relativa):
    # Obtiene la ruta absoluta respecto al archivo actual
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, ruta_relativa)

def texto_docx(ruta):
    """Extrae texto de un DOCX para usarlo en el PDF."""
    try:
        path = obtener_ruta_completa(ruta)
        if not os.path.exists(path):
            return ""
        doc = Document(path)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    except Exception:
        return ""

# --------------------------------------------------
# GENERACIÓN DE PDF
# --------------------------------------------------

def generar_pdf_profesional(titulo_plan, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=16, spaceAfter=12)
    estilo_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=13, spaceBefore=10, spaceAfter=5)
    estilo_texto = ParagraphStyle('Texto', parent=styles['Normal'], fontSize=11, alignment=TA_LEFT, leading=14)

    elementos = []
    elementos.append(Paragraph(f"PLAN DE PREPARACIÓN: {titulo_plan}", estilo_titulo))

    for nombre, contenido in secciones.items():
        if contenido:
            elementos.append(Paragraph(nombre, estilo_subtitulo))
            for linea in contenido.split("\n"):
                if linea.strip():
                    # Limpieza básica de caracteres especiales para ReportLab
                    linea_limpia = linea.replace("•", "-").strip()
                    elementos.append(Paragraph(linea_limpia, estilo_texto))
            elementos.append(Spacer(1, 10))

    doc.build(elementos)
    return tmp.name

def mostrar_docx_en_ui(ruta):
    """Muestra el contenido del DOCX en la interfaz de Streamlit."""
    try:
        path = obtener_ruta_completa(ruta)
        if os.path.exists(path):
            doc = Document(path)
            for p in doc.paragraphs:
                if p.text.strip():
                    st.markdown(f"- {p.text}")
        else:
            st.warning(f"Archivo no encontrado: {ruta}")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")

# --------------------------------------------------
# INTERFAZ DE USUARIO (UI)
# --------------------------------------------------

st.title("🏥 Asistente de Preparación Endoscópica")

opcion = st.sidebar.radio(
    "Menú de Navegación:",
    ["ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"]
)

if st.sidebar.button("🔄 Reiniciar Aplicación"):
    reiniciar()

st.divider()

# --- SECCIÓN: ANTES ---
if opcion == "ANTES DE MI ENDOSCOPIA":
    st.header("Alertas Generales")
    st.info("Por favor, lea atentamente estas indicaciones antes de su estudio.")
    
    st.markdown("""
    1. **Medicación:** Si toma anticoagulantes o antiagregantes, consulte con hematología.
    2. **Documentación:** Traer orden vigente y autorizada.
    3. **Acompañante:** Es obligatorio concurrir acompañado por un adulto.
    
    **REQUISITOS CRÍTICOS:**
    * **Ayuno:** 8 hs de sólidos y lácteos. Líquidos claros (agua/Gatorade) hasta 4 hs antes.
    * **Estética:** Sin uñas pintadas, sin anillos ni piercings.
    
    **INFORMACIÓN MÉDICA:**
    * La preparación causa diarrea intensa (realizar en domicilio).
    * Riesgo de perforación diagnóstica: ~1 cada 2000 estudios.
    """)

# --- SECCIÓN: PREPARACIÓN ---
elif opcion == "MI PREPARACIÓN":
    col1, col2 = st.columns(2)
    
    with col1:
        familia = st.selectbox(
            "Tipo de preparación prescrita:",
            ["FOSFATOS", "PICOSULFATO", "POLIETILENGLICOL", "BAREX KIT"]
        )
    
    with col2:
        franja = st.radio(
            "Horario de su turno:",
            ["7 A 12", "12 A 16", "16 A 19"]
        )

    # Lógica de archivos
    if familia == "BAREX KIT":
        # Ajuste de lógica para Barex Kit según tu código original
        horario_file = "7 A 12" if franja == "7 A 12" else "12 A 19"
        archivo_prep = f"textos/BAREX KIT DE {horario_file}.docx"
    elif familia == "POLIETILENGLICOL":
        archivo_prep = f"textos/POLIETILENGLICOL 4 litros de {franja}HS.docx"
    else:
        archivo_prep = f"textos/{familia} DE {franja}.docx"

    st.subheader(f"Instrucciones para {familia}")
    mostrar_docx_en_ui(archivo_prep)

    # --- GENERACIÓN DE PDF ---
    st.divider()
    if st.button("🛠️ Preparar documento para descarga"):
        texto_preparacion = texto_docx(archivo_prep)
        texto_post = texto_docx("textos/despues de mi endoscopia.docx")
        
        datos_pdf = {
            "INDICACIONES PREVIAS": "8hs Ayuno sólidos. 4hs Ayuno líquidos claros. Concurrir acompañado.",
            f"INSTRUCCIONES DE {familia}": texto_preparacion,
            "CUIDADOS POST-ESTUDIO": texto_post
        }

        ruta_pdf = generar_pdf_profesional(f"{familia} ({franja}hs)", datos_pdf)
        
        with open(ruta_pdf, "rb") as f:
            st.download_button(
                label="📥 Descargar Plan en PDF",
                data=f.read(),
                file_name=f"Plan_Preparacion_{familia.replace(' ','_')}.pdf",
                mime="application/pdf"
            )

# --- SECCIÓN: DESPUÉS ---
elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("Indicaciones Post-Estudio")
    mostrar_docx_en_ui("textos/despues de mi endoscopia.docx")