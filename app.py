import streamlit as st
import base64
from docx import Document
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile

st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --------------------------------------------------
# REINICIAR
# --------------------------------------------------

def reiniciar():
    st.session_state.clear()
    st.rerun()

# --------------------------------------------------
# ESTILO
# --------------------------------------------------

st.markdown("""
<style>

.stApp{
background:linear-gradient(180deg,#e9f0f7,#dfe8f3);
}

html,body,[class*="css"]{
font-size:22px !important;
}

h1{font-size:52px !important;}

.stButton button{
font-size:22px !important;
padding:14px 26px;
border-radius:14px;
background:#4da6ff;
color:white;
border:none;
}

.card{
background:white;
padding:28px;
border-radius:22px;
box-shadow:0px 8px 24px rgba(0,0,0,0.08);
}

</style>
""",unsafe_allow_html=True)

# --------------------------------------------------
# DETECTAR ICONOS
# --------------------------------------------------

def detectar_icono(texto):

    t=texto.lower()

    if "no debe" in t or "quitar" in t:
        return "🚫","#ffeaea","#ff4d4d"

    if "riesgo" in t or "perforación" in t or "biopsia" in t or "pólipo" in t or "recuerde" in t:
        return "⚠️","#fff7cc","#f0ad4e"

    if "hs" in t:
        return "⏰","white","#4da6ff"

    return "✅","white","#4da6ff"

# --------------------------------------------------
# MOSTRAR DOCX
# --------------------------------------------------

def mostrar_docx(ruta):

    if not os.path.exists(ruta):
        st.error(f"No se encontró el archivo: {ruta}")
        return

    doc=Document(ruta)

    textos=[]
    buffer=""

    for p in doc.paragraphs:

        texto=p.text.strip()

        if texto=="":
            continue

        if texto.lower().startswith("y/o") or texto.lower().startswith("o "):
            buffer+=" "+texto

        else:

            if buffer!="":
                textos.append(buffer)

            buffer=texto

    if buffer!="":
        textos.append(buffer)

    for texto in textos:

        icono,fondo,color=detectar_icono(texto)

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
        """,unsafe_allow_html=True)

# --------------------------------------------------
# EXTRAER TEXTO DOCX
# --------------------------------------------------

def texto_docx(ruta):

    if not os.path.exists(ruta):
        return ""

    doc=Document(ruta)

    texto=[]

    for p in doc.paragraphs:

        t=p.text.strip()

        if t!="":
            texto.append(t)

    return "\n".join(texto)

# --------------------------------------------------
# GENERAR PDF
# --------------------------------------------------

def generar_pdf(texto):

    tmp=tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")

    c=canvas.Canvas(tmp.name,pagesize=A4)

    width,height=A4
    y=height-40

    for linea in texto.split("\n"):

        c.drawString(40,y,linea[:95])
        y-=18

        if y<40:
            c.showPage()
            y=height-40

    c.save()

    return tmp.name

# --------------------------------------------------
# POST ENDOSCOPIA
# --------------------------------------------------

def mostrar_post_endoscopia(ruta):

    doc=Document(ruta)

    parrafos=[p.text.strip() for p in doc.paragraphs if p.text.strip()!=""]

    bloques={}
    titulo=None

    for p in parrafos:

        if "observaciones iniciales" in p.lower():
            titulo="1. Observaciones iniciales"
            bloques[titulo]=""

        elif "cuidados en el domicilio" in p.lower():
            titulo="2. Cuidados en el domicilio"
            bloques[titulo]=""

        elif "signos de alarma" in p.lower():
            titulo="3. Signos de alarma – acudir de inmediato"
            bloques[titulo]=""

        elif "contacto de urgencia" in p.lower():
            titulo="4. Contacto de urgencia"
            bloques[titulo]=""

        elif "12 horas" in p.lower():
            titulo="5. Indicaciones primeras 12 horas"
            bloques[titulo]=""

        elif "anatomía patológica" in p.lower():
            titulo="6. Toma de muestras – Anatomía Patológica"
            bloques[titulo]=""

        else:

            if titulo:
                bloques[titulo]+=p+" "

    for t,c in bloques.items():

        st.markdown(f"""
        <div style="
        background:white;
        padding:26px;
        border-radius:18px;
        margin-bottom:20px;
        font-size:26px;
        line-height:1.8;
        border-left:8px solid #4da6ff;
        box-shadow:0px 6px 16px rgba(0,0,0,0.07);">
        <b>✅ {t}</b><br><br>
        {c}
        </div>
        """,unsafe_allow_html=True)

# --------------------------------------------------
# IMAGEN
# --------------------------------------------------

def get_img64(path):

    if not os.path.exists(path):
        return None

    with open(path,"rb") as f:
        return base64.b64encode(f.read()).decode()

img=get_img64("francisco.png")

# --------------------------------------------------
# LAYOUT
# --------------------------------------------------

col1,col2=st.columns([1.1,1])

with col1:

    st.markdown('<div class="card">',unsafe_allow_html=True)

    st.markdown("# Hola, soy Francisco 👋")
    st.write("Voy a ayudarte paso a paso con tu estudio.")

    opcion=st.radio(
        "Elegí una opción:",
        [
        "Seleccionar...",
        "ANTES DE MI ENDOSCOPIA",
        "MI PREPARACIÓN",
        "DESPUÉS DE MI ENDOSCOPIA"
        ]
    )

    st.markdown("<br>",unsafe_allow_html=True)

    c1,c2,c3=st.columns([1,1,1])

    with c2:
        if st.button("🔄 REINICIAR"):
            reiniciar()

    st.markdown('</div>',unsafe_allow_html=True)

with col2:

    if img:
        st.markdown(f"""
        <div style="display:flex;justify-content:center;">
        <img src="data:image/png;base64,{img}" style="width:100%;max-width:850px;border-radius:24px;">
        </div>
        """,unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------
# ANTES DEL ESTUDIO
# --------------------------------------------------

if opcion=="ANTES DE MI ENDOSCOPIA":

    mostrar_docx("textos/Alertas Generales a todas las preparaciones.docx")

    st.header("Dieta 3 días previos")

    mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

# --------------------------------------------------
# MI PREPARACIÓN
# --------------------------------------------------

elif opcion=="MI PREPARACIÓN":

    st.subheader("Generar mi plan de preparación")

    familia=st.selectbox(
        "Tipo de preparación indicada",
        ["FOSFATOS","PICOSULFATO","POLIETINELGLICOL","BAREX KIT"]
    )

    franja=st.radio(
        "Franja horaria del estudio",
        ["7 A 12","12 A 16","16 A 19"]
    )

    st.markdown("### Antecedentes médicos")

    sin=st.checkbox("Sin antecedentes")

    renal=st.checkbox("Insuficiencia renal",disabled=sin)
    cardiaca=st.checkbox("Insuficiencia cardíaca",disabled=sin)
    diabetes=st.checkbox("Diabetes",disabled=sin)
    hipertension=st.checkbox("Hipertensión arterial",disabled=sin)

    st.markdown("### Medicación actual")

    sin_medicacion=st.checkbox("Sin medicación")

    aspirina=st.checkbox("Aspirina",disabled=sin_medicacion)
    clopidogrel=st.checkbox("Clopidogrel",disabled=sin_medicacion)
    sintrom=st.checkbox("Sintrom",disabled=sin_medicacion)
    insulina=st.checkbox("Insulina",disabled=sin_medicacion)
    metformina=st.checkbox("Metformina",disabled=sin_medicacion)

    if st.button("GENERAR PLAN"):

        st.header("Dieta 3 días previos")

        mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

        if familia=="BAREX KIT":

            if franja=="7 A 12":
                archivo="textos/BAREX KIT DE 7 A 12.docx"
            else:
                archivo="textos/BAREX KIT DE 12 A 19.docx"

        elif familia=="FOSFATOS":
            archivo=f"textos/FOSFATOS DE {franja}.docx"

        elif familia=="PICOSULFATO":
            archivo=f"textos/PICOSULFATO DE {franja}.docx"

        elif familia=="POLIETINELGLICOL":
            archivo=f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"

        st.header("Preparación indicada")

        mostrar_docx(archivo)

        st.header("Ayuno")

        mostrar_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx")

        titulo_protocolo = f"{familia} {franja}"

        texto_pdf=f"""
{titulo_protocolo}

ANTES DEL ESTUDIO
{texto_docx("textos/Alertas Generales a todas las preparaciones.docx")}

DIETA 3 DIAS PREVIOS
{texto_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")}

PREPARACION
{texto_docx(archivo)}

AYUNO
{texto_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx")}

DESPUES DEL ESTUDIO
{texto_docx("textos/despues de mi endoscopia.docx")}
"""

        pdf=generar_pdf(texto_pdf)

        nombre_archivo = f"{familia}_{franja.replace(' ','_')}.pdf"

        with open(pdf,"rb") as f:

            st.download_button(
                "📄 Descargar preparación completa en PDF",
                f,
                file_name=nombre_archivo
            )

# --------------------------------------------------
# DESPUES DEL ESTUDIO
# --------------------------------------------------

elif opcion=="DESPUÉS DE MI ENDOSCOPIA":

    st.header("Indicaciones después del estudio")

    mostrar_post_endoscopia("textos/despues de mi endoscopia.docx")