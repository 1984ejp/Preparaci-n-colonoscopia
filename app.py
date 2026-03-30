import streamlit as st
import base64
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import tempfile

# CONFIG
st.set_page_config(page_title="Asistente Endoscopía - Francisco", layout="wide")

# TEXTOS
TEXTO_ANTES = """..."""  # (dejalo igual, no lo repito para no ensuciar)

TEXTO_POST = """..."""

# FUNCIONES
def reiniciar():
    st.session_state.clear()
    st.rerun()

def texto_docx(ruta):
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        doc = Document(os.path.join(base, ruta))
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    except:
        return "Error al cargar archivo."

def mostrar_docx(ruta):
    texto = texto_docx(ruta)
    st.markdown(f"""
    <div style="background:white;padding:20px;border-radius:15px;border-left:8px solid #4da6ff;color:#1a1a1a;">
    {texto.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

def generar_pdf(titulo, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('t', parent=styles['Heading1'])
    texto_style = ParagraphStyle('n', parent=styles['Normal'])

    elementos = [Paragraph(titulo, titulo_style)]

    for k, v in secciones.items():
        elementos.append(Spacer(1, 10))
        elementos.append(Paragraph(k, styles['Heading2']))
        for linea in v.split("\n"):
            if linea.strip():
                elementos.append(Paragraph(linea, texto_style))

    doc.build(elementos)
    return tmp.name

# CSS CORREGIDO (CLAVE)
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg,#e9f0f7,#dfe8f3); }

body, .stApp {
    color: #1a1a1a !important;
}

p, li, span {
    color: #1a1a1a !important;
}

.stButton button {
    background:#4da6ff;
    color:white;
    border-radius:12px;
    font-size:18px;
}

</style>
""", unsafe_allow_html=True)

# IMG
def get_img(path):
    if not os.path.exists(path): return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_img("francisco.png")

# UI
col1, col2 = st.columns([1.1,1])

with col1:
    st.markdown("# Hola, soy Francisco 👋")
    opcion = st.radio("Elegí:", ["ANTES DE MI ENDOSCOPIA","MI PREPARACIÓN","DESPUÉS DE MI ENDOSCOPIA"])
    if st.button("Reiniciar"):
        reiniciar()

with col2:
    if img:
        st.image(f"data:image/png;base64,{img}")

# LOGICA

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.header("Indicaciones")
    st.markdown(TEXTO_ANTES.replace("\n","<br>"), unsafe_allow_html=True)

elif opcion == "MI PREPARACIÓN":

    familia = st.selectbox("Preparación", ["FOSFATOS","PICOSULFATO","POLIETILENGLICOL","BAREX KIT"])
    franja = st.radio("Horario", ["7 A 12","12 A 16","16 A 19"])

    # archivo
    if familia == "BAREX KIT":
        archivo = "textos/BAREX KIT DE 7 A 12.docx" if franja=="7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
    elif familia == "POLIETILENGLICOL":
        archivo = f"textos/POLIETILENGLICOL 4 litros de {franja}HS.docx"
    else:
        archivo = f"textos/{familia} DE {franja}.docx"

    st.subheader("Tu preparación")
    mostrar_docx(archivo)

    # PDF DIRECTO (SIN BOTÓN GENERAR)
    secciones = {
        "Antes del estudio": TEXTO_ANTES,
        "Después del estudio": TEXTO_POST
    }

    pdf = generar_pdf(f"{familia} - {franja}", secciones)

    with open(pdf, "rb") as f:
        st.download_button(
            "📄 Descargar PDF",
            f.read(),
            file_name=f"Plan_{familia}_{franja.replace(' ','_')}.pdf",
            mime="application/pdf"
        )

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("Post estudio")
    st.markdown(TEXTO_POST.replace("\n","<br>"), unsafe_allow_html=True)