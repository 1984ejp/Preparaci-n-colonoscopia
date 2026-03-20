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

# Configuración de página
st.set_page_config(page_title="Asistente Endoscopía", layout="wide", initial_sidebar_state="collapsed")

# --------------------------------------------------
# FUNCIONES DE SISTEMA Y ARCHIVOS
# --------------------------------------------------

def reiniciar():
    st.session_state.clear()
    st.rerun()

def obtener_ruta_recursiva(nombre_archivo):
    """Busca el archivo en la raíz y en la carpeta 'textos' de forma segura."""
    posibles_rutas = [
        nombre_archivo,
        os.path.join("textos", nombre_archivo),
        os.path.join(os.path.dirname(__file__), nombre_archivo) if "__file__" in locals() else nombre_archivo,
        os.path.join(os.path.dirname(__file__), "textos", nombre_archivo) if "__file__" in locals() else os.path.join("textos", nombre_archivo)
    ]
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta
    return None

def extraer_texto_completo(nombre_archivo):
    ruta = obtener_ruta_recursiva(nombre_archivo)
    if not ruta: return ""
    try:
        doc = Document(ruta)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    except: return ""

# --------------------------------------------------
# ESTILOS CSS (DISEÑO ORIGINAL DE ALTO IMPACTO)
# --------------------------------------------------

st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #e9f0f7, #dfe8f3); }
    
    /* Tipografía y Tamaños */
    html, body, [class*="css"] { font-size: 22px !important; color: #2c3e50; }
    h1 { font-size: 52px !important; font-weight: 800; color: #1a5c96; margin-bottom: 10px; }
    h2 { font-size: 32px !important; color: #2980b9; margin-top: 20px; }

    /* Tarjeta Principal */
    .card {
        background: white; padding: 35px; border-radius: 25px;
        box-shadow: 0px 12px 30px rgba(0,0,0,0.1); margin-bottom: 25px;
    }

    /* Burbujas de Información */
    .burbuja-info {
        background: white; padding: 25px; border-radius: 18px;
        margin-bottom: 20px; border-left: 10px solid #4da6ff;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.06);
        line-height: 1.6; font-size: 24px; transition: 0.3s;
    }
    .burbuja-alerta {
        background: #fffafa; padding: 25px; border-radius: 18px;
        margin-bottom: 20px; border-left: 10px solid #ff4d4d;
        box-shadow: 0px 6px 15px rgba(255, 77, 77, 0.1);
        line-height: 1.6; font-size: 24px;
    }

    /* Botones */
    .stButton button {
        font-size: 24px !important; font-weight: bold; padding: 15px 30px;
        border-radius: 15px; background: #4da6ff; color: white;
        border: none; width: 100%; transition: all 0.3s ease;
    }
    .stButton button:hover { background: #1a8cff; transform: translateY(-2px); }

    /* Responsive */
    @media (max-width: 768px) {
        h1 { font-size: 36px !important; }
        .burbuja-info, .burbuja-alerta { font-size: 19px; padding: 18px; }
        .hide-mobile { display: none; }
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# COMPONENTES DE INTERFAZ (ANTES / DESPUES)
# --------------------------------------------------

def mostrar_alertas_antes():
    # Textos completos del original
    alertas = [
        ("⚠️", "Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo."),
        ("📄", "Debe traer la orden del estudio vigente y debidamente autorizada si corresponde."),
        ("👥", "Debe concurrir acompañado."),
        ("✅", "PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS 4 ÍTEMS ANTERIORES."),
        ("⏰", "8 hs antes del estudio suspende todo alimento sólido y lácteo. Puede continuar con agua y/o Gatorade hasta 4 hs antes del procedimiento."),
        ("🚫", "NO debe concurrir con las uñas pintadas o esmaltadas."),
        ("🚫", "DEBE quitarse los anillos, aros y/o piercings antes del estudio."),
        ("💧", "Esta preparación produce una diarrea intensa, por lo que debe realizarla en su domicilio."),
        ("⚠️", "Es importante que sepa que durante el estudio se pueden extraer pólipos y tomar biopsias. Los riesgos incluyen perforación (0.15% a 2.14% en terapéutica).")
    ]
    for ico, texto in alertas:
        clase = "burbuja-alerta" if ico in ["🚫", "⚠️"] else "burbuja-info"
        st.markdown(f'<div class="{clase}"><b>{ico}</b> {texto}</div>', unsafe_allow_html=True)

def mostrar_post_endoscopia_diagramado(nombre_archivo):
    ruta = obtener_ruta_recursiva(nombre_archivo)
    if not ruta:
        st.error("No se encontró el archivo de indicaciones post-estudio.")
        return
    
    doc = Document(ruta)
    parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    
    secciones = [
        "1. Observaciones iniciales", "2. Cuidados en el domicilio",
        "3. Signos de alarma – acudir de inmediato", "4. Contacto de urgencia",
        "5. Indicaciones primeras 12 horas", "6. Toma de muestras – Anatomía Patológica"
    ]
    
    bloques = {s: "" for s in secciones}
    actual = None
    
    for p in parrafos:
        p_low = p.lower()
        if "observaciones iniciales" in p_low: actual = secciones[0]
        elif "cuidados en el domicilio" in p_low: actual = secciones[1]
        elif "signos de alarma" in p_low: actual = secciones[2]
        elif "contacto de urgencia" in p_low: actual = secciones[3]
        elif "12 horas" in p_low: actual = secciones[4]
        elif "anatomía patológica" in p_low: actual = secciones[5]
        elif actual: bloques[actual] += p + " "

    for titulo in secciones:
        contenido = bloques[titulo].strip()
        if contenido:
            color_borde = "#ff4d4d" if "alarma" in titulo.lower() else "#4da6ff"
            st.markdown(f"""
                <div style="background:white; padding:25px; border-radius:20px; margin-bottom:20px; 
                border-left:10px solid {color_borde}; box-shadow:0px 8px 20px rgba(0,0,0,0.06);">
                    <b style="font-size:26px; color:#1a5c96;">{titulo}</b><br>
                    <span style="font-size:22px; color:#34495e;">{contenido}</span>
                </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------
# LOGICA DE IMAGEN FRANCISCO
# --------------------------------------------------

def francisco_img():
    path = obtener_ruta_recursiva("francisco.png")
    if path:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <div class="hide-mobile" style="display:flex; justify-content:center; align-items:center; height:100%;">
                    <img src="data:image/png;base64,{b64}" style="width:100%; max-width:450px; border-radius:30px; box-shadow: 0 15px 35px rgba(0,0,0,0.2);">
                </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------
# CUERPO PRINCIPAL (LAYOUT)
# --------------------------------------------------

col_izq, col_der = st.columns([1.2, 1])

with col_izq:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Hola, soy Francisco 👋")
    st.write("Gestionaremos tu estudio de forma segura y profesional.")
    
    opcion = st.radio(
        "¿Qué información necesitas consultar?",
        ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"],
        index=0
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 REINICIAR ASISTENTE"):
        reiniciar()
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    francisco_img()

st.divider()

# --------------------------------------------------
# NAVEGACIÓN DE SECCIONES
# --------------------------------------------------

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.header("📋 Requisitos y Alertas Generales")
    mostrar_alertas_antes()
    
    st.header("🥗 Dieta de los 3 días previos")
    texto_dieta = extraer_texto_completo("Dieta comun 3 días PREVIOS AL ESTUDIO.docx")
    if texto_dieta:
        for p in texto_dieta.split("\n"):
            if p.strip(): st.markdown(f'<div class="burbuja-info">✅ {p}</div>', unsafe_allow_html=True)

elif opcion == "MI PREPARACIÓN":
    st.header("⚙️ Configuración de tu Plan")
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento recetado:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Horario de tu turno:", ["7 A 12", "12 A 16", "16 A 19"])
    with c2:
        antecedentes = st.multiselect("Antecedentes médicos:", ["Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca", "Hipertensión"])
    
    # Validación de seguridad médica
    if familia == "FOSFATOS" and any(x in antecedentes for x in ["Insuficiencia Renal", "Insuficiencia Cardíaca"]):
        st.markdown("""
            <div style="background:#ff4d4d; color:white; padding:30px; border-radius:20px; font-weight:bold; font-size:26px; text-align:center;">
                🚨 ALERTA MÉDICA: No debe utilizar FOSFATOS con sus antecedentes. Por favor, comuníquese con el centro médico.
            </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("GENERAR MI GUÍA PERSONALIZADA"):
            # Lógica de nombre de archivo exacta
            if familia == "BAREX KIT":
                archivo = f"BAREX KIT DE {'7 A 12' if franja == '7 A 12' else '12 A 19'}.docx"
            elif familia == "POLIETINELGLICOL":
                archivo = f"POLIETINELGLICOL 4 litros de {franja}HS.docx"
            else:
                archivo = f"{familia} DE {franja}.docx"
            
            st.subheader(f"Guía de Preparación: {familia}")
            texto_prep = extraer_texto_completo(archivo)
            if texto_prep:
                for line in texto_prep.split("\n"):
                    if line.strip():
                        icono = "🚫" if any(x in line.lower() for x in ["no", "evite", "suspenda"]) else "✅"
                        color = "#ff4d4d" if icono == "🚫" else "#4da6ff"
                        st.markdown(f'<div class="burbuja-info" style="border-left-color:{color}"><b>{icono}</b> {line}</div>', unsafe_allow_html=True)

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("🏠 Cuidados Post-Procedimiento")
    mostrar_post_endoscopia_diagramado("despues de mi endoscopia.docx")