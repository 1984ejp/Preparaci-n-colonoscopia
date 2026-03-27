import streamlit as st
import base64
from docx import Document
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import tempfile



st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --------------------------------------------------
# BUSCAR ARCHIVO ROBUSTO
# --------------------------------------------------

def buscar_alertas():

    carpeta="textos"

    if not os.path.exists(carpeta):
        return "textos/Alertas Generales a todas las preparaciones.docx"

    for archivo in os.listdir(carpeta):

        if "alertas" in archivo.lower():

            return os.path.join(carpeta,archivo)

    return "textos/Alertas Generales a todas las preparaciones.docx"

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
# ALERTAS ANTES DE LA ENDOSCOPIA
# --------------------------------------------------

def obtener_alertas():

    return [

        ("⚠️","Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo."),

        ("📄","Debe traer la orden del estudio vigente y debidamente autorizada si corresponde."),

        ("👥","Debe concurrir acompañado."),

        ("✅","PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS 4 ÍTEMS ANTERIORES."),

        ("⏰","8 hs antes del estudio suspende todo alimento sólido y lácteo. Puede continuar con agua y/o Gatorade (sabor manzana o limón) hasta 4 hs antes del procedimiento."),

        ("🚫","NO debe concurrir con las uñas pintadas o esmaltadas."),

        ("🚫","DEBE quitarse los anillos, aros y/o piercings antes del estudio."),

        ("💧","Esta preparación produce una diarrea intensa, por lo que debe realizarla en su domicilio y no en su ámbito laboral."),

        ("⚠️","Es importante que sepa que durante el estudio se pueden extraer pólipos y tomar biopsias. Entre los riesgos potenciales del método está la perforación microscópica o completa del intestino grueso. La incidencia de perforación por colonoscopía es más común después de una terapéutica y oscila entre 0.15% y 2.14% según las series publicadas. Para una colonoscopía diagnóstica la presencia de complicaciones es aproximadamente 1 cada 2000 exploraciones.")

    ]
def mostrar_alertas():

    alertas = obtener_alertas()

    for icono,texto in alertas:

        st.markdown(f"""
        <div style="
        background:white;
        padding:24px;
        border-radius:16px;
        margin-bottom:18px;
        line-height:1.7;
        font-size:24px;
        box-shadow:0px 6px 16px rgba(0,0,0,0.07);
        border-left:8px solid #4da6ff;">
        <b>{icono}</b> {texto}
        </div>
        """,unsafe_allow_html=True)
# --------------------------------------------------
# MOSTRAR DOCX
# --------------------------------------------------

def mostrar_docx(ruta):

    # ruta absoluta para que funcione en Streamlit Cloud
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(base_dir, ruta)

    # si el archivo no existe intentar encontrar el de alertas
    if not os.path.exists(ruta_completa):

        carpeta = os.path.join(base_dir, "textos")

        if os.path.exists(carpeta):

            nombre = os.path.basename(ruta).lower()

            for archivo in os.listdir(carpeta):

                if "alertas" in archivo.lower():
                    ruta_completa = os.path.join(carpeta, archivo)
                    break

    # si aún no existe mostrar error
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
# GENERAR PDF PROFESIONAL
# --------------------------------------------------

def generar_pdf_profesional(titulo_plan, secciones):
    # Crear un archivo temporal que no se borre inmediatamente
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    # Estilos personalizados
    estilo_titulo = ParagraphStyle('Titulo', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor="#1a5c96")
    estilo_subtitulo = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=14, spaceBefore=15, spaceAfter=10, textColor="#4da6ff")
    estilo_texto = ParagraphStyle('Texto', parent=styles['Normal'], fontSize=11, leading=14, alignment=TA_LEFT, spaceAfter=8)

    elementos = []
    elementos.append(Paragraph(f"PLAN DE PREPARACIÓN: {titulo_plan}", estilo_titulo))
    
    for nombre_seccion, contenido in secciones.items():
        if contenido and contenido.strip():
            elementos.append(Paragraph(nombre_seccion.upper(), estilo_subtitulo))
            # Dividir el texto por líneas para mantener el formato
            lineas = contenido.split('\n')
            for linea in lineas:
                if linea.strip():
                    elementos.append(Paragraph(linea, estilo_texto))
            elementos.append(Spacer(1, 12))

    doc.build(elementos)
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
# LAYOUT PRINCIPAL
# --------------------------------------------------

col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Hola, soy Francisco 👋")
    st.markdown("### Voy a ayudarte paso a paso con tu estudio.")
    
    # Bloque Institucional
    st.markdown("""
    <div style="background:#f0f7ff; padding:20px; border-radius:15px; border-left:5px solid #4da6ff; margin: 20px 0; font-size:18px; color:#1a5c96; line-height:1.6;">
    <i>"La Endoscopía representa hoy, la mejor técnica que dispone el médico para el diagnóstico 
    y seguimiento de las enfermedades del Intestino Grueso, para la prevención del Cáncer de Colon 
    y para el tratamiento de un variado número de lesiones."</i>
    </div>
    """, unsafe_allow_html=True)

    st.write("---") 

    opcion = st.radio(
        "¿En qué etapa te encuentras?",
        [
            "Seleccionar...",
            "ANTES DE MI ENDOSCOPIA",
            "MI PREPARACIÓN",
            "DESPUÉS DE MI ENDOSCOPIA"
        ]
    )

    if opcion == "Seleccionar...":
        st.info("💡 Por favor, selecciona una opción para comenzar con las instrucciones.")

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
        @media (max-width:768px){ .hide-mobile{display:none;} }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="hide-mobile" style="display:flex;justify-content:center;">
        <img src="data:image/png;base64,{img}" style="width:100%;max-width:100%;border-radius:24px;">
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# LÓGICA DE CONTENIDO SEGÚN LA OPCIÓN
# --------------------------------------------------

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.markdown("## 📋 Instrucciones Previas")
    st.markdown(f"""
    <div style="background:white; padding:30px; border-radius:20px; line-height:1.8; font-size:22px; border-left:10px solid #4da6ff; box-shadow:0px 10px 20px rgba(0,0,0,0.05);">
        {TEXTO_ANTES.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("🍎 Dieta 3 días previos")
    mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

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

    if st.button("GENERAR PLAN"):
        # Lógica de selección de archivo
        archivo = ""
        if familia == "BAREX KIT":
            archivo = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        elif familia == "FOSFATOS":
            archivo = f"textos/FOSFATOS DE {franja}.docx"
        elif familia == "PICOSULFATO":
            archivo = f"textos/PICOSULFATO DE {franja}.docx"
        elif familia == "POLIETINELGLICOL":
            archivo = f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"

        st.success("Plan generado. Puede leerlo aquí o descargarlo en PDF.")
        
        st.header("Tu Preparación Específica")
        mostrar_docx(archivo)

        # Generar PDF con los textos fijos + el archivo específico
        secciones_para_pdf = {
            "Indicaciones Previas": TEXTO_ANTES,
            "Tu Preparación Detallada": texto_docx(archivo),
            "Cuidados Post-Estudio": TEXTO_POST
        }

        try:
            ruta_pdf = generar_pdf_profesional(f"{familia} - {franja}HS", secciones_para_pdf)
            with open(ruta_pdf, "rb") as f:
                st.download_button(
                    label="📩 DESCARGAR MI PLAN EN PDF",
                    data=f.read(),
                    file_name=f"Plan_Endoscopia_{familia}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Error al generar el PDF: {e}")

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.markdown("## 🏁 Recomendaciones Post-Estudio")
    st.markdown(f"""
    <div style="background:white; padding:30px; border-radius:20px; line-height:1.8; font-size:22px; border-left:10px solid #2ecc71; box-shadow:0px 10px 20px rgba(0,0,0,0.05);">
        {TEXTO_POST.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# ANTES DEL ESTUDIO
# --------------------------------------------------

if opcion=="ANTES DE MI ENDOSCOPIA":

    mostrar_alertas()
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
        # 1. Definir el archivo según la lógica de selección
        archivo = ""
        if familia=="BAREX KIT":
            archivo = "textos/BAREX KIT DE 7 A 12.docx" if franja=="7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        elif familia=="FOSFATOS":
            archivo = f"textos/FOSFATOS DE {franja}.docx"
        elif familia=="PICOSULFATO":
            archivo = f"textos/PICOSULFATO DE {franja}.docx"
        elif familia=="POLIETINELGLICOL":
            archivo = f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"

        # 2. Mostrar visualmente en la app
        st.header("Dieta 3 días previos")
        mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")
        
        st.header("Preparación indicada")
        mostrar_docx(archivo)
        
        st.header("Ayuno")
        mostrar_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx")

        # 3. Preparar datos para el PDF
        secciones_para_pdf = {
            "Alertas Importantes": texto_docx("textos/Alertas Generales a todas las preparaciones.docx"),
            "Dieta Previa": texto_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx"),
            "Instrucciones de Preparación": texto_docx(archivo),
            "Ayuno": texto_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx"),
            "Cuidados Post-Estudio": texto_docx("textos/despues de mi endoscopia.docx")
        }

        # 4. Generar y ofrecer descarga
        try:
            ruta_archivo_pdf = generar_pdf_profesional(f"{familia} - {franja}HS", secciones_para_pdf)
            with open(ruta_archivo_pdf, "rb") as f:
                pdf_data = f.read()
            
            st.download_button(
                label="📩 DESCARGAR MI PLAN EN PDF",
                data=pdf_data,
                file_name=f"Plan_Endoscopia_{familia}_{franja.replace(' ','')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error al generar el PDF: {e}")

# --------------------------------------------------
# DESPUES DEL ESTUDIO
# --------------------------------------------------

# --------------------------------------------------
# DESPUES DEL ESTUDIO
# --------------------------------------------------

elif opcion=="DESPUÉS DE MI ENDOSCOPIA":

    st.header("Indicaciones después del estudio")

    mostrar_post_endoscopia("textos/despues de mi endoscopia.docx")
