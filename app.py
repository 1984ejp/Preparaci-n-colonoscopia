import streamlit as st
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

    estilo_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=16)
    estilo_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=13)
    estilo_texto = ParagraphStyle('Texto', parent=styles['Normal'], fontSize=11, alignment=TA_LEFT)

    elementos = []
    elementos.append(Paragraph(f"PLAN DE PREPARACIÓN: {titulo_plan}", estilo_titulo))

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
# MOSTRAR DOCX
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
# ANTES (SIN ARCHIVO)
# --------------------------------------------------

if opcion == "ANTES DE MI ENDOSCOPIA":

    st.header("Alertas Generales")

    st.markdown("""
1. Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo.  
2. Debe traer la orden del estudio vigente y debidamente autorizada si corresponde.  
3. Debe concurrir acompañado.  

**PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS ÍTEMS ANTERIORES**

• 8 hs antes del estudio suspender todo alimento sólido y lácteo. Puede continuar con agua y/o Gatorade (manzana o limón) hasta 4 hs antes.  
• NO debe concurrir con las uñas pintadas o esmaltadas.  
• DEBE quitarse anillos, aros y/o piercings.  

**TENER EN CUENTA:**

- Esta preparación produce diarrea intensa → realizarla en domicilio.  
- Durante el estudio pueden extraerse pólipos o biopsias.  
- Riesgo de perforación:
    - Terapéutica: 0.15% – 2.14%  
    - Diagnóstica: ~1 cada 2000 estudios  
""")

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

    # Definir archivo
    if familia == "BAREX KIT":
        archivo_prep = f"textos/BAREX KIT DE {'7 A 12' if franja=='7 A 12' else '12 A 19'}.docx"
    elif familia == "POLIETILENGLICOL":
        archivo_prep = f"textos/POLIETILENGLICOL 4 litros de {franja}HS.docx"
    else:
        archivo_prep = f"textos/{familia} DE {franja}.docx"

    st.divider()

    st.subheader("Preparación")
    mostrar_docx(archivo_prep)

    st.subheader("Después del estudio")
    mostrar_docx("textos/despues de mi endoscopia.docx")

    st.divider()

    # PDF directo (UN SOLO BOTÓN)
    nombre_plan = f"{familia} {franja}"

    datos_pdf = {
        "Antes del Estudio": """
Si toma medicación que altere la coagulación consulte con su médico.
Debe traer orden vigente.
Debe concurrir acompañado.

8 hs antes: sin sólidos ni lácteos.
Puede tomar agua o Gatorade hasta 4 hs antes.

No uñas pintadas.
Retirar anillos y piercings.

Produce diarrea intensa.
Puede haber biopsias o polipectomía.
Riesgo bajo de perforación.
""",
        "Después del Estudio": texto_docx("textos/despues de mi endoscopia.docx")
    }

    ruta_pdf = generar_pdf_profesional(nombre_plan, datos_pdf)

    with open(ruta_pdf, "rb") as f:
        st.download_button(
            label="📄 Descargar PDF",
            data=f.read(),
            file_name=f"Plan_{familia}_{franja.replace(' ','_')}.pdf",
            mime="application/pdf"
        )

# --------------------------------------------------
# DESPUÉS
# --------------------------------------------------

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":

    st.header("Indicaciones después del estudio")
    mostrar_docx("textos/despues de mi endoscopia.docx")