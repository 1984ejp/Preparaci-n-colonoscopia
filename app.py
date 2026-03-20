import streamlit as st
import base64
from docx import Document
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
import tempfile

# Configuración de página
st.set_page_config(page_title="Asistente Endoscopía", layout="wide")

# --------------------------------------------------
# FUNCIONES DE EXTRACCIÓN Y LÓGICA
# --------------------------------------------------

def texto_docx(ruta):
    """Extrae texto plano de un .docx de forma segura."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(base_dir, ruta)
    if not os.path.exists(ruta_completa):
        return ""
    doc = Document(ruta_completa)
    return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip() != ""])

def detectar_icono(texto):
    """Asigna iconos y colores según palabras clave."""
    t = texto.lower()
    if any(x in t for x in ["no debe", "quitar", "prohibido"]):
        return "🚫", "#ffeaea", "#ff4d4d" # Rojo
    if any(x in t for x in ["riesgo", "perforación", "biopsia", "pólipo", "atención"]):
        return "⚠️", "#fff7cc", "#f0ad4e" # Naranja
    if "hs" in t or "hora" in t:
        return "⏰", "white", "#4da6ff" # Azul reloj
    return "✅", "white", "#4da6ff" # Azul estándar

# --------------------------------------------------
# GENERADOR DE PDF (PLATYPUS)
# --------------------------------------------------

def generar_pdf_completo(titulo_doc, secciones):
    """Genera un PDF profesional con saltos de línea automáticos."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    style_title = styles["Heading1"]
    style_title.alignment = TA_CENTER
    style_header = styles["Heading2"]
    style_body = styles["Normal"]
    style_body.fontSize = 11
    style_body.leading = 14

    story = []
    # Título Principal
    story.append(Paragraph(f"GUÍA DE ENDOSCOPÍA: {titulo_doc}", style_title))
    story.append(Spacer(1, 20))

    for nombre_seccion, contenido in secciones:
        if contenido.strip():
            story.append(Paragraph(nombre_seccion, style_header))
            story.append(Spacer(1, 8))
            # Convertir saltos de línea para el PDF
            texto_formateado = contenido.replace("\n", "<br/>")
            story.append(Paragraph(texto_formateado, style_body))
            story.append(Spacer(1, 15))
    
    doc.build(story)
    return tmp.name

# --------------------------------------------------
# COMPONENTES VISUALES
# --------------------------------------------------

def mostrar_docx_visual(ruta):
    """Muestra el contenido del docx en tarjetas visuales en Streamlit."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(base_dir, ruta)
    if not os.path.exists(ruta_completa):
        st.error(f"Archivo no encontrado: {ruta}")
        return
    
    doc = Document(ruta_completa)
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
    """Fuerza el orden 1, 2, 3... del documento post-estudio."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_completa = os.path.join(base_dir, ruta)
    if not os.path.exists(ruta_completa): return

    doc = Document(ruta_completa)
    parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip() != ""]
    
    orden_maestro = [
        "1. Observaciones iniciales",
        "2. Cuidados en el domicilio",
        "3. Signos de alarma – acudir de inmediato",
        "4. Contacto de urgencia",
        "5. Indicaciones primeras 12 horas",
        "6. Toma de muestras – Anatomía Patológica"
    ]
    
    bloques = {t: "" for t in orden_maestro}
    seccion_actual = None

    for p in parrafos:
        pl = p.lower()
        if "observaciones iniciales" in pl: seccion_actual = orden_maestro[0]
        elif "cuidados en el domicilio" in pl: seccion_actual = orden_maestro[1]
        elif "signos de alarma" in pl: seccion_actual = orden_maestro[2]
        elif "contacto de urgencia" in pl: seccion_actual = orden_maestro[3]
        elif "12 horas" in pl: seccion_actual = orden_maestro[4]
        elif "anatomía patológica" in pl: seccion_actual = orden_maestro[5]
        elif seccion_actual:
            bloques[seccion_actual] += p + " "

    for titulo in orden_maestro:
        contenido = bloques[titulo].strip()
        if contenido:
            # Resaltar en rojo si es la sección de alarmas
            borde = "#ff4d4d" if "alarma" in titulo.lower() else "#4da6ff"
            st.markdown(f"""
                <div style="background:white; padding:20px; border-radius:12px; margin-bottom:15px; border-left:10px solid {borde}; box-shadow:0px 4px 10px rgba(0,0,0,0.05);">
                    <b style="font-size:22px; color:#333;">{titulo}</b><br>
                    <p style="font-size:19px; color:#555; margin-top:10px;">{contenido}</p>
                </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------
# INTERFAZ DE USUARIO (STREAMLIT)
# --------------------------------------------------

st.write("### Asistente Virtual")
col1, col2 = st.columns([1.5, 1])

with col1:
    st.title("Hola, soy Francisco 👋")
    st.info("Te guiaré en tu preparación y cuidados post-estudio.")
    opcion = st.radio("¿Qué necesitas consultar?", 
                     ["Seleccionar...", "ANTES DE MI ENDOSCOPIA", "MI PREPARACIÓN", "DESPUÉS DE MI ENDOSCOPIA"])

with col2:
    if os.path.exists("francisco.png"):
        st.image("francisco.png", width=300)

st.divider()

if opcion == "ANTES DE MI ENDOSCOPIA":
    st.header("Alertas Importantes")
    mostrar_docx_visual("textos/Alertas Generales a todas las preparaciones.docx")
    st.header("Dieta de los 3 días previos")
    mostrar_docx_visual("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")

elif opcion == "MI PREPARACIÓN":
    col_a, col_b = st.columns(2)
    with col_a:
        familia = st.selectbox("Medicamento indicado:", ["FOSFATOS", "PICOSULFATO", "POLIETINELGLICOL", "BAREX KIT"])
    with col_b:
        franja = st.radio("Horario de tu estudio:", ["7 A 12", "12 A 16", "16 A 19"])
    
    if st.button("GENERAR MI GUÍA PERSONALIZADA", use_container_width=True):
        # Selección lógica de archivo de preparación
        if familia == "BAREX KIT":
            ruta_prep = "textos/BAREX KIT DE 7 A 12.docx" if franja == "7 A 12" else "textos/BAREX KIT DE 12 A 19.docx"
        elif familia == "FOSFATOS":
            ruta_prep = f"textos/FOSFATOS DE {franja}.docx"
        elif familia == "PICOSULFATO":
            ruta_prep = f"textos/PICOSULFATO DE {franja}.docx"
        else: # POLIETINELGLICOL
            ruta_prep = f"textos/POLIETINELGLICOL 4 litros de {franja}HS.docx"
        
        st.success(f"Plan generado para {familia} en el horario {franja}")
        
        # Mostrar en pantalla
        mostrar_docx_visual(ruta_prep)
        
        # Crear PDF Completo
        secciones_para_pdf = [
            ("1. ALERTAS GENERALES", texto_docx("textos/Alertas Generales a todas las preparaciones.docx")),
            ("2. DIETA PREVIA (3 DÍAS)", texto_docx("textos/Dieta comun 3 días PREVIOS AL ESTUDIO.docx")),
            (f"3. INSTRUCCIONES: {familia}", texto_docx(ruta_prep)),
            ("4. AYUNO", texto_docx("textos/AYUNO PARA TODAS LA PREPARACIONES.docx")),
            ("5. CUIDADOS POST-ESTUDIO", texto_docx("textos/despues de mi endoscopia.docx"))
        ]
        
        nombre_pdf = f"{familia}_{franja.replace(' ','_')}.pdf"
        ruta_pdf_generado = generar_pdf_completo(f"{familia} ({franja})", secciones_para_pdf)
        
        with open(ruta_pdf_generado, "rb") as f:
            st.download_button(
                label=f"📥 Descargar Guía Completa {nombre_pdf}",
                data=f,
                file_name=nombre_pdf,
                mime="application/pdf",
                use_container_width=True
            )

elif opcion == "DESPUÉS DE MI ENDOSCOPIA":
    st.header("Indicaciones Post-Estudio")
    mostrar_post_endoscopia_ordenado("textos/despues de mi endoscopia.docx")