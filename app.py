import streamlit as st
import base64
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import tempfile

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Asistente Endoscopía - Francisco", layout="wide")

# 2. TEXTOS FIJOS
TEXTO_ANTES = """
⚠️ Si toma medicación que altere la coagulación de la sangre debe recordárselo a su médico con anticipación y consultarlo con su médico hematólogo.
📄 Debe traer la orden del estudio vigente y debidamente autorizada si corresponde.
👥 Debe concurrir acompañado.
✅ PODRÁ REALIZAR EL ESTUDIO SI CUMPLE CON LOS 4 ÍTEMS ANTERIORES.
⏰ 8 hs antes del estudio suspende todo alimento sólido y lácteo. Puede continuar con agua y/o Gatorade (sabor manzana o limón) hasta 4 hs antes del procedimiento.
🚫 NO debe concurrir con las uñas pintadas o esmaltadas.
🚫 DEBE quitarse los anillos, aros y/o piercings antes del estudio.
💧 Esta preparación produce una diarrea intensa, por lo que debe realizarla en su domicilio y no en su ámbito laboral.
⚠️ Es importante que sepa que durante el estudio se pueden extraer pólipos y tomar biopsias. Entre los riesgos potenciales del método está la perforación microscópica o completa del intestino grueso. La incidencia de perforación por colonoscopía oscila entre 0.15% y 2.14%. Para una colonoscopía diagnóstica la presencia de complicaciones es aproximadamente 1 cada 2000 exploraciones.
"""

TEXTO_POST = """
Usted acaba de realizar una endoscopia digestiva con sedación/anestesia. Es importante seguir estas recomendaciones para su seguridad y recuperación. 

1. OBSERVACIONES INICIALES 
• Permanecer bajo vigilancia en la sala de recuperación hasta que recupere estado de alerta y estabilidad vital. 
• Evite realizar actividades que requieran coordinación hasta pasadas al menos 12 horas post-procedimiento. 
• Evite conducir, manejar maquinaria o firmar documentos importantes durante las primeras 12 horas.

2. CUIDADOS EN EL DOMICILIO 
• Descansar y evitar esfuerzos físicos importantes. 
• Mantener dieta ligera las primeras horas, según indicación del médico. 
• Evitar consumo de alcohol y medicamentos sedantes sin indicación. 

3. SIGNOS DE ALARMA – ACUDIR DE INMEDIATO 
Consulte urgentemente si presenta: 
• Dolor abdominal intenso o repentino. 
• Fiebre ≥ 38°C. 
• Sangrado abundante, vómitos persistentes o dificultad respiratoria.

4. CONTACTO DE URGENCIA 
• Gastroenterología CEMIC (08:00 a 20:00 hs): 11 5596 2440. 
• Fuera de horario: Guardia CEMIC Saavedra (Galván 4102) o CEMIC Pombo (Av. Cnel. Díaz 2423).

5. TOMA DE MUESTRAS - ANATOMÍA PATOLÓGICA 
• El resultado será enviado automáticamente a su mail registrado. 
• De no recibirlo en 21 días, pídalo a: informespatologia@cemic.edu.ar
"""

# 3. FUNCIONES DE APOYO
def reiniciar():
    st.session_state.clear()
    st.rerun()

def texto_docx(ruta_relativa):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(base_dir, ruta_relativa)
    if not os.path.exists(ruta_completa):
        return f"[Archivo no encontrado: {ruta_relativa}]"
    doc = Document(ruta_completa)
    return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])

def mostrar_docx(ruta_relativa):
    texto = texto_docx(ruta_relativa)
    st.markdown(f"""
    <div style="background-color:white; padding:20px; border-radius:15px; border-left:8px solid #4da6ff; margin-bottom:20px; font-size:20px; box-shadow:0px 4px 12px rgba(0,0,0,0.05); color: #333333 !important;">
    {texto.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

def generar_pdf_profesional(titulo_plan, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('T', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor="#1a5c96")
    estilo_sub = ParagraphStyle('S', parent=styles['Heading2'], fontSize=14, spaceBefore=15, textColor="#4da6ff")
    estilo_txt = ParagraphStyle('X', parent=styles['Normal'], fontSize=11, leading=14)

    elementos = [Paragraph(f"PLAN DE PREPARACIÓN: {titulo_plan}", estilo_titulo)]
    for nombre, contenido in secciones.items():
        elementos.append(Paragraph(nombre.upper(), estilo_sub))
        for linea in contenido.split('\n'):
            if linea.strip(): elementos.append(Paragraph(linea, estilo_txt))
        elementos.append(Spacer(1, 12))
    doc.build(elementos)
    return tmp.name

# 4. ESTILOS CSS (REFINADOS)
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg,#e9f0f7,#dfe8f3); }
.card { 
    background-color: white !important; 
    padding: 28px; 
    border-radius: 22px; 
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08); 
    margin-bottom: 20px;
}
/* Forzamos color oscuro en textos clave */
.card h1, .card h3, .card p, .card span, .card i {
    color: #1a5c96 !important;
}
.stButton button { 
    background-color: #4da6ff !important; 
    color: white !important; 
    border-radius: 12px; 
    font-size: 20px; 
    width: 100%; 
}
/* Asegura que los textos fuera de la card también se vean */
h1, h2, h3, p, span, label {
    color: #1a5c96 !important;
}
</style>
""", unsafe_allow_html=True)

# 5. IMAGEN FRANCISCO
def get_img64(path):
    if not os.path.exists(path): return None
    with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
img = get_img64("francisco.png")

# 6. LAYOUT
col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("# Hola, soy Francisco 👋")
    st.markdown("### Voy a ayudarte paso a paso con tu estudio.")
    st.markdown(f"""
    <div style="background-color:#f0f7ff; padding:15px; border-radius:12px; border-left:5px solid #4da6ff; margin-top:10px;">
        <span style="color:#1a5c96 !important; font-style: italic; font-size:16px;">
        "La Endoscopía representa hoy, la mejor técnica para el diagnóstico y prevención del Cáncer de Colon."
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    opcion = st.radio("¿En qué etapa te encuentras?", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    
    if st.button("🔄 REINICIAR"): reiniciar()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if img:
        st.markdown(f'<div style="display:flex;justify-content:center;margin-top:20px;"><img src="data:image/png;base64,{img}" style="width:100%;max-width:400px;border-radius:24px;"></div>', unsafe_allow_html=True)

# 7. LÓGICA DE CONTENIDO
if opcion == "ANTES DE MI ENDOSCOPIA":
    st.markdown("## 📋 Instrucciones Previas")
    st.markdown(f"""
    <div style="background-color:white; padding:25px; border-radius:15px; border-left:10px solid #4da6ff; color:#333333 !important; font-size:18px; line-height:1.6; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);">
        {TEXTO_ANTES.replace(chr(10), "<br>")}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("## 🍎 Dieta 3 días previos")
    mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

elif opcion == "MI PREPARACIÓN":
    st.markdown("### Configura tu plan")
    familia = st.selectbox("Preparación", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
    franja = st.radio("Horario del estudio", ["7 A 12", "12 A 16", "16 A 19"])

    if st.button("GENERAR PLAN"):
        archivo = ""
        if familia == "BAREX KIT":
            archivo = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        else:
            archivo = f"textos/{familia} DE {franja}.docx" if familia != "POLIETINELGLICOL" else f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"
        
        st.session_state['plan_listo'] = True
        st.session_state['archivo_ruta'] = archivo
        st.session_state['plan_titulo'] = f"{familia} - {franja}"

    if st.session_state.get('plan_listo'):
        archivo = st.session_state['archivo_ruta']
        st.success("Plan generado.")
        mostrar_docx(archivo)
        
        secciones = {"Indicaciones": TEXTO_ANTES, "Tu Plan": texto_docx(archivo), "Post-Estudio": TEXTO_POST}
        try:
            path_pdf = generar_pdf_profesional(st.session_state['plan_titulo'], secciones)
            with open(path_pdf, "rb") as f:
                st.download_button("📩 DESCARGAR PLAN PDF", f.read(), file_name=f"Plan_{st.session_state['plan_titulo']}.pdf", mime="application/pdf")
        except: 
            st.error("Error al crear PDF. Verifica los archivos en la carpeta 'textos'.")

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.markdown("## 🏁 Recomendaciones Post-Estudio")
    st.markdown(f"""
    <div style="background-color:white; padding:25px; border-radius:15px; border-left:10px solid #2ecc71; color:#333333 !important; font-size:18px; line-height:1.6; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);">
        {TEXTO_POST.replace(chr(10), "<br>")}
    </div>
    """, unsafe_allow_html=True)