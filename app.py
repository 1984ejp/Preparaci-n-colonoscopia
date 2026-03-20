import streamlit as st
import base64
from docx import Document
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import tempfile

# Configuración de página
st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --------------------------------------------------
# FUNCIONES TÉCNICAS (CORREGIDAS PARA LA NUBE)
# --------------------------------------------------

def obtener_ruta(ruta_relativa):
    """Asegura que la ruta funcione en Windows y Linux (Streamlit Cloud)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, ruta_relativa)

def texto_docx(ruta):
    ruta_c = obtener_ruta(ruta)
    if not os.path.exists(ruta_c):
        return f"[Archivo no encontrado: {ruta}]"
    doc = Document(ruta_c)
    return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])

def detectar_icono(texto):
    t = texto.lower()
    if any(x in t for x in ["no debe", "quitar", "prohibido"]):
        return "🚫", "#ffeaea", "#ff4d4d"
    if any(x in t for x in ["riesgo", "perforación", "biopsia", "pólipo", "atención", "importante"]):
        return "⚠️", "#fff7cc", "#f0ad4e"
    if "hs" in t or "hora" in t:
        return "⏰", "white", "#4da6ff"
    return "✅", "white", "#4da6ff"

def generar_pdf_completo(titulo_doc, secciones):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()
    style_title = styles["Heading1"]
    style_title.alignment = TA_CENTER
    style_header = styles["Heading2"]
    style_body = styles["Normal"]
    style_body.fontSize = 11
    style_body.leading = 14

    story = []
    story.append(Paragraph(f"GUÍA DE ENDOSCOPÍA: {titulo_doc}", style_title))
    story.append(Spacer(1, 20))

    for nombre_seccion, contenido in secciones:
        if contenido.strip():
            story.append(Paragraph(nombre_seccion, style_header))
            story.append(Spacer(1, 8))
            texto_f = contenido.replace("\n", "<br/>")
            story.append(Paragraph(texto_f, style_body))
            story.append(Spacer(1, 15))
    
    doc.build(story)
    return tmp.name

# --------------------------------------------------
# COMPONENTES DE INTERFAZ
# --------------------------------------------------

def mostrar_docx_visual(ruta):
    ruta_c = obtener_ruta(ruta)
    if not os.path.exists(ruta_c):
        st.error(f"No se pudo cargar el texto: {ruta}")
        return
    
    doc = Document(ruta_c)
    for p in doc.paragraphs:
        texto = p.text.strip()
        if not texto: continue
        icono, fondo, color = detectar_icono(texto)
        st.markdown(f"""
            <div style="background:{fondo}; padding:18px; border-radius:12px; margin-bottom:12px; border-left:8px solid {color}; box-shadow:0px 4px 10px rgba(0,0,0,0.05);">
                <b style="font-size:20px;">{icono}</b> <span style="font-size:18px;">{texto}</span>
            </div>
        """, unsafe_allow_html=True)

def mostrar_post_endoscopia_ordenado(ruta):
    ruta_c = obtener_ruta(ruta)
    if not os.path.exists(ruta_c): return
    doc = Document(ruta_c)
    parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip() != ""]
    
    orden = [
        "1. Observaciones iniciales", "2. Cuidados en el domicilio", 
        "3. Signos de alarma – acudir de inmediato", "4. Contacto de urgencia", 
        "5. Indicaciones primeras 12 horas", "6. Toma de muestras – Anatomía Patológica"
    ]
    bloques = {t: "" for t in orden}
    curr = None
    for p in parrafos:
        pl = p.lower()
        if "observaciones iniciales" in pl: curr = orden[0]
        elif "cuidados en el domicilio" in pl: curr = orden[1]
        elif "signos de alarma" in pl: curr = orden[2]
        elif "contacto de urgencia" in pl: curr = orden[3]
        elif "12 horas" in pl: curr = orden[4]
        elif "anatomía patológica" in pl: curr = orden[5]
        elif curr: bloques[curr] += p + " "

    for t in orden:
        cont = bloques[t].strip()
        if cont:
            borde = "#ff4d4d" if "alarma" in t.lower() else "#4da6ff"
            st.markdown(f"""<div style="background:white; padding:20px; border-radius:12px; margin-bottom:15px; border-left:10px solid {borde}; box-shadow:0px 4px 10px rgba(0,0,0,0.05);"><b style="font-size:22px;">{t}</b><p style="font-size:18px; color:#444;">{cont}</p></div>""", unsafe_allow_html=True)

# --------------------------------------------------
# APP PRINCIPAL
# --------------------------------------------------

col1, col2 = st.columns([1.5, 1])
with col1:
    st.title("Hola, soy Francisco 👋")
    opcion = st.radio("¿Qué necesitas consultar?", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])

with col2:
    img_path = obtener_ruta("francisco.png")
    if os.path.exists(img_path):
        st.image(img_path, width=280)

st.divider()

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.header("Alertas Importantes")
    mostrar_docx_visual("textos/Alertas Generales a todas las preparaciones.docx")
    st.header("Dieta de los 3 días previos")
    mostrar_docx_visual("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

elif opcion == "MI PREPARACIÓN":
    st.subheader("Configura tu Plan Personalizado")
    
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento indicado:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Horario del estudio:", ["7 A 12", "12 A 16", "16 A 19"])
    
    with c2:
        st.write("**Antecedentes y Medicación**")
        ant = st.multiselect("Marque si posee alguno:", ["Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca", "Hipertensión"])
        med = st.multiselect("Medicamentos que toma:", ["Aspirina", "Clopidogrel", "Sintrom / Anticoagulantes", "Insulina", "Metformina"])

    if st.button("GENERAR MI GUÍA PERSONALIZADA", use_container_width=True):
        # Selección de archivo de preparación
        if familia == "BAREX KIT":
            ruta_p = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        elif familia == "FOSFATOS":
            ruta_p = f"textos/FOSFATOS DE {franja}.docx"
        elif familia == "PICOSULFATO":
            ruta_p = f"textos/PICOSULFATO DE {franja}.docx"
        else:
            ruta_p = f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"
        
        st.success(f"Guía generada para {familia}")
        mostrar_docx_visual(ruta_p)
        
        # Resumen de alertas para el PDF
        alertas_usuario = f"ANTECEDENTES: {', '.join(ant) if ant else 'Ninguno'}\nMEDICACIÓN: {', '.join(med) if med else 'Ninguna'}"
        
        secciones_pdf = [
            ("DATOS DEL PACIENTE", alertas_usuario),
            ("1. ALERTAS GENERALES", texto_docx("textos/Alertas Generales a todas las preparaciones.docx")),
            ("2. DIETA PREVIA", texto_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")),
            (f"3. PREPARACIÓN ESPECÍFICA: {familia}", texto_docx(ruta_p)),
            ("4. AYUNO", texto_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx")),
            ("5. DESPUÉS DEL ESTUDIO", texto_docx("textos/despues de mi endoscopia.docx"))
        ]
        
        nombre_f = f"{familia}_{franja.replace(' ','_')}.pdf"
        pdf_path = generar_pdf_completo(f"{familia} - {franja}", secciones_pdf)
        
        with open(pdf_path, "rb") as f:
            st.download_button(f"📥 Descargar PDF: {nombre_f}", f, file_name=nombre_f, mime="application/pdf", use_container_width=True)

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    mostrar_post_endoscopia_ordenado("textos/despues de mi endoscopia.docx")