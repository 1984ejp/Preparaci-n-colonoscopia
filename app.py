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

# 2. TEXTOS FIJOS (RESTAURADOS ÍNTEGROS - SIN RECORTES)
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
    except Exception as e:
        return f"[Error al leer el archivo Word: {str(e)}]"

def mostrar_docx(ruta_relativa):
    texto = texto_docx(ruta_relativa)
    st.markdown(f"""
<div style="background-color:white; padding:25px; border-radius:15px; border-left:8px solid #2bb673; margin-bottom:20px; font-size:18px; box-shadow:0px 4px 12px rgba(0,0,0,0.05); color: #333333 !important; line-height: 1.6;">
{texto.replace(chr(10), '<br>')}
</div>
""", unsafe_allow_html=True)

# 4. ESTILOS CSS (FUERZA BRUTA PARA VISIBILIDAD TOTAL)
st.markdown("""
<style>
/* Fondo de la aplicación */
.stApp { background-color: #f4f7f6; }

/* Forzar color de texto oscuro en TODO el documento */
* { color: #333333 !important; }

/* Títulos en Verde Esmeralda */
h1, h2, h3, h4, h5, h6 { color: #2bb673 !important; }

/* Botones con texto blanco */
.stButton button p { color: white !important; }
.stButton button { 
    background-color: #2bb673 !important; 
    border-radius: 12px; 
    font-weight: bold;
    border: none;
    padding: 10px 20px;
}

/* Tarjetas de información */
.card { 
    background-color: white !important; 
    padding: 30px; 
    border-radius: 22px; 
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08); 
    border-top: 10px solid #2bb673;
}

/* Color en selectores y radio buttons */
div[data-baseweb="select"] > div { color: #333333 !important; }
div[role="radiogroup"] label p { color: #333333 !important; font-size: 17px; }
</style>
""", unsafe_allow_html=True)

# 5. IMAGEN FRANCISCO
def get_img64(path):
    if not os.path.exists(path): return None
    try:
        with open(path, "rb") as f: 
            return base64.b64encode(f.read()).decode()
    except: return None

img = get_img64("francisco.png")

# 6. LAYOUT PRINCIPAL (PANTALLA DE INICIO RESTAURADA)
col1, col2 = st.columns([1.2, 1])

with col1:
    bienvenida_html = f"""
<div class="card">
<h1 style="margin-top:0; color:#2bb673 !important;">Hola, soy Francisco 👋</h1>
<h3 style="color:#444444 !important; margin-bottom:20px;">Voy a ayudarte paso a paso con tu estudio.</h3>

<div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#2bb673; color:white !important; font-size:18px;">
<span style="color:white !important;">La Endoscopía representa hoy, la mejor técnica para el diagnóstico y seguimiento de las enfermedades del Intestino Grueso, la prevención del Cáncer de Colon y para el tratamiento de un variado número de lesiones.</span>
</div>

<div style="padding:18px; border-radius:15px; margin-bottom:15px; background-color:#eafaf1; border-left:6px solid #2bb673; color:#1e7d4f !important; font-size:17px;">
Durante el estudio se pueden extraer pólipos y tomar biopsias.
</div>

<div style="padding:18px; border-radius:15px; margin-bottom:15px; background-color:#fef9e7; border-left:6px solid #f1c40f; color:#1a5c96 !important; font-size:17px;">
Entre los riesgos potenciales, está la perforación microscópica y/o completa del Intestino Grueso. La incidencia en estudios diagnósticos es de aproximadamente 1 por cada 2000 exploraciones.
</div>
</div>
"""
    st.markdown(bienvenida_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    opcion = st.radio("¿En qué etapa te encuentras?", 
                      ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    
    if st.button("🔄 REINICIAR ASISTENTE"):
        reiniciar()

with col2:
    if img:
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img}" style="width:100%; max-width:420px; border-radius:50%; border: 10px solid white; box-shadow: 0px 10px 30px rgba(0,0,0,0.15);"></div>', unsafe_allow_html=True)

# 7. LÓGICA DE CONTENIDO SEGÚN SELECCIÓN
if opcion == "ANTES DE MI ENDOSCOPIA":
    st.markdown("## 📋 Instrucciones Previas al Estudio")
    st.markdown(f"""
<div style="background-color:white; padding:30px; border-radius:15px; border-left:10px solid #2bb673; color:#333333 !important; font-size:19px; line-height:1.7; box-shadow: 0px 4px 15px rgba(0,0,0,0.06);">
{TEXTO_ANTES.replace(chr(10), "<br>")}
</div>
""", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🍎 Dieta recomendada (3 días previos)")
    mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

elif opcion == "MI PREPARACIÓN":
    st.markdown("## 💧 Mi Plan de Preparación")
    st.info("Por favor, selecciona tu medicación y el horario de tu turno para generar las instrucciones personalizadas.")
    
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("¿Qué medicación te recetaron?", 
                               ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
    with c2:
        franja = st.radio("¿En qué horario es tu estudio?", 
                          ["7 A 12", "12 A 16", "16 A 19"])
    
    if st.button("GENERAR CRONOGRAMA PASO A PASO"):
        # Lógica de archivos completa
        if familia == "POLIETINELGLICOL":
            archivo = f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"
        elif familia == "BAREX KIT":
            archivo = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        else:
            archivo = f"textos/{familia} DE {franja}.docx"
            
        st.session_state['archivo_ruta'] = archivo
        st.session_state['plan_listo'] = True

    if st.session_state.get('plan_listo'):
        st.success(f"Instrucciones para: {familia}")
        mostrar_docx(st.session_state['archivo_ruta'])

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.markdown("## 🏁 Recomendaciones Post-Estudio")
    
    # RECUADRO CON LOS 6 PUNTOS COMPLETOS SIN RECORTES
    post_estudio_html = f"""
<div style="color: #333333 !important;">
    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#eafaf1; border-left:6px solid #2bb673; color:#1e7d4f !important; box-shadow: 0px 4px 10px rgba(0,0,0,0.03);">
        <b style="font-size:1.1rem;">1. OBSERVACIONES INICIALES</b><br>
        • Permanecer bajo vigilancia en la sala de recuperación endoscópica hasta que recupere estado de alerta y estabilidad vital.<br>
        • Evite realizar actividades que requieran coordinación hasta pasadas al menos 12 horas post-procedimiento.<br>
        • Evite conducir, manejar maquinaria o firmar documentos importantes durante las primeras 12 horas post procedimiento.
    </div>

    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#f4f6f7; border-left:6px solid #95a5a6; color:#333333 !important;">
        <b style="font-size:1.1rem;">2. CUIDADOS EN EL DOMICILIO</b><br>
        • Descansar y evitar esfuerzos físicos importantes.<br>
        • Mantener dieta ligera las primeras horas, según indicación del médico.<br>
        • Evitar consumo de alcohol y medicamentos sedantes sin indicación.<br>
        • Seguir indicaciones sobre la reanudación de su medicación habitual.<br>
        • Controlar signos vitales si es posible: fiebre, pulso irregular o dolor intenso.
    </div>

    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#fdedec; border-left:6px solid #e74c3c; color:#c0392b !important;">
        <b style="font-size:1.1rem;">3. SIGNOS DE ALARMA – ACUDIR DE INMEDIATO</b><br>
        Consulte urgentemente al endoscopista o concurra a la guardia del hospital si presenta:<br>
        • Dolor abdominal intenso o repentino.<br>
        • Fiebre mayor o igual a 38°C.<br>
        • Sangrado rectal abundante.<br>
        • Vómitos persistentes.<br>
        • Dificultad respiratoria o hinchazón abdominal marcada.
    </div>

    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#eafaf1; border-left:6px solid #2bb673; color:#1e7d4f !important;">
        <b style="font-size:1.1rem;">4. CONTACTO DE URGENCIA</b><br>
        • Contactarse al número de teléfono de Gastroenterología del CEMIC entre las 08:00 hs. y 20:00 hs: <b>11 5596 2440</b>.<br>
        • Fuera de este horario, concurrir directamente a la guardia del CEMIC: Galván 4102 (Saavedra) o Av. Cnel. Díaz 2423 (Palermo).
    </div>

    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#fef9e7; border-left:6px solid #f1c40f; color:#856404 !important;">
        <b style="font-size:1.1rem;">5. INDICACIONES IMPORTANTES PRIMERAS 12 HORAS</b><br>
        • Mantenerse acompañado si es posible.<br>
        • No realizar actividad física, no conducir ni operar maquinaria.<br>
        • Seguir las recomendaciones de dieta e indicaciones del equipo médico.<br>
        • Guardar esta hoja y mostrarla en caso de urgencia.
    </div>

    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#ffffff; border:2px solid #2bb673; border-left:10px solid #2bb673; color:#1e7d4f !important;">
        <b style="font-size:1.1rem;">6. TOMA DE MUESTRAS - ANATOMÍA PATOLÓGICA</b><br>
        • Si se realizó toma de muestras/biopsias, el resultado será enviado automáticamente a su mail registrado en CEMIC.<br>
        • De no recibirlo en 21 días, pedirlo a: <b>informespatologia@cemic.edu.ar</b>. (Recuerde que ya no se retiran de forma impresa).
    </div>
</div>
"""
    st.markdown(post_estudio_html, unsafe_allow_html=True)