import streamlit as st
import base64
from docx import Document
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import tempfile

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Asistente Endoscopía", layout="wide", initial_sidebar_state="collapsed")

# --------------------------------------------------
# 2. FUNCIONES DE SISTEMA (BÚSQUEDA ROBUSTA)
# --------------------------------------------------

def reiniciar():
    st.session_state.clear()
    st.rerun()

def obtener_ruta_segura(nombre_archivo):
    """Busca archivos en la raíz o en la carpeta 'textos'."""
    rutas = [
        nombre_archivo,
        os.path.join("textos", nombre_archivo),
        os.path.join(os.path.dirname(__file__), "textos", nombre_archivo) if "__file__" in locals() else None
    ]
    for r in rutas:
        if r and os.path.exists(r):
            return r
    return None

def extraer_texto_docx(nombre_archivo):
    ruta = obtener_ruta_segura(nombre_archivo)
    if not ruta: return ""
    try:
        doc = Document(ruta)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])
    except: return ""

# --------------------------------------------------
# 3. ESTILO CSS RESPONSIVO (ADAPTABILIDAD TOTAL)
# --------------------------------------------------

st.markdown("""
<style>
    /* Fondo y Base */
    .stApp { background: linear-gradient(180deg, #e9f0f7, #dfe8f3); }
    
    /* Tipografía Adaptable */
    html, body, [class*="css"] { 
        font-size: 20px; 
        color: #2c3e50; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Títulos Responsivos */
    h1 { font-size: 3.5rem !important; font-weight: 800; color: #1a5c96; margin-bottom: 0.5rem; }
    
    /* Contenedores */
    .card {
        background: white; padding: 2rem; border-radius: 25px;
        box-shadow: 0px 12px 30px rgba(0,0,0,0.1); margin-bottom: 2rem;
    }

    /* Burbujas de Información (Antes/Después/Prep) */
    .burbuja-comun {
        background: white; padding: 1.5rem; border-radius: 20px;
        margin-bottom: 1.2rem; border-left: 10px solid #4da6ff;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.06);
        line-height: 1.6; font-size: 1.4rem;
    }
    .burbuja-alerta {
        background: #fffafa; padding: 1.5rem; border-radius: 20px;
        margin-bottom: 1.2rem; border-left: 10px solid #ff4d4d;
        box-shadow: 0px 6px 15px rgba(255, 77, 77, 0.1);
        line-height: 1.6; font-size: 1.4rem;
    }

    /* Botones Adaptables */
    .stButton button {
        font-size: 1.3rem !important; font-weight: bold; padding: 1rem;
        border-radius: 15px; background: #4da6ff; color: white;
        border: none; width: 100%; transition: 0.3s;
    }
    .stButton button:hover { background: #1a8cff; transform: scale(1.02); }

    /* Media Queries para Móviles */
    @media (max-width: 768px) {
        html, body, [class*="css"] { font-size: 16px !important; }
        h1 { font-size: 2.2rem !important; text-align: center; }
        .burbuja-comun, .burbuja-alerta { font-size: 1.1rem !important; padding: 1rem !important; }
        .hide-mobile { display: none; }
        .card { padding: 1.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 4. COMPONENTES VISUALES (ANTES / DESPUES)
# --------------------------------------------------

def mostrar_alertas_antes():
    # TEXTOS COMPLETOS (SISTEMA INTEGRAL)
    alertas = [
        ("⚠️", "Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo."),
        ("📄", "Debe traer la orden del estudio vigente y debidamente autorizada si corresponde."),
        ("👥", "Debe concurrir acompañado."),
        ("✅", "PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS 4 ÍTEMS ANTERIORES."),
        ("⏰", "8 hs antes del estudio suspende todo alimento sólido y lácteo. Puede continuar con agua y/o Gatorade (sabor manzana o limón) hasta 4 hs antes del procedimiento."),
        ("🚫", "NO debe concurrir con las uñas pintadas o esmaltadas."),
        ("🚫", "DEBE quitarse los anillos, aros y/o piercings antes del estudio."),
        ("💧", "Esta preparación produce una diarrea intensa, por lo que debe realizarla en su domicilio y no en su ámbito laboral."),
        ("⚠️", "Es importante que sepa que durante el estudio se pueden extraer pólipos y tomar biopsias. La incidencia de perforación por colonoscopía oscila entre 0.15% y 2.14% según terapéutica.")
    ]
    for icono, texto in alertas:
        estilo = "burbuja-alerta" if icono in ["🚫", "⚠️"] else "burbuja-comun"
        st.markdown(f'<div class="{estilo}"><b>{icono}</b> {texto}</div>', unsafe_allow_html=True)

def mostrar_post_endoscopia(archivo):
    ruta = obtener_ruta_segura(archivo)
    if not ruta: return
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
        cont = bloques[titulo].strip()
        if cont:
            color = "#ff4d4d" if "alarma" in titulo.lower() else "#4da6ff"
            st.markdown(f"""
                <div style="background:white; padding:1.5rem; border-radius:20px; margin-bottom:1.2rem; 
                border-left:10px solid {color}; box-shadow:0px 8px 20px rgba(0,0,0,0.05);">
                    <b style="font-size:1.4rem; color:#1a5c96;">{titulo}</b><br>
                    <span style="font-size:1.2rem; color:#34495e;">{cont}</span>
                </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------
# 5. LOGICA DE INTERFAZ Y NAVEGACIÓN
# --------------------------------------------------

col_main, col_img = st.columns([1.2, 1])

with col_main:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Hola, soy Francisco 👋")
    opcion = st.radio("Elegí una opción:", 
                      ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    if st.button("🔄 REINICIAR"): reiniciar()
    st.markdown('</div>', unsafe_allow_html=True)

with col_img:
    img_path = obtener_ruta_segura("francisco.png")
    if img_path:
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <div class="hide-mobile" style="text-align:center;">
                    <img src="data:image/png;base64,{b64}" style="width:100%; max-width:420px; border-radius:30px; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
                </div>
            """, unsafe_allow_html=True)

st.divider()

if opcion == "ANTES DE MI ENDOSCOPIA":
    mostrar_alertas_antes()
    st.header("🥗 Dieta Previa")
    texto_dieta = extraer_texto_docx("Dieta comun 3 días PREVIOS AL ESTUDIO.docx")
    if texto_dieta:
        for p in texto_dieta.split("\n"):
            if p.strip(): st.markdown(f'<div class="burbuja-comun">✅ {p}</div>', unsafe_allow_html=True)

elif opcion == "MI PREPARACIÓN":
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Turno:", ["7 A 12", "12 A 16", "16 A 19"])
    with c2:
        antecedentes = st.multiselect("Antecedentes:", ["Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca"])
    
    if familia == "FOSFATOS" and any(x in antecedentes for x in ["Insuficiencia Renal", "Insuficiencia Cardíaca"]):
        st.markdown('<div class="burbuja-alerta">🚨 <b>ERROR MÉDICO:</b> No puede usar FOSFATOS.</div>', unsafe_allow_html=True)
    elif st.button("GENERAR MI PLAN"):
        if familia == "BAREX KIT":
            archivo = f"BAREX KIT DE {'7 A 12' if franja == '7 A 12' else '12 A 19'}.docx"
        elif familia == "POLIETINELGLICOL":
            archivo = f"POLIETINELGLICOL 4 litros de {franja}HS.docx"
        else:
            archivo = f"{familia} DE {franja}.docx"
        
        texto_p = extraer_texto_docx(archivo)
        if texto_p:
            for line in texto_p.split("\n"):
                if line.strip():
                    icono = "🚫" if any(x in line.lower() for x in ["no", "evite", "suspenda"]) else "✅"
                    st.markdown(f'<div class="burbuja-comun"><b>{icono}</b> {line}</div>', unsafe_allow_html=True)

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("🏠 Cuidados Post-Estudio")
    mostrar_post_endoscopia("despues de mi endoscopia.docx")