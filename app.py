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
# REINICIAR
# --------------------------------------------------

def reiniciar():
    st.session_state.clear()
    st.rerun()

# --------------------------------------------------
# ESTILO CSS ORIGINAL (ESTÉTICA QUE TE GUSTA)
# --------------------------------------------------

st.markdown("""
<style>

.stApp{
background:linear-gradient(180deg,#e9f0f7,#dfe8f3);
}

/* escritorio */
html,body,[class*="css"]{
font-size:22px !important;
}

h1{
font-size:52px !important;
}

/* botones */
.stButton button{
font-size:22px !important;
padding:14px 26px;
border-radius:14px;
background:#4da6ff;
color:white;
border:none;
width:100%;
}

/* tarjeta */
.card{
background:white;
padding:28px;
border-radius:22px;
box-shadow:0px 8px 24px rgba(0,0,0,0.08);
}

/* RESPONSIVE PARA CELULAR */

@media (max-width: 768px){

html,body,[class*="css"]{
font-size:18px !important;
}

h1{
font-size:32px !important;
}

.card{
padding:18px;
}

.stButton button{
font-size:18px !important;
padding:12px;
}

}

</style>
""",unsafe_allow_html=True)


# --------------------------------------------------
# DETECTAR ICONOS (PARA PREPARACIÓN)
# --------------------------------------------------

def detectar_icono(texto):
    t=texto.lower()

    if "no debe" in t or "quitar" in t or "evite" in t:
        return "🚫","#ffeaea","#ff4d4d"

    if "riesgo" in t or "perforación" in t or "biopsia" in t or "pólipo" in t or "recuerde" in t:
        return "⚠️","#fff7cc","#f0ad4e"

    if "hs" in t:
        return "⏰","white","#4da6ff"

    return "✅","white","#4da6ff"


# --------------------------------------------------
# MOSTRAR DOCX (PARA PREPARACIÓN)
# --------------------------------------------------

def mostrar_docx(ruta):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(base_dir, ruta)

    if not os.path.exists(ruta_completa):
        st.error(f"No se encontró el archivo: {ruta}")
        return

    doc = Document(ruta_completa)
    textos = []
    buffer = ""

    for p in doc.paragraphs:
        texto = p.text.strip()
        if texto == "":
            continue

        if texto.lower().startswith("y/o") or texto.lower().startswith("o "):
            buffer += " " + texto
        else:
            if buffer != "":
                textos.append(buffer)
            buffer = texto

    if buffer != "":
        textos.append(buffer)

    for texto in textos:
        icono, fondo, color = detectar_icono(texto)

        st.markdown(f"""
        <div style="
        background:{fondo};
        padding:24px;
        border-radius:16px;
        margin-bottom:18px;
        line-height:1.7;
        font-size:24px;
        box-shadow:0px 6px 16px rgba(0,0,0,0.07);
        border-left:8px solid {color};">
        <b>{icono}</b> {texto}
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# EXTRAER TEXTO DOCX (PARA PDF)
# --------------------------------------------------

def texto_docx(ruta):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(base_dir, ruta)
    
    if not os.path.exists(ruta_completa):
        return ""

    doc = Document(ruta_completa)
    texto = []

    for p in doc.paragraphs:
        t = p.text.strip()
        if t != "":
            texto.append(t)

    return "\n".join(texto)


# --------------------------------------------------
# NUEVA FUNCIÓN: GENERAR PDF ROBUSTO (SIN CORTAR LÍNEAS)
# --------------------------------------------------

def generar_pdf_completo(titulo, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    style_title = styles["Heading1"]
    style_title.alignment = TA_CENTER
    style_header = styles["Heading2"]
    style_body = styles["Normal"]
    style_body.fontSize = 11
    style_body.leading = 14

    story = []
    story.append(Paragraph(f"PLAN DE ENDOSCOPÍA: {titulo}", style_title))
    story.append(Spacer(1, 20))

    for nombre_seccion, contenido in secciones:
        if contenido.strip():
            story.append(Paragraph(nombre_seccion, style_header))
            story.append(Spacer(1, 10))
            
            # Reemplaza saltos de línea por <br/> para ReportLab
            texto_formateado = contenido.replace("\n", "<br/>")
            story.append(Paragraph(texto_formateado, style_body))
            story.append(Spacer(1, 15))
    
    doc.build(story)
    return tmp.name


# --------------------------------------------------
# POST ENDOSCOPIA DIAGRAMADO
# --------------------------------------------------

def mostrar_post_endoscopia(ruta):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(base_dir, ruta)

    if not os.path.exists(ruta_completa):
        st.error("No se encontró el archivo de post-endoscopía.")
        return

    doc = Document(ruta_completa)
    parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip() != ""]

    bloques = {}
    titulo = None

    for p in parrafos:
        if "observaciones iniciales" in p.lower():
            titulo = "1. Observaciones iniciales"
            bloques[titulo] = ""
        elif "cuidados en el domicilio" in p.lower():
            titulo = "2. Cuidados en el domicilio"
            bloques[titulo] = ""
        elif "signos de alarma" in p.lower():
            titulo = "3. Signos de alarma – acudir de inmediato"
            bloques[titulo] = ""
        elif "contacto de urgencia" in p.lower():
            titulo = "4. Contacto de urgencia"
            bloques[titulo] = ""
        elif "12 horas" in p.lower():
            titulo = "5. Indicaciones primeras 12 horas"
            bloques[titulo] = ""
        elif "anatomía patológica" in p.lower():
            titulo = "6. Toma de muestras – Anatomía Patológica"
            bloques[titulo] = ""
        else:
            if titulo:
                bloques[titulo] += p + " "

    for t, c in bloques.items():
        color_borde = "#ff4d4d" if "alarma" in t.lower() else "#4da6ff"
        st.markdown(f"""
        <div style="
        background:white;
        padding:26px;
        border-radius:18px;
        margin-bottom:20px;
        font-size:26px;
        line-height:1.8;
        border-left:8px solid {color_borde};
        box-shadow:0px 6px 16px rgba(0,0,0,0.07);">
        <b>✅ {t}</b><br><br>
        {c}
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# IMAGEN FRANCISCO
# --------------------------------------------------

def get_img64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_img64("francisco.png")


# --------------------------------------------------
# LAYOUT PRINCIPAL
# --------------------------------------------------

col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Hola, soy Francisco 👋")
    st.write("Voy a ayudarte paso a paso con tu estudio.")

    opcion = st.radio(
        "Elegí una opción:",
        [
            "Seleccionar...",
            "ANTES DE MI ENDOSCOPIA",
            "MI PREPARACIÓN",
            "DESPUÉS DE MI ENDOSCOPIA"
        ]
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("🔄 REINICIAR"):
            reiniciar()

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if img:
        st.markdown("""
        <style>
        @media (max-width:768px){
        .hide-mobile{display:none;}
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="hide-mobile" style="display:flex;justify-content:center;">
        <img src="data:image/png;base64,{img}" style="width:100%;max-width:100%;border-radius:24px;">
        </div>
        """, unsafe_allow_html=True)

st.divider()


# --------------------------------------------------
# SECCIÓN: ANTES DEL ESTUDIO (TEXTO DIRECTO SIN ARCHIVOS)
# --------------------------------------------------

# Se define el texto de Antes exactamente como lo pediste para meterlo también en el PDF
TEXTO_ANTES_COMPLETO_PDF = """Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo.
Debe traer la orden del estudio vigente y debidamente autorizada si corresponde.
Debe concurrir acompañado.

8 hs antes del estudio suspende todo alimento sólido y lácteo, continuar con agua y/o Gatorade (sabor manzana o limón) hasta 4hs antes del procedimiento-.
NO debe concurrir con las uñas pintadas o esmaltadas.
DEBE quitarse los anillos, aros y/o piercings antes del estudio.

TENER EN CUENTA:
- Esta preparación produce una diarrea intensa por lo que debe realizarla en su domicilio y no en su ámbito laboral.
- Es importante que sepa que durante el estudio se pueden extraer pólipos y tomar biopsias. Entre los riesgos potenciales que presenta el método, está la perforación microscópica y/o completa del Intestino Grueso. La incidencia de perforación por Colonoscopía es más común después de una terapéutica; oscila del 0.15 y el 2.14% según las series publicadas. Para una Colonoscopía Diagnóstica, la presencia de complicaciones es de aproximadamente 1 por cada 2000 exploraciones."""


if opcion == "ANTES DE MI ENDOSCOPIA":
    
    requisitos = [
        ("🩸", "Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo."),
        ("📄", "Debe traer la orden del estudio vigente y debidamente autorizada si corresponde."),
        ("👥", "Debe concurrir acompañado."),
        ("✅", "PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS 3 ÍTEMS ANTERIORES.")
    ]

    indicaciones = [
        ("⏰", "8 hs antes del estudio suspende todo alimento sólido y lácteo, continuar con agua y/o Gatorade (sabor manzana o limón) hasta 4hs antes del procedimiento-."),
        ("🚫", "NO debe concurrir con las uñas pintadas o esmaltadas."),
        ("💍", "DEBE quitarse los anillos, aros y/o piercings antes del estudio.")
    ]

    cuidados = [
        ("🏠", "Esta preparación produce una diarrea intensa por lo que debe realizarla en su domicilio y no en su ámbito laboral."),
        ("⚠️", "Es importante que sepa que durante el estudio se pueden extraer pólipos y tomar biopsias. Entre los riesgos potenciales que presenta el método, está la perforación microscópica y/o completa del Intestino Grueso. La incidencia de perforación por Colonoscopía es más común después de una terapéutica; oscila del 0.15 y el 2.14% según las series publicadas. Para una Colonoscopía Diagnóstica, la presencia de complicaciones es de aproximadamente 1 por cada 2000 exploraciones.")
    ]

    st.subheader("📋 Requisitos Fundamentales")
    for ico, txt in requisitos:
        st.markdown(f'<div style="background:white; padding:24px; border-radius:16px; margin-bottom:18px; line-height:1.7; font-size:24px; box-shadow:0px 6px 16px rgba(0,0,0,0.07); border-left:8px solid #4da6ff;"><b>{ico}</b> {txt}</div>', unsafe_allow_html=True)

    st.subheader("⚠️ Indicaciones Críticas")
    for ico, txt in indicaciones:
        st.markdown(f'<div style="background:#fffafa; padding:24px; border-radius:16px; margin-bottom:18px; line-height:1.7; font-size:24px; box-shadow:0px 6px 16px rgba(255, 77, 77, 0.1); border-left:8px solid #ff4d4d;"><b>{ico}</b> {txt}</div>', unsafe_allow_html=True)

    st.subheader("🔍 TENER EN CUENTA:")
    for ico, txt in cuidados:
        st.markdown(f'<div style="background:white; padding:24px; border-radius:16px; margin-bottom:18px; line-height:1.7; font-size:24px; box-shadow:0px 6px 16px rgba(0,0,0,0.07); border-left:8px solid #f0ad4e;"><b>{ico}</b> {txt}</div>', unsafe_allow_html=True)

    st.header("Dieta 3 días previos")
    mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")


# --------------------------------------------------
# SECCIÓN: MI PREPARACIÓN
# --------------------------------------------------

elif opcion == "MI PREPARACIÓN":

    st.subheader("Generar mi plan de preparación")

    familia = st.selectbox(
        "Tipo de preparación indicada",
        ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"]
    )

    franja = st.radio(
        "Franja horaria del estudio",
        ["7 A 12", "12 A 16", "16 A 19"]
    )

    st.markdown("### Antecedentes médicos")
    sin = st.checkbox("Sin antecedentes")
    renal = st.checkbox("Insuficiencia renal", disabled=sin)
    cardiaca = st.checkbox("Insuficiencia cardíaca", disabled=sin)
    diabetes = st.checkbox("Diabetes", disabled=sin)
    hipertension = st.checkbox("Hipertensión arterial", disabled=sin)

    st.markdown("### Medicación actual")
    sin_medicacion = st.checkbox("Sin medicación")
    aspirina = st.checkbox("Aspirina", disabled=sin_medicacion)
    clopidogrel = st.checkbox("Clopidogrel", disabled=sin_medicacion)
    sintrom = st.checkbox("Sintrom", disabled=sin_medicacion)
    insulina = st.checkbox("Insulina", disabled=sin_medicacion)
    metformina = st.checkbox("Metformina", disabled=sin_medicacion)

    if st.button("GENERAR PLAN"):

        # 1. Mostrar Dieta en pantalla
        st.header("Dieta 3 días previos")
        mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

        # 2. Elegir archivo de preparación
        if familia == "BAREX KIT":
            archivo_prep = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        elif familia == "FOSFATOS":
            archivo_prep = f"textos/FOSFATOS DE {franja}.docx"
        elif familia == "PICOSULFATO":
            archivo_prep = f"textos/PICOSULFATO DE {franja}.docx"
        elif familia == "POLIETINELGLICOL":
            archivo_prep = f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"

        st.header("Preparación indicada")
        mostrar_docx(archivo_prep)

        # 3. Mostrar Ayuno en pantalla
        st.header("Ayuno")
        mostrar_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx")

        # 4. Construcción del PDF Completo con los módulos (ReportLab)
        secciones_pdf = [
            ("ANTES DE MI ENDOSCOPIA (Indicaciones comunes)", TEXTO_ANTES_COMPLETO_PDF),
            ("DIETA 3 DÍAS PREVIOS AL ESTUDIO", texto_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")),
            (f"PREPARACIÓN ESPECÍFICA: {familia}", texto_docx(archivo_prep)),
            ("AYUNO OBLIGATORIO", texto_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx")),
            ("DESPUÉS DE MI ENDOSCOPIA", texto_docx("textos/despues de mi endoscopia.docx"))
        ]

        pdf_generado = generar_pdf_completo(f"{familia} ({franja})", secciones_pdf)
        nombre_descarga = f"Plan_Endoscopia_{familia}_{franja.replace(' ', '_')}.pdf"

        with open(pdf_generado, "rb") as f:
            st.download_button(
                label="📄 Descargar Plan Completo en PDF",
                data=f,
                file_name=nombre_descarga,
                mime="application/pdf"
            )


# --------------------------------------------------
# SECCIÓN: DESPUÉS DEL ESTUDIO
# --------------------------------------------------

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":

    st.header("Indicaciones después del estudio")
    mostrar_post_endoscopia("textos/despues de mi endoscopia.docx")