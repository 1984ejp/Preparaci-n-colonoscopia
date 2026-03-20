import streamlit as st
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import tempfile

st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --- FUNCIONES DE APOYO ---
def obtener_ruta(nombre_archivo):
    ruta_raiz = os.path.join(os.getcwd(), nombre_archivo)
    ruta_textos = os.path.join(os.getcwd(), "textos", nombre_archivo)
    if os.path.exists(ruta_raiz): return ruta_raiz
    return ruta_textos

def texto_docx(nombre_archivo):
    ruta = obtener_ruta(nombre_archivo)
    if not os.path.exists(ruta): return ""
    try:
        doc = Document(ruta)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except: return ""

def detectar_estilo_burbuja(texto):
    t = texto.lower()
    if any(x in t for x in ["no debe", "quitar", "suspenda", "🚫", "evite"]): 
        return "#ffeaea", "#ff4d4d" # Rojo/Alerta
    if any(x in t for x in ["riesgo", "perforación", "biopsia", "⚠️", "importante"]): 
        return "#fff7cc", "#f0ad4e" # Amarillo/Atención
    return "white", "#4da6ff" # Azul/Informativo

def mostrar_burbujas_agrupadas(nombre_archivo):
    ruta = obtener_ruta(nombre_archivo)
    if not os.path.exists(ruta):
        st.error(f"Archivo {nombre_archivo} no encontrado.")
        return

    doc = Document(ruta)
    bloques = []
    bloque_actual = []

    # Lógica de agrupación: Detecta cuando una línea empieza con un número (1., 2., 3...)
    for p in doc.paragraphs:
        texto = p.text.strip()
        if not texto: continue
        
        # Si el texto empieza con un número seguido de punto, es un nuevo grupo
        import re
        if re.match(r'^\d+\.', texto) or (bloque_actual == []):
            if bloque_actual:
                bloques.append(bloque_actual)
            bloque_actual = [texto]
        else:
            bloque_actual.append(texto)
    
    if bloque_actual:
        bloques.append(bloque_actual)

    # Renderizado de burbujas
    for grupo in bloques:
        texto_completo = "<br>".join(grupo)
        # Usamos el primer elemento del grupo para definir el color de toda la burbuja
        fnd, clr = detectar_estilo_burbuja(grupo[0])
        st.markdown(f'''
            <div style="background:{fnd}; padding:20px; border-radius:15px; margin-bottom:15px; border-left:10px solid {clr}; line-height:1.6;">
                {texto_completo}
            </div>
        ''', unsafe_allow_html=True)

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

# --- INTERFAZ ---
col_txt, col_img = st.columns([1.5, 1])

with col_img:
    img_path = obtener_ruta("francisco.png")
    if os.path.exists(img_path): st.image(img_path, width=250)
    if st.button("🔄 REINICIAR", use_container_width=True): st.rerun()

with col_txt:
    st.title("Hola, soy Francisco 👋")
    opcion = st.radio("¿Qué necesitas consultar?", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])

st.divider()

if opcion == "ANTES DE MI ENDOSCOPIA":
    mostrar_burbujas_agrupadas("Alertas Generales a todas las preparaciones.docx")

elif opcion == "MI PREPARACIÓN":
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento indicado:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Horario del estudio:", ["7 A 12", "12 A 16", "16 A 19"])
    with c2:
        ant = st.multiselect("Sus Antecedentes:", ["Sin antecedentes", "Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca", "Hipertensión Arterial"])
        med = st.multiselect("Su Medicación:", ["Sin medicación", "Aspirina (AAS)", "Clopidogrel / Ticagrelor", "Sintrom / Anticoagulantes", "Insulina", "Metformina"])

    alertas_f = []
    if familia == "FOSFATOS" and any(x in ant for x in ["Insuficiencia Renal", "Insuficiencia Cardíaca"]):
        st.error("🚨 CONTRAINDICACIÓN: Los FOSFATOS no son seguros para sus antecedentes. CONSULTE A SU MÉDICO.")
    else:
        if "Sintrom / Anticoagulantes" in med: alertas_f.append("🩸 Anticoagulantes: Requiere planificación previa.")
        if "Insulina" in med: alertas_f.append("💉 Insulina: Ajustar dosis por ayuno.")
        for a in alertas_f: st.warning(a)

        if st.button("GENERAR MI PLAN Y PDF", use_container_width=True):
            if familia == "BAREX KIT":
                archivo_p = "BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "BAREX KIT DE 12 A 19.docx"
            else:
                mapping = {"FOSFATOS": "FOSFATOS", "PICOSULFATO": "PICOSULFATO", "POLIETINELGLICOL": "POLIETINELGLICOL 4 litros"}
                archivo_p = f"{mapping[familia]} de {franja if familia != 'POLIETINELGLICOL' else franja + 'HS'}.docx"
            
            prep_txt = texto_docx(archivo_p)
            if prep_txt:
                mostrar_burbujas_agrupadas(archivo_p)
                
                secciones_pdf = [
                    ("INSTRUCCIONES DE PREPARACIÓN", prep_txt),
                    ("ALERTAS ANTES DEL ESTUDIO", texto_docx("Alertas Generales a todas las preparaciones.docx")),
                    ("CUIDADOS DESPUÉS DEL ESTUDIO", texto_docx("despues de mi endoscopia.docx"))
                ]
                pdf = generar_pdf_clinico(f"{familia} - {franja} HS", secciones_pdf, alertas_f)
                with open(pdf, "rb") as f:
                    st.download_button("📥 DESCARGAR GUÍA COMPLETA (PDF)", f, file_name=f"Guia_{familia}.pdf", use_container_width=True)

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    mostrar_burbujas_agrupadas("despues de mi endoscopia.docx")