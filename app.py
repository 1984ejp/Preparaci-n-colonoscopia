import streamlit as st
import base64
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_completa = os.path.join(base_dir, ruta_relativa)
        if not os.path.exists(ruta_completa):
            return f"[Archivo no encontrado: {ruta_relativa}]"
        doc = Document(ruta_completa)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except:
        return "[Error al leer el archivo Word]"

def mostrar_docx(ruta_relativa):
    texto = texto_docx(ruta_relativa)
    st.markdown(f"""
<div style="background-color:white; padding:20px; border-radius:15px; border-left:8px solid #2bb673; margin-bottom:20px; font-size:18px; box-shadow:0px 4px 12px rgba(0,0,0,0.05); color: #1a1a1a !important; line-height: 1.6;">
{texto.replace(chr(10), '<br>')}
</div>
""", unsafe_allow_html=True)

# 4. ESTILOS CSS (REVISADOS)
st.markdown("""
<style>
.stApp { background-color: #f4f7f6; }
.stMarkdown p, .stMarkdown span, .stMarkdown li, label, .stWidget label p {
    color: #1a1a1a !important;
}
.card { 
    background-color: white !important; 
    padding: 30px; 
    border-radius: 22px; 
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08); 
    border-top: 10px solid #2bb673;
}
h1, h2, h3 { color: #2bb673 !important; }
.stButton button { 
    background-color: #2bb673 !important; 
    color: white !important; 
    border-radius: 12px; 
    font-size: 18px; 
    width: 100%;
}
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
    bienvenida = f"""
<div class="card">
<h1 style="margin-top:0; color:#2bb673 !important;">Hola, soy Francisco 👋</h1>
<h3 style="color:#444 !important; margin-bottom:20px;">Voy a ayudarte paso a paso con tu estudio.</h3>
<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#2bb673; color:white;">
La Endoscopía representa hoy, la mejor técnica para el diagnóstico y seguimiento de las enfermedades del Intestino Grueso, la prevención del Cáncer de Colon y para el tratamiento de un variado número de lesiones.
</div>
<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#eafaf1; border-left:6px solid #2bb673; color:#1e7d4f;">
Durante el estudio se pueden extraer pólipos y tomar biopsias.
</div>
<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#fef9e7; border-left:6px solid #f1c40f; color:#1a5c96;">
Entre los riesgos potenciales, está la perforación microscópica y/o completa del Intestino Grueso. La incidencia en estudios diagnósticos es de aproximadamente 1 por cada 2000 exploraciones.
</div>
</div>
"""
    st.markdown(bienvenida, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    opcion = st.radio("¿En qué etapa te encuentras?", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    if st.button("🔄 REINICIAR"): reiniciar()

with col2:
    if img:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img}" style="width:100%; max-width:400px; border-radius:50%; border: 8px solid white; box-shadow: 0px 10px 25px rgba(0,0,0,0.1);"></div>', unsafe_allow_html=True)

# 7. LÓGICA DE CONTENIDO
if opcion == "ANTES DE MI ENDOSCOPIA":
    st.markdown("## 📋 Instrucciones Previas")
    st.markdown(f"""
<div style="background-color:white; padding:25px; border-radius:15px; border-left:10px solid #2bb673; color:#1a1a1a !important; font-size:18px; line-height:1.6; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);">
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
        archivo = f"textos/{familia} DE {franja}.docx" if familia != "POLIETINELGLICOL" else f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"
        if familia == "BAREX KIT":
            archivo = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        st.session_state['archivo_ruta'] = archivo
        st.session_state['plan_listo'] = True
    if st.session_state.get('plan_listo'):
        mostrar_docx(st.session_state['archivo_ruta'])

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.markdown("## 🏁 Recomendaciones Post-Estudio")
    post = f"""
<div style="color: #1a1a1a !important;">
<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#eafaf1; border-left:6px solid #2bb673; color:#1e7d4f;">
<b>1. OBSERVACIONES INICIALES</b><br>
• Permanecer bajo vigilancia en la sala de recuperación hasta que recupere estado de alerta y estabilidad vital.<br>
• Evite realizar actividades que requieran coordinación hasta pasadas al menos 12 horas.<br>
• Evite conducir o firmar documentos durante las primeras 12 horas.
</div>
<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#f4f6f7; border-left:6px solid #95a5a6; color:#333;">
<b>2. CUIDADOS EN EL DOMICILIO</b><br>
• Descansar y evitar esfuerzos. Mantener dieta ligera. Evitar alcohol y sedantes.
</div>
<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#fdedec; border-left:6px solid #e74c3c; color:#c0392b;">
<b>3. SIGNOS DE ALARMA</b><br>
Consulte urgente si presenta: Dolor abdominal intenso, Fiebre ≥ 38°C, Sangrado abundante o Vómitos.
</div>
<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#eafaf1; border-left:6px solid #2bb673; color:#1e7d4f;">
<b>4. CONTACTO DE URGENCIA</b><br>
• Gastroenterología CEMIC (08 a 20 hs): 11 5596 2440.<br>
• Fuera de horario: Guardia CEMIC Galván 4102 o Av. Cnel. Díaz 2423.
</div>
<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#fef9e7; border-left:6px solid #f1c40f; color:#856404;">
<b>5. INDICACIONES IMPORTANTES</b><br>
• Mantenerse acompañado. No conducir. Guardar esta hoja.
</div>
<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#ffffff; border:1px solid #2bb673; border-left:6px solid #2bb673; color:#1e7d4f;">
<b>6. TOMA DE MUESTRAS - ANATOMÍA PATOLÓGICA</b><br>
• El resultado será enviado automáticamente a su mail registrado. Si no lo recibe en 21 días, pídalo a informespatologia@cemic.edu.ar.
</div>
</div>
"""
    st.markdown(post, unsafe_allow_html=True)