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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, nombre_archivo)

def texto_docx(ruta_relativa):
    ruta_c = obtener_ruta(ruta_relativa)
    if not os.path.exists(ruta_c): 
        return ""
    try:
        doc = Document(ruta_c)
        return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])
    except: 
        return ""

def detectar_icono_original(texto):
    t = texto.lower()
    if "no debe" in t or "quitar" in t: return "🚫", "#ffeaea", "#ff4d4d"
    if any(x in t for x in ["riesgo", "perforación", "biopsia", "pólipo", "recuerde"]): return "⚠️", "#fff7cc", "#f0ad4e"
    if "hs" in t: return "⏰", "white", "#4da6ff"
    return "✅", "white", "#4da6ff"

def generar_pdf_clinico(titulo_doc, secciones, alertas):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()
    style_alert = ParagraphStyle('Alert', parent=styles['Normal'], color='red', fontSize=12)
    
    story = [Paragraph(f"PLAN: {titulo_doc}", styles["Heading1"]), Spacer(1, 12)]
    
    if alertas:
        story.append(Paragraph("OBSERVACIONES MÉDICAS:", styles["Heading2"]))
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

# --- CABECERA ---
col_txt, col_img = st.columns([1.5, 1])

with col_img:
    img = obtener_ruta("francisco.png")
    if os.path.exists(img): st.image(img, width=250)
    if st.button("🔄 REINICIAR FORMULARIO", use_container_width=True):
        st.rerun()

with col_txt:
    st.title("Hola, soy Francisco 👋")
    opcion = st.radio("¿Qué necesitas consultar?", ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])

st.divider()

# --- SECCIÓN: ANTES DE MI ENDOSCOPIA ---
if opcion == "ANTES DE MI ENDOSCOPIA":
    ruta_alertas = "Alertas Generales a todas las preparaciones.docx"
    if os.path.exists(obtener_ruta(ruta_alertas)):
        doc = Document(obtener_ruta(ruta_alertas))
        for p in doc.paragraphs:
            if p.text.strip():
                ico, fnd, clr = detectar_icono_original(p.text)
                st.markdown(f'<div style="background:{fnd}; padding:15px; border-radius:10px; margin-bottom:10px; border-left:8px solid {clr};">{ico} {p.text}</div>', unsafe_allow_html=True)

# --- SECCIÓN: MI PREPARACIÓN ---
elif opcion == "MI PREPARACIÓN":
    c1, c2 = st.columns(2)
    with c1:
        familia = st.selectbox("Medicamento indicado:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
        franja = st.radio("Horario del estudio:", ["7 A 12", "12 A 16", "16 A 19"])
    with c2:
        ant = st.multiselect("Antecedentes:", ["Sin antecedentes", "Diabetes", "Insuficiencia Renal", "Insuficiencia Cardíaca", "Hipertensión Arterial"])
        med = st.multiselect("Medicación habitual:", ["Sin medicación", "Aspirina (AAS)", "Clopidogrel / Ticagrelor", "Sintrom / Anticoagulantes", "Insulina", "Metformina"])

    contraindicado = False
    alertas_finales = []

    if familia == "FOSFATOS" and any(x in ant for x in ["Insuficiencia Renal", "Insuficiencia Cardíaca"]):
        contraindicado = True
        st.error("🚨 CONTRAINDICACIÓN: Los FOSFATOS están contraindicados en pacientes con Insuficiencia Renal o Cardíaca. CONSULTE A SU MÉDICO.")
    
    if "Sintrom / Anticoagulantes" in med: alertas_finales.append("🩸 ANTICOAGULANTES: Requiere planificación médica previa. Consulte a su médico.")
    if "Insulina" in med: alertas_finales.append("💉 INSULINA: Ajustar dosis por ayuno. Consulte a su médico.")

    for a in alertas_finales:
        st.warning(a)

    if not contraindicado:
        if st.button("GENERAR MI PLAN Y PDF", use_container_width=True):
            if familia == "BAREX KIT":
                ruta_p = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
            elif familia == "FOSFATOS":
                ruta_p = f"textos/FOSFATOS DE {franja}.docx"
            elif familia == "PICOSULFATO":
                ruta_p = f"textos/PICOSULFATO DE {franja}.docx"
            else:
                ruta_p = f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"
            
            if os.path.exists(obtener_ruta(ruta_p)):
                # Mostrar preparación en pantalla
                doc_p = Document(obtener_ruta(ruta_p))
                for p in doc_p.paragraphs:
                    if p.text.strip():
                        ico, fnd, clr = detectar_icono_original(p.text)
                        st.markdown(f'<div style="background:{fnd}; padding:15px; border-radius:10px; margin-bottom:10px; border-left:8px solid {clr};">{ico} {p.text}</div>', unsafe_allow_html=True)
                
                # RECOLECCIÓN DE TEXTOS PARA EL PDF
                identificador = f"{familia}_{franja.replace(' ', '_')}"
                
                # Forzamos la carga de los tres archivos necesarios para el PDF completo
                texto_preparacion = texto_docx(ruta_p)
                texto_alertas = texto_docx("Alertas Generales a todas las preparaciones.docx")
                texto_post = texto_docx("despues de mi endoscopia.docx")
                
                secciones_pdf = [
                    ("INSTRUCCIONES DE PREPARACIÓN", texto_preparacion), 
                    ("ALERTAS GENERALES", texto_alertas),
                    ("CUIDADOS POST-ESTUDIO", texto_post)
                ]
                
                pdf_path = generar_pdf_clinico(identificador, secciones_pdf, alertas_finales)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label=f"📥 DESCARGAR PLAN: {familia} ({franja} HS)", 
                        data=f, 
                        file_name=f"Plan_{identificador}.pdf", 
                        use_container_width=True
                    )
            else:
                st.error("Archivo de preparación no encontrado en la carpeta 'textos'.")
    else:
        st.info("⚠️ La preparación no se puede mostrar debido a la contraindicación detectada. Por favor, hable con su equipo médico.")

# --- SECCIÓN: DESPUÉS DE MI ENDOSCOPIA (VISUALIZACIÓN WEB) ---
elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("Cuidados Post-Estudio")
    ruta_post_web = "despues de mi endoscopia.docx"
    if os.path.exists(obtener_ruta(ruta_post_web)):
        doc_post = Document(obtener_ruta(ruta_post_web))
        for p in doc_post.paragraphs:
            if p.text.strip():
                ico, fnd, clr = detectar_icono_original(p.text)
                st.markdown(f'<div style="background:{fnd}; padding:15px; border-radius:10px; margin-bottom:10px; border-left:8px solid {clr};">{ico} {p.text}</div>', unsafe_allow_html=True)
    else:
        st.warning("El archivo 'despues de mi endoscopia.docx' no se encuentra en el servidor.")