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

# 4. ESTILOS CSS
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg,#e9f0f7,#dfe8f3); }

/* Ajuste de la tarjeta para que contenga todo sin espacios extra arriba */
.card { 
    background-color: white !important; 
    padding: 28px; 
    border-radius: 22px; 
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08); 
    margin-top: 0px; 
}

/* Colores de texto forzados */
h1, h2, h3, p, span, label {
    color: #1a5c96 !important;
}

.stButton button { 
    background-color: #4da6ff !important; 
    color: white !important; 
    border-radius: 12px; 
    font-size: 20px; 
    width: 100%; 
}

/* Burbujas de información */
.burbuja {
    padding: 18px; 
    border-radius: 15px; 
    margin-bottom: 12px;
    font-size: 16px; 
    line-height: 1.5; 
    display: block;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
}
.burbuja-azul { background-color: #f0f7ff !important; border-left: 6px solid #4da6ff; color: #1a5c96 !important; }
.burbuja-verde { background-color: #eafaf1 !important; border-left: 6px solid #2ecc71; color: #1a5c96 !important; }
.burbuja-amarilla { background-color: #fef9e7 !important; border-left: 6px solid #f1c40f; color: #1a5c96 !important; }
.burbuja-roja { background-color: #fdedec !important; border-left: 6px solid #e74c3c; color: #1a5c96 !important; }
.burbuja-gris { background-color: #f4f6f7 !important; border-left: 6px solid #95a5a6; color: #1a5c96 !important; }
</style>
""", unsafe_allow_html=True)

# 5. IMAGEN FRANCISCO
def get_img64(path):
    if not os.path.exists(path): return None
    with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
img = get_img64("francisco.png")

# 6. LAYOUT PRINCIPAL
col1, col2 = st.columns([1.1, 1])

with col1:
    # TODO EL SALUDO Y BURBUJAS DENTRO DE UN SOLO BLOQUE HTML
    st.markdown(f"""
    <div class="card">
        <h1 style="margin-top:0;">Hola, soy Francisco 👋</h1>
        <h3>Voy a ayudarte paso a paso con tu estudio.</h3>
        
        <div class="burbuja burbuja-verde">
            La Endoscopía representa hoy , la mejor  técnica para el diagnóstico y seguimiento de las enfermedades del Intestino Grueso, la prevención del Cáncer de Colon y para el tratamiento de un variado número de lesiones.
        </div>
        <div class="burbuja burbuja-clara">
            Durante el estudio se pueden extraer pólipos y tomar biopsias.
        </div>
        <div class="burbuja burbuja-alerta">
            Entre los riesgos potenciales, está la perforación microscópica y/o completa del Intestino Grueso. La incidencia en estudios diagnósticos es de aproximadamente 1 por cada 2000 exploraciones.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # El radio button se mantiene como componente de Streamlit para que funcione el click
    st.markdown("<br>", unsafe_allow_html=True)
    opcion = st.radio("¿En qué etapa te encuentras?", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    
    if st.button("🔄 REINICIAR"): reiniciar()    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if img:
        # Ajuste de margen para alinear la imagen con la burbuja blanca de la izquierda
        st.markdown(f'<div style="display:flex;justify-content:center;margin-top:0px;"><img src="data:image/png;base64,{img}" style="width:100%;max-width:400px;border-radius:24px;"></div>', unsafe_allow_html=True)

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
        
        secciones = {"Indicaciones": TEXTO_ANTES, "Tu Plan": texto_docx(archivo)}
        try:
            path_pdf = generar_pdf_profesional(st.session_state['plan_titulo'], secciones)
            with open(path_pdf, "rb") as f:
                st.download_button("📩 DESCARGAR PLAN PDF", f.read(), file_name=f"Plan_{st.session_state['plan_titulo']}.pdf", mime="application/pdf")
        except: 
            st.error("Error al crear PDF.")

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.markdown("## 🏁 Recomendaciones Post-Estudio")
    st.info("Siga estas recomendaciones para su seguridad:")
    
    st.markdown("""
    <div class="burbuja burbuja-azul">
        <b>1. OBSERVACIONES INICIALES</b><br>
        • Permanecer bajo vigilancia en la sala de recuperación.<br>
        • Evite actividades que requieran coordinación por 12 horas.<br>
        • No conducir ni firmar documentos importantes.
    </div>
    <div class="burbuja burbuja-gris">
        <b>2. CUIDADOS EN EL DOMICILIO</b><br>
        • Descansar y evitar esfuerzos físicos.<br>
        • Mantener dieta ligera las primeras horas.<br>
        • Evitar alcohol y sedantes.
    </div>
    <div class="burbuja burbuja-roja">
        <b>3. SIGNOS DE ALARMA</b><br>
        Consulte urgentemente si presenta dolor abdominal intenso, fiebre o sangrado.
    </div>
    <div class="burbuja burbuja-verde">
        <b>4. CONTACTO DE URGENCIA</b><br>
        • Gastroenterología CEMIC: 11 5596 2440.<br>
        • Guardias: Galván 4102 o Av. Cnel. Díaz 2423.
    </div>
    <div class="burbuja burbuja-amarilla">
        <b>5. ANATOMÍA PATOLÓGICA</b><br>
        • Resultado por mail. Si no llega en 21 días: informespatologia@cemic.edu.ar
    </div>
    """, unsafe_allow_html=True)
