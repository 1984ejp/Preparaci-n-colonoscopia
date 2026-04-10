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
    # Cambiado color azul por verde #2bb673
    st.markdown(f"""
    <div style="background-color:white; padding:20px; border-radius:15px; border-left:8px solid #2bb673; margin-bottom:20px; font-size:20px; box-shadow:0px 4px 12px rgba(0,0,0,0.05); color: #333333 !important;">
    {texto.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

def generar_pdf_profesional(titulo_plan, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    # Cambiado color azul por verde #2bb673
    estilo_titulo = ParagraphStyle('T', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor="#1e7d4f")
    estilo_sub = ParagraphStyle('S', parent=styles['Heading2'], fontSize=14, spaceBefore=15, textColor="#2bb673")
    estilo_txt = ParagraphStyle('X', parent=styles['Normal'], fontSize=11, leading=14)

    elementos = [Paragraph(f"PLAN DE PREPARACIÓN: {titulo_plan}", estilo_titulo)]
    for nombre, contenido in secciones.items():
        elementos.append(Paragraph(nombre.upper(), estilo_sub))
        for linea in contenido.split('\n'):
            if linea.strip(): elementos.append(Paragraph(linea, estilo_txt))
        elementos.append(Spacer(1, 12))
    doc.build(elementos)
    return tmp.name

# 4. ESTILOS CSS (GAMA VERDE ESMERALDA)
st.markdown("""
<style>
/* Degradado de fondo en verde suave */
.stApp { background: linear-gradient(180deg,#eafaf1,#dfeae3); }

/* Ajuste de la tarjeta blanca para que contenga todo sin espacios extra arriba */
.card { 
    background-color: white !important; 
    padding: 30px; 
    border-radius: 22px; 
    box-shadow: 0px 8px 24px rgba(0,0,0,0.08); 
    margin-top: 0px; 
    border-top: 10px solid #2bb673; /* Barra verde superior */
}

/* Colores de texto forzados */
h1, h2, h3 { color: #2bb673 !important; }
p, span, label { color: #1e7d4f !important; }

.stButton button { 
    background-color: #2bb673 !important; 
    color: white !important; 
    border-radius: 12px; 
    font-size: 20px; 
    width: 100%; 
    border: none;
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
.burbuja-verde-solida { background-color: #2bb673 !important; color: white !important; }
.burbuja-clara { background-color: #eafaf1 !important; border-left: 6px solid #2bb673; color: #1e7d4f !important; }
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

# 6. LAYOUT PRINCIPAL (CORREGIDO: SIN ESPACIOS INICIALES PARA EVITAR CUADROS DE CÓDIGO)
col1, col2 = st.columns([1.1, 1])

with col1:
    # IMPORTANTE: El texto dentro de las comillas debe estar pegado al margen izquierdo
    contenido_bienvenida = f"""
<div class="card">
<h1 style="margin-top:0; padding-top:0;">Hola, soy Francisco 👋</h1>
<h3 style="color: #444 !important; margin-bottom:20px;">Voy a ayudarte paso a paso con tu estudio.</h3>
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
    st.markdown(contenido_bienvenida, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    opcion = st.radio("¿En qué etapa te encuentras?", 
                      ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    
    if st.button("🔄 REINICIAR"):
        reiniciar()

with col2:
    if img:
        st.markdown(f"""
<div style="display:flex; justify-content:center; align-items:flex-start;">
<img src="data:image/png;base64,{img}" style="width:100%; max-width:400px; border-radius:50%; border: 8px solid white; box-shadow: 0px 10px 25px rgba(0,0,0,0.1);">
</div>
""", unsafe_allow_html=True)

# 7. LÓGICA DE CONTENIDO
if opcion == "ANTES DE MI ENDOSCOPIA":
    st.markdown(f"## <span style='color:#2bb673'>📋 Instrucciones Previas</span>", unsafe_allow_html=True)
    # Cambiado color azul por verde #2bb673
    st.markdown(f"""
    <div style="background-color:white; padding:25px; border-radius:15px; border-left:10px solid #2bb673; color:#333333 !important; font-size:18px; line-height:1.6; box-shadow: 0px 4px 12px rgba(0,0,0,0.05);">
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
    st.markdown(f"## <span style='color:#2bb673'>🏁 Recomendaciones Post-Estudio</span>", unsafe_allow_html=True)
    
    # Definimos el contenido en una variable pegada al margen izquierdo para evitar el error de visualización
    contenido_post = f"""
<div style="font-family: sans-serif;">
<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#eafaf1; border-left:6px solid #2bb673; color:#1e7d4f;">
<b>1. OBSERVACIONES INICIALES</b><br>
• Permanecer bajo vigilancia en la sala de recuperación endoscópica hasta que recupere estado de alerta y estabilidad vital.<br>
• Evite realizar actividades que requieran coordinación hasta pasadas al menos 12 horas post-procedimiento.<br>
• Evite conducir, manejar maquinaria o firmar documentos importantes durante las primeras 12 horas post procedimiento.
</div>

<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#f4f6f7; border-left:6px solid #95a5a6; color:#333;">
<b>2. CUIDADOS EN EL DOMICILIO</b><br>
• Descansar y evitar esfuerzos físicos importantes.<br>
• Mantener dieta ligera las primeras horas, según indicación del médico.<br>
• Evitar consumo de alcohol y medicamentos sedantes sin indicación.<br>
• Seguir indicaciones sobre la reanudación de su medicación habitual.<br>
• Controlar signos vitales si es posible: fiebre, pulso irregular o dolor intenso.
</div>

<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#fdedec; border-left:6px solid #e74c3c; color:#c0392b;">
<b>3. SIGNOS DE ALARMA – ACUDIR DE INMEDIATO</b><br>
Consulte urgentemente al endoscopista o concurra a la guardia del hospital si presenta:<br>
• Dolor abdominal intenso o repentino<br>
• Fiebre ≥ 38°C<br>
• Sangrado abundante por boca, nariz o recto<br>
• Vómitos persistentes o con sangre<br>
• Dificultad respiratoria o sensación de desmayo<br>
• Hinchazón abdominal marcada o sensación de abdomen duro
</div>

<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#eafaf1; border-left:6px solid #2bb673; color:#1e7d4f;">
<b>4. CONTACTO DE URGENCIA</b><br>
• Contactarse al número de teléfono de Gastroenterología del CEMIC entre las 08:00 hs. y 20:00 hs: <b>11 5596 2440</b>.<br>
• Fuera de este horario, concurrir directamente a la guardia del CEMIC: Galván 4102 (Saavedra) o Av. Cnel. Díaz 2423 (Pombo).<br>
• Informar al médico de guardia que lo evalúa para que avise inmediatamente al endoscopista participante.
</div>

<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#fef9e7; border-left:6px solid #f1c40f; color:#856404;">
<b>5. INDICACIONES IMPORTANTES PRIMERAS 12 HORAS</b><br>
• Mantenerse acompañado si es posible.<br>
• No realizar actividad física, no conducir ni operar maquinaria.<br>
• Seguir las recomendaciones de dieta y medicación indicadas por el equipo médico.<br>
• Guardar esta hoja y mostrarla en caso de urgencia.
</div>

<div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#ffffff; border:1px solid #2bb673; border-left:6px solid #2bb673; color:#1e7d4f;">
<b>6. TOMA DE MUESTRAS - ANATOMÍA PATOLÓGICA</b><br>
• Si se realizó toma de muestras/biopsias, el resultado será enviado automáticamente a su mail registrado en CEMIC.<br>
• De no recibirlo en 21 días, pedirlo a: <b>informespatologia@cemic.edu.ar</b>. (No se retiran más de forma impresa).
</div>
</div>
"""
    st.markdown(contenido_post, unsafe_allow_html=True)