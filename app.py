import streamlit as st
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import tempfile

st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --------------------------------------------------
# FUNCIONES DE APOYO
# --------------------------------------------------

def obtener_ruta(nombre_archivo):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, nombre_archivo)

def texto_docx(ruta_relativa):
    ruta_c = obtener_ruta(ruta_relativa)
    if not os.path.exists(ruta_c): return ""
    try:
        doc = Document(ruta_c)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except: return ""

def generar_pdf_clinico(titulo_doc, secciones, alertas):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    style_alert = ParagraphStyle('Alert', parent=styles['Normal'], color='red', fontWeight='bold', fontSize=12, leading=14)
    
    story = [Paragraph(f"PLAN DE COLONOSCOPIA: {titulo_doc}", styles["Heading1"]), Spacer(1, 12)]
    
    if alertas:
        story.append(Paragraph("⚠️ ALERTAS DE SEGURIDAD MÉDICA:", styles["Heading2"]))
        for a in alertas:
            story.append(Paragraph(f"• {a}", style_alert))
        story.append(Spacer(1, 15))

    for nombre, contenido in secciones:
        if contenido.strip():
            story.append(Paragraph(nombre, styles["Heading2"]))
            story.append(Paragraph(contenido.replace("\n", "<br/>"), styles["Normal"]))
            story.append(Spacer(1, 12))
            
    doc.build(story)
    return tmp.name

def mostrar_tarjeta(texto, tipo="info"):
    iconos = {"info": "✅", "warning": "⚠️", "danger": "🚨"}
    colores = {"info": "#4da6ff", "warning": "#f0ad4e", "danger": "#ff4d4d"}
    fondos = {"info": "white", "warning": "#fff7cc", "danger": "#ffeaea"}
    
    st.markdown(f"""
        <div style="background:{fondos[tipo]}; padding:15px; border-radius:10px; margin-bottom:10px; border-left:8px solid {colores[tipo]}; shadow:0px 2px 5px rgba(0,0,0,0.1);">
            <b style="font-size:18px;">{iconos[tipo]}</b> {texto}
        </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# INTERFAZ PRINCIPAL
# --------------------------------------------------

col1, col2 = st.columns([1.5, 1])
with col1:
    st.title("Hola, soy Francisco 👋")
    opcion = st.radio("Menú Principal:", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])

with col2:
    img = obtener_ruta("francisco.png")
    if os.path.exists(img): st.image(img, width=250)

st.divider()

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.header("Instrucciones Previas")
    ruta_alertas = "Alertas Generales a todas las preparaciones.docx"
    doc = Document(obtener_ruta(ruta_alertas))
    for p in doc.paragraphs:
        if p.text.strip(): mostrar_tarjeta(p.text)
    
    st.subheader("Dieta de los 3 días previos")
    ruta_dieta = "textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx"
    if os.path.exists(obtener_ruta(ruta_dieta)):
        doc_d = Document(obtener_ruta(ruta_dieta))
        for p in doc_d.paragraphs:
            if p.text.strip(): mostrar_tarjeta(p.text)

elif opcion == "MI PREPARACIÓN":
    st.header("Configuración de Seguridad Clínica")
    
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento recetado:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Horario del estudio:", ["7 A 12", "12 A 16", "16 A 19"])
    
    with c2:
        ant = st.multiselect("Antecedentes Médicos:", ["Sin antecedentes", "Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca", "Hipertensión Arterial"])
        med = st.multiselect("Medicación Habitual:", ["Sin medicación", "Aspirina (AAS)", "Clopidogrel / Ticagrelor", "Sintrom / Anticoagulantes", "Insulina", "Metformina"])

    # --- LÓGICA DE MATRIZ CLÍNICA ---
    alertas_finales = []
    
    # Matriz Comorbilidades vs Preparación
    if familia == "FOSFATOS" and ("Insuficiencia Renal" in ant or "Insuficiencia Cardíaca" in ant):
        alertas_finales.append("🚨 CONTRAINDICACIÓN CRÍTICA: Los FOSFATOS están contraindicados en pacientes con Insuficiencia Renal o Cardíaca. Consulte URGENTE a su médico para cambiar a POLIETINELGLICOL (PEG).")
    
    if familia == "PICOSULFATO" and ("Insuficiencia Renal" in ant or "Insuficiencia Cardíaca" in ant):
        alertas_finales.append("⚠️ PRECAUCIÓN: El Picosulfato puede causar deshidratación riesgosa en su condición. Se recomienda preferir POLIETINELGLICOL.")

    # Matriz Medicación
    if "Sintrom / Anticoagulantes" in med:
        alertas_finales.append("🩸 ANTICOAGULANTES: Requiere planificación médica (suspensión 3-5 días antes). No suspenda sin indicación de su hematólogo/cardiólogo.")
    if "Clopidogrel / Ticagrelor" in med:
        alertas_finales.append("⚠️ ANTIAGREGANTES: Si se prevé polipectomía, suele suspenderse 5-7 días antes. Consulte con su médico.")
    if "Insulina" in med:
        alertas_finales.append("💉 INSULINA: Debe ajustar dosis por el ayuno para evitar hipoglucemia. Controle su azúcar frecuentemente.")
    if "Metformina" in med:
        alertas_finales.append("💊 METFORMINA: Generalmente se suspende el día del estudio por el riesgo de deshidratación.")
    if "Aspirina (AAS)" in med:
        alertas_finales.append("✅ ASPIRINA: Habitualmente NO se suspende, pero informe al equipo médico al llegar.")

    # Mostrar alertas en pantalla
    for a in alertas_finales:
        tipo = "danger" if "🚨" in a else "warning" if "⚠️" in a else "info"
        mostrar_tarjeta(a, tipo=tipo)

    if st.button("GENERAR MI PLAN Y PDF", use_container_width=True):
        # Lógica de archivos
        if familia == "BAREX KIT":
            ruta_p = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        elif familia == "FOSFATOS":
            ruta_p = f"textos/FOSFATOS DE {franja}.docx"
        elif familia == "PICOSULFATO":
            ruta_p = f"textos/PICOSULFATO DE {franja}.docx"
        else:
            ruta_p = f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"
        
        st.subheader("Su Instructivo Personalizado:")
        mostrar_docx_visual(ruta_p)
        
        # PDF
        secciones = [
            ("ANTECEDENTES Y MEDICACIÓN", f"Marcados: {', '.join(ant)} / {', '.join(med)}"),
            ("1. PREPARACIÓN ESPECÍFICA", texto_docx(ruta_p)),
            ("2. ALERTAS GENERALES", texto_docx("Alertas Generales a todas las preparaciones.docx")),
            ("3. AYUNO", texto_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx")),
            ("4. CUIDADOS POST-ESTUDIO", texto_docx("despues de mi endoscopia.docx"))
        ]
        
        pdf_path = generar_pdf_clinico(f"{familia} - {franja}", secciones, alertas_finales)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 DESCARGAR GUÍA MÉDICA (PDF)", f, file_name=f"Plan_{familia}.pdf", use_container_width=True)

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("Cuidados y Signos de Alarma")
    mostrar_docx_visual("despues de mi endoscopia.docx")