import streamlit as st
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import tempfile

st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --- TEXTOS INTEGRADOS (Lectura directa desde el código) ---
TEXTO_ALERTAS_GENERALES = """
• Realice la dieta indicada de forma estricta para asegurar la limpieza del colon.
• No debe suspender su medicación habitual para la presión o el corazón.
• Si toma Aspirina o Anticoagulantes, debe haber consultado previamente con su médico.
• Es obligatorio concurrir con un acompañante adulto que pueda hacerse responsable de su retiro.
• No podrá conducir ningún tipo de vehículo durante las 12 horas posteriores al estudio.
• Traiga todos sus estudios previos relacionados (ecografías, análisis, endoscopías anteriores).
"""

TEXTO_POST_ENDOSCOPIA = """
✅ Reposo: Mantenga reposo relativo en su domicilio. No realice actividad física intensa hoy.
✅ Alimentación: Comience con líquidos claros y luego una dieta blanda (té, galletitas de agua, pollo hervido).
✅ Sedación: Es normal sentir somnolencia o mareos leves. No tome decisiones importantes hoy.
⚠️ Alarma: En caso de dolor abdominal fuerte, fiebre o sangrado importante, concurra a la guardia médica.
✅ Medicación: Puede retomar su medicación habitual salvo que el médico le indique lo contrario.
"""

# --- FUNCIONES DE APOYO ---
def obtener_ruta(nombre_archivo):
    # Busca en la carpeta 'textos' para los instructivos .docx
    ruta_textos = os.path.join(os.getcwd(), "textos", nombre_archivo)
    return ruta_textos if os.path.exists(ruta_textos) else nombre_archivo

def texto_docx(nombre_archivo):
    ruta = obtener_ruta(nombre_archivo)
    if not os.path.exists(ruta): return ""
    try:
        doc = Document(ruta)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except: return ""

def detectar_icono_original(texto):
    t = texto.lower()
    if any(x in t for x in ["no debe", "quitar", "suspenda", "🚫"]): return "🚫", "#ffeaea", "#ff4d4d"
    if any(x in t for x in ["riesgo", "perforación", "⚠️", "importante"]): return "⚠️", "#fff7cc", "#f0ad4e"
    if "hs" in t or "hora" in t: return "⏰", "white", "#4da6ff"
    return "✅", "white", "#4da6ff"

def mostrar_texto_con_iconos(texto):
    for linea in texto.strip().split('\n'):
        if linea.strip():
            ico, fnd, clr = detectar_icono_original(linea)
            st.markdown(f'<div style="background:{fnd}; padding:15px; border-radius:10px; margin-bottom:10px; border-left:8px solid {clr};">{ico} {linea}</div>', unsafe_allow_html=True)

def generar_pdf_clinico(titulo_doc, secciones, alertas):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()
    style_n = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=14)
    style_a = ParagraphStyle('Alert', parent=styles['Normal'], color='red', fontSize=12, leading=14)
    
    story = [Paragraph(f"PLAN DE ESTUDIO: {titulo_doc}", styles["Heading1"]), Spacer(1, 12)]
    
    if alertas:
        story.append(Paragraph("OBSERVACIONES MÉDICAS:", styles["Heading2"]))
        for a in alertas:
            story.append(Paragraph(f"• {a}", style_a))
        story.append(Spacer(1, 15))

    for nombre, contenido in secciones:
        if contenido.strip():
            story.append(Paragraph(nombre, styles["Heading2"]))
            story.append(Paragraph(contenido.replace("\n", "<br/>"), style_n))
            story.append(Spacer(1, 12))
            
    doc.build(story)
    return tmp.name

# --- INTERFAZ PRINCIPAL ---
col_txt, col_img = st.columns([1.5, 1])
with col_img:
    img_path = obtener_ruta("francisco.png")
    if os.path.exists(img_path): st.image(img_path, width=250)
    if st.button("🔄 REINICIAR FORMULARIO", use_container_width=True): st.rerun()

with col_txt:
    st.title("Hola, soy Francisco 👋")
    opcion = st.radio("¿En qué puedo ayudarte hoy?", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])

st.divider()

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.subheader("Indicaciones Generales")
    mostrar_texto_con_iconos(TEXTO_ALERTAS_GENERALES)

elif opcion == "MI PREPARACIÓN":
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento indicado:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Horario de su turno:", ["7 A 12", "12 A 16", "16 A 19"])
    with c2:
        ant = st.multiselect("Sus Antecedentes:", ["Sin antecedentes", "Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca", "Hipertensión Arterial"])
        med = st.multiselect("Su Medicación:", ["Sin medicación", "Aspirina (AAS)", "Clopidogrel / Ticagrelor", "Sintrom / Anticoagulantes", "Insulina", "Metformina"])

    alertas_finales = []
    # Validación de Seguridad Crítica
    if familia == "FOSFATOS" and any(x in ant for x in ["Insuficiencia Renal", "Insuficiencia Cardíaca"]):
        st.error("🚨 CONTRAINDICACIÓN: Los FOSFATOS están contraindicados para usted. Por favor, contacte a su médico para cambiar la preparación.")
    else:
        if "Sintrom / Anticoagulantes" in med: alertas_finales.append("🩸 ATENCIÓN: Sus anticoagulantes requieren manejo previo.")
        if "Insulina" in med: alertas_finales.append("💉 ATENCIÓN: Debe ajustar su dosis de Insulina por el ayuno.")
        for a in alertas_finales: st.warning(a)

        if st.button("GENERAR MI PLAN Y DESCARGAR PDF", use_container_width=True):
            # Lógica de nombres de archivo
            if familia == "BAREX KIT":
                archivo = "BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "BAREX KIT DE 12 A 19.docx"
            else:
                mapping = {"FOSFATOS": "FOSFATOS", "PICOSULFATO": "PICOSULFATO", "POLIETINELGLICOL": "POLIETINELGLICOL 4 litros"}
                archivo = f"{mapping[familia]} de {franja if familia != 'POLIETINELGLICOL' else franja + 'HS'}.docx"
            
            prep_txt = texto_docx(archivo)
            if prep_txt:
                st.subheader("Su Instructivo Personalizado:")
                mostrar_texto_con_iconos(prep_txt)
                
                # Secciones completas para el PDF
                secciones_pdf = [
                    ("1. INSTRUCCIONES DE PREPARACIÓN", prep_txt),
                    ("2. ALERTAS Y RECOMENDACIONES", TEXTO_ALERTAS_GENERALES),
                    ("3. CUIDADOS POST-ESTUDIO", TEXTO_POST_ENDOSCOPIA)
                ]
                
                pdf = generar_pdf_clinico(f"{familia} - {franja} HS", secciones_pdf, alertas_finales)
                with open(pdf, "rb") as f:
                    st.download_button("📥 DESCARGAR GUÍA COMPLETA (PDF)", f, file_name=f"Guia_Endoscopia_{familia}.pdf", use_container_width=True)
            else:
                st.error(f"No se encontró el archivo '{archivo}' en la carpeta 'textos'.")

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("Cuidados Posteriores")
    mostrar_texto_con_iconos(TEXTO_POST_ENDOSCOPIA)