import streamlit as st
import base64
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import tempfile

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Asistente Endoscopía - Francisco", layout="wide")

# 2. TEXTOS FIJOS ÍNTEGROS
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

TEXTO_DESPUES_PDF = """
1. OBSERVACIONES INICIALES: Permanecer bajo vigilancia hasta recuperar estado de alerta. Evite actividades de coordinación, conducir o firmar documentos por 12 hs.
2. CUIDADOS EN EL DOMICILIO: Descanso, dieta ligera, evitar alcohol y sedantes. Controlar fiebre o dolor.
3. SIGNOS DE ALARMA: Consulte urgente si hay dolor intenso, fiebre >= 38°C, sangrado o vómitos.
4. CONTACTO: Gastroenterología CEMIC (08-20hs): 11 5596 2440. Guardia: Galván 4102 o Av. Cnel. Díaz 2423.
5. INDICACIONES: Mantenerse acompañado y no realizar actividad física.
6. BIOPSIAS: Resultados en 21 días vía mail o a informespatologia@cemic.edu.ar.
"""

# 3. FUNCIONES DE APOYO
def reiniciar():
    st.session_state.clear()
    st.rerun()

def texto_docx(ruta_relativa):
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_completa = os.path.join(base_dir, ruta_relativa)
        if not os.path.exists(ruta_completa): return f"[Archivo no encontrado: {ruta_relativa}]"
        doc = Document(ruta_completa)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except: return "[Error al leer archivo]"

def mostrar_docx(ruta_relativa):
    texto = texto_docx(ruta_relativa)
    st.markdown(f'<div style="background-color:white; padding:25px; border-radius:15px; border-left:8px solid #2bb673; margin-bottom:20px; font-size:18px; color:#333333 !important; line-height:1.6; box-shadow:0px 4px 12px rgba(0,0,0,0.05);">{texto.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

# 4. GENERADOR DE PDF
def generar_pdf(titulo_prep, contenido_prep):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        doc = SimpleDocTemplate(tmp.name, pagesize=A4)
        estilos = getSampleStyleSheet()
        
        # Estilos personalizados
        estilo_titulo = ParagraphStyle('Titulo', parent=estilos['Heading1'], alignment=TA_CENTER, textColor='#2bb673', spaceAfter=20)
        estilo_sub = ParagraphStyle('Sub', parent=estilos['Heading2'], textColor='#1e7d4f', spaceBefore=15, spaceAfter=10)
        estilo_body = ParagraphStyle('Body', parent=estilos['Normal'], fontSize=10, leading=14, alignment=TA_LEFT, textColor='#333333')

        historia = []
        historia.append(Paragraph(f"Plan de Preparación: {titulo_prep}", estilo_titulo))
        
        # Sección ANTES
        historia.append(Paragraph("I. INSTRUCCIONES PREVIAS (ANTES DEL ESTUDIO)", estilo_sub))
        for linea in TEXTO_ANTES.split('\n'):
            if linea.strip(): historia.append(Paragraph(linea, estilo_body))
        
        historia.append(PageBreak())
        
        # Sección PREPARACIÓN
        historia.append(Paragraph(f"II. CRONOGRAMA DE PREPARACIÓN ({titulo_prep})", estilo_sub))
        for linea in contenido_prep.split('\n'):
            if linea.strip(): historia.append(Paragraph(linea, estilo_body))
        
        historia.append(PageBreak())

        # Sección DESPUÉS
        historia.append(Paragraph("III. RECOMENDACIONES POST-ESTUDIO (DESPUÉS)", estilo_sub))
        for linea in TEXTO_DESPUES_PDF.split('\n'):
            if linea.strip(): historia.append(Paragraph(linea, estilo_body))
            
        doc.build(historia)
        return tmp.name

# 5. ESTILOS CSS
st.markdown("""
<style>
.stApp { background-color: #f4f7f6; }
* { color: #333333 !important; }
h1, h2, h3 { color: #2bb673 !important; }
.stButton button p { color: white !important; }
.stButton button { background-color: #2bb673 !important; border-radius: 12px; font-weight: bold; border:none; }
.card { background-color: white !important; padding: 30px; border-radius: 22px; box-shadow: 0px 8px 24px rgba(0,0,0,0.08); border-top: 10px solid #2bb673; }
</style>
""", unsafe_allow_html=True)

# 6. LAYOUT PRINCIPAL
def get_img64(path):
    if not os.path.exists(path): return None
    with open(path, "rb") as f: return base64.b64encode(f.read()).decode()

img = get_img64("francisco.png")
col1, col2 = st.columns([1.2, 1])

with col1:
    bienvenida = f"""
    <div class="card">
    <h1 style="margin-top:0;">Hola, soy Francisco 👋</h1>
    <h3 style="color:#444444 !important;">Voy a ayudarte paso a paso con tu estudio.</h3>
    <div style="padding:18px; border-radius:15px; margin-bottom:12px; background-color:#2bb673; color:white !important;">
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
    st.markdown(bienvenida, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    opcion = st.radio("¿En qué etapa te encuentras?", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])
    if st.button("🔄 REINICIAR"): reiniciar()

with col2:
    if img: st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{img}" style="width:100%; max-width:400px; border-radius:50%; border: 10px solid white; box-shadow: 0px 10px 30px rgba(0,0,0,0.15);"></div>', unsafe_allow_html=True)

# 7. LÓGICA DE CONTENIDO
if opcion == "ANTES DE MI ENDOSCOPIA":
    st.markdown("## 📋 Antes de mi Endoscopía")
    st.markdown(f'<div style="background-color:white; padding:30px; border-radius:15px; border-left:10px solid #2bb673; color:#333333 !important; font-size:18px; line-height:1.7;">{TEXTO_ANTES.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    st.markdown("### 🍎 Dieta 3 días previos")
    mostrar_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

elif opcion == "MI PREPARACIÓN":
    st.markdown("## 💧 Plan de Preparación")
    c1, c2 = st.columns(2)
    with c1: familia = st.selectbox("Medicación", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
    with c2: franja = st.radio("Horario turno", ["7 A 12", "12 A 16", "16 A 19"])
    
    if st.button("GENERAR MI PREPARACIÓN"):
        if familia == "POLIETINELGLICOL": archivo = f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"
        elif familia == "BAREX KIT": archivo = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        else: archivo = f"textos/{familia} DE {franja}.docx"
        
        st.session_state['archivo_ruta'] = archivo
        st.session_state['nombre_prep'] = f"{familia}_{franja.replace(' ','_')}"
        st.session_state['plan_listo'] = True

    if st.session_state.get('plan_listo'):
        st.success(f"Plan: {familia} ({franja})")
        contenido = texto_docx(st.session_state['archivo_ruta'])
        mostrar_docx(st.session_state['archivo_ruta'])
        
        # BOTÓN DE DESCARGA PDF
        pdf_path = generar_pdf(st.session_state['nombre_prep'], contenido)
        with open(pdf_path, "rb") as f:
            st.download_button(label="📥 DESCARGAR INSTRUCCIONES EN PDF", data=f, file_name=f"{st.session_state['nombre_prep']}.pdf", mime="application/pdf")

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.markdown("## 🏁 Recomendaciones Post-Estudio")
    
    # Punto 1
    st.markdown("""
    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#eafaf1; border-left:6px solid #2bb673; color:#333333 !important;">
        <b style="color:#1e7d4f !important; font-size:1.1rem;">1. OBSERVACIONES INICIALES</b><br>
        • Permanecer bajo vigilancia en la sala de recuperación endoscópica hasta que recupere estado de alerta y estabilidad vital.<br>
        • Evite realizar actividades que requieran coordinación hasta pasadas al menos 12 horas post-procedimiento.<br>
        • Evite conducir, manejar maquinaria o firmar documentos importantes durante las primeras 12 horas post procedimiento.
    </div>
    """, unsafe_allow_html=True)

    # Punto 2
    st.markdown("""
    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#f4f6f7; border-left:6px solid #95a5a6; color:#333333 !important;">
        <b style="font-size:1.1rem;">2. CUIDADOS EN EL DOMICILIO</b><br>
        • Descansar y evitar esfuerzos físicos importantes.<br>
        • Mantener dieta ligera las primeras horas, según indicación del médico.<br>
        • Evitar consumo de alcohol y medicamentos sedantes sin indicación.<br>
        • Seguir indicaciones sobre la reanudación de su medicación habitual.<br>
        • Controlar signos vitales si es posible: fiebre, pulso irregular o dolor intenso.
    </div>
    """, unsafe_allow_html=True)

    # Punto 3
    st.markdown("""
    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#fdedec; border-left:6px solid #e74c3c; color:#333333 !important;">
        <b style="color:#c0392b !important; font-size:1.1rem;">3. SIGNOS DE ALARMA – ACUDIR DE INMEDIATO</b><br>
        Consulte urgentemente al endoscopista o concurra a la guardia del hospital si presenta:<br>
        • Dolor abdominal intenso o repentino.<br>
        • Fiebre mayor o igual a 38°C.<br>
        • Sangrado rectal abundante.<br>
        • Vómitos persistentes.<br>
        • Dificultad respiratoria o hinchazón abdominal marcada.
    </div>
    """, unsafe_allow_html=True)

    # Punto 4
    st.markdown("""
    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#eafaf1; border-left:6px solid #2bb673; color:#333333 !important;">
        <b style="color:#1e7d4f !important; font-size:1.1rem;">4. CONTACTO DE URGENCIA</b><br>
        • Contactarse al número de teléfono de Gastroenterología del CEMIC entre las 08:00 hs. y 20:00 hs: <b>11 5596 2440</b>.<br>
        • Fuera de este horario, concurrir directamente a la guardia del CEMIC: Galván 4102 (Saavedra) o Av. Cnel. Díaz 2423 (Palermo).
    </div>
    """, unsafe_allow_html=True)

    # Punto 5
    st.markdown("""
    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#fef9e7; border-left:6px solid #f1c40f; color:#333333 !important;">
        <b style="color:#856404 !important; font-size:1.1rem;">5. INDICACIONES IMPORTANTES PRIMERAS 12 HORAS</b><br>
        • Mantenerse acompañado si es posible.<br>
        • No realizar actividad física, no conducir ni operar maquinaria.<br>
        • Seguir las recomendaciones de dieta e indicaciones del equipo médico.<br>
        • Guardar esta hoja y mostrarla en caso de urgencia.
    </div>
    """, unsafe_allow_html=True)

    # Punto 6
    st.markdown("""
    <div style="padding:20px; border-radius:15px; margin-bottom:15px; background-color:#ffffff; border:2px solid #2bb673; border-left:10px solid #2bb673; color:#333333 !important;">
        <b style="color:#1e7d4f !important; font-size:1.1rem;">6. TOMA DE MUESTRAS - ANATOMÍA PATOLÓGICA</b><br>
        • Si se realizó toma de muestras/biopsias, el resultado será enviado automáticamente a su mail registrado en CEMIC.<br>
        • De no recibirlo en 21 días, pedirlo a: <b>informespatologia@cemic.edu.ar</b>. (Recuerde que ya no se retiran de forma impresa).
    </div>
    """, unsafe_allow_html=True)