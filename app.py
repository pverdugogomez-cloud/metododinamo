import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from docx import Document
from docx.shared import Inches, RGBColor, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import io
import re

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Diagnóstico Dínamo", page_icon="📊")

# --- BASE DE DATOS ---
db_encuesta = {
    "PILAR COGNITIVO": [
        {"pregunta": "1. Estado de tu energía mental cotidiana", "opciones": ["Me siento mentalmente apagado/a o saturado/a", "Funciono, pero con esfuerzo y dispersión", "Me siento claro/a y funcional la mayor parte del día", "Me siento activo/a mentalmente, creativo/a y con ideas"]},
        {"pregunta": "2. Actividades que encienden tu mente", "opciones": ["Me cuesta y las evito", "Las hago, pero sin mayor disfrute", "Me activan y me ayudan a concentrarme", "Me energizan y sacan lo mejor de mí"]},
        {"pregunta": "3. Capacidad de enfoque", "opciones": ["Muy bajo, me distraigo con facilidad", "Intermitente, depende del día", "Bueno, logro enforcarme cuando lo necesito", "Alto, entro fácilmente en estados de concentración profunda"]},
        {"pregunta": "4. Sensación de crecimiento cognitivo", "opciones": ["Siento que estoy estancado", "Siento poco avance", "Siento que estoy creciendo gradualmente", "Siento que estoy expandiendo activamente mi potencial"]},
        {"pregunta": "5. Desarrollo de pasatiempos", "opciones": ["No tengo pasatiempos o los he dejado de lado", "Tengo intereses, pero los practico muy poco", "Tengo al menos un pasatiempo que practico con cierta regularidad", "Mis pasatiempos son una fuente clara de energía y motivación"]},
        {"pregunta": "6. Impacto de los pasatiempos en tu potencial", "opciones": ["No noto mayor efecto", "Me distraen, pero no me activan demasiado", "Me ayudan a desconectarme y sentirme mejor", "Siento que activan habilidades y aspectos valiosos de mí"]},
        {"pregunta": "7. Consumo de redes sociales", "opciones": ["Siento que me consumen mucha energía y atención", "Las uso bastante y me cuesta regularlas", "Las uso con cierto control", "Las uso de manera consciente y no interfieren con mi foco"]},
        {"pregunta": "8. Efecto de las RRSS en tu mente", "opciones": ["Me dispersan y me saturan", "A veces me afectan, a veces no", "Generalmente no interfieren", "Mantengo claridad y foco independiente de su uso"]}
    ],
    "PILAR FÍSICO": [
        {"pregunta": "9. Nivel de energía física diaria", "opciones": ["Baja, me siento cansado/a gran parte del tiempo", "Variable, con subidas y bajadas", "Adecuada para mis actividades diarias", "Alta, me siento vital y con impulso"]},
        {"pregunta": "10. Relación con tu cuerpo", "opciones": ["Desconectada, lo siento como una carga", "Funcional, pero poco consciente", "Bastante conectada y respetuosa", "Muy conectada, lo siento como un aliado"]},
        {"pregunta": "11. Movimiento y actividad corporal", "opciones": ["Está prácticamente ausente", "Aparece de forma esporádica", "Está presente de manera regular", "Es un pilar que potencia mi energía"]},
        {"pregunta": "12. Alimentación equilibrada", "opciones": ["Siento que desordena o afecta negativamente mi energía", "Es irregular y poco consciente", "Es mayormente equilibrada", "Es un hábito que potencia mi bienestar y energía"]},
        {"pregunta": "13. Impacto de la alimentación en tu funcionamiento", "opciones": ["Me genera cansancio, malestar o baja energía", "A veces afecta, a veces me sostiene", "Generalmente me sostiene bien", "Claramente mejora mi energía, concentración y ánimo"]},
        {"pregunta": "14. Higiene de sueño (Calidad)", "opciones": ["Poco reparador, despierto cansado/a", "Irregular, con noches buenas y malas", "Bastante reparador", "Profundo y reparador"]},
        {"pregunta": "15. Higiene de sueño (Hábitos)", "opciones": ["No tengo rutinas y duermo desordenadamente", "Tengo algunos intentos, pero soy irregular", "Mantengo rutinas relativamente estables", "Tengo hábitos de sueños claros y establecidos"]}
    ],
    "PILAR ESPIRITUAL": [
        {"pregunta": "16. Conexión contigo mismo/a", "opciones": ["Bajo, me siento desconectado/a de mí", "Intermitente", "Presente la mayor parte del tiempo", "Profundo y estable"]},
        {"pregunta": "17. Sentido y coherencia vital", "opciones": ["Siento poca coherencia o sentido", "Siento dudas frecuentes", "Siento bastante coherencia", "Siento que estoy alineado/a con quien soy"]},
        {"pregunta": "18. Práctica de pausas conscientes o meditación", "opciones": ["No realizo ninguna práctica", "Las realizo de forma muy esporádica", "Las realizo con cierta regularidad", "Son un pilar importante para mi bienestar"]},
        {"pregunta": "19. Efecto de estas prácticas en tu vida", "opciones": ["No están presentes, por lo tanto, no influyen", "Me ayudan solo en momentos puntuales", "Me ayudan a regularme emocionalmente", "Me ayudan a mantener coherencia, calma y claridad"]},
        {"pregunta": "20. Relaciones significativas", "opciones": ["Me drenan o me generar conflicto", "Son neutras, cumplen una función", "Me aportan apoyo y contención", "Potencian lo mejor de mí"]},
        {"pregunta": "21. Conexión con algo más grande", "opciones": ["Inexistente", "Esporádica", "Presente", "Profunda y nutritiva"]},
        {"pregunta": "22. Sensación global de activación personal", "opciones": ["Estás sobreviviendo", "Estás funcionando", "Estás en proceso de activación", "Estás desplegando tu potencial"]}
    ]
}

db_plan_accion = {
    "PILAR COGNITIVO": {
        "BAJO": [
            {"accion": "Desconexión Digital: Apagar pantallas 1h antes de dormir.", "frecuencia": "Diario (Noche)"},
            {"accion": "Técnica Pomodoro: 25 min de trabajo enfocado.", "frecuencia": "2 veces al día"},
            {"accion": "Lectura ligera (no trabajo) por 15 minutos.", "frecuencia": "Fines de Semana"}
        ],
        "MEDIO": [
            {"accion": "Bloque de Enfoque Profundo (sin celular).", "frecuencia": "Diario (90 min)"},
            {"accion": "Aprender algo nuevo (podcast, video educativo).", "frecuencia": "3 veces por semana"},
            {"accion": "Limpieza de redes sociales (dejar de seguir cuentas tóxicas).", "frecuencia": "Mensual"}
        ],
        "ALTO": [
            {"accion": "Enseñar o mentorear a alguien en tu área.", "frecuencia": "Semanal"},
            {"accion": "Escribir ideas creativas o journaling.", "frecuencia": "Diario (Mañana)"},
            {"accion": "Desafío intelectual complejo (idioma, ajedrez).", "frecuencia": "Fines de Semana"}
        ]
    },
    "PILAR FÍSICO": {
        "BAJO": [
            {"accion": "Hidratación consciente (1 vaso al despertar).", "frecuencia": "Diario"},
            {"accion": "Caminata suave de 15 minutos.", "frecuencia": "Diario"},
            {"accion": "Establecer hora fija para ir a la cama.", "frecuencia": "Diario"}
        ],
        "MEDIO": [
            {"accion": "Ejercicio de fuerza o resistencia media.", "frecuencia": "3 veces por semana"},
            {"accion": "Preparar comidas saludables (Meal Prep).", "frecuencia": "Semanal (Domingo)"},
            {"accion": "Pausa activa de estiramiento.", "frecuencia": "Cada 2 horas"}
        ],
        "ALTO": [
            {"accion": "Entrenamiento de alta intensidad o deporte.", "frecuencia": "4-5 veces por semana"},
            {"accion": "Optimización del sueño (temperatura, oscuridad total).", "frecuencia": "Diario"},
            {"accion": "Actividad física en la naturaleza (trekking, etc).", "frecuencia": "Mensual"}
        ]
    },
    "PILAR ESPIRITUAL": {
        "BAJO": [
            {"accion": "Respiración consciente (3 minutos).", "frecuencia": "Diario (Al despertar)"},
            {"accion": "Contacto con la naturaleza (parque, jardín).", "frecuencia": "Semanal"},
            {"accion": "Evitar noticias negativas en la mañana.", "frecuencia": "Diario"}
        ],
        "MEDIO": [
            {"accion": "Diario de Gratitud (3 cosas buenas del día).", "frecuencia": "Diario (Noche)"},
            {"accion": "Conversación profunda con un amigo/familiar.", "frecuencia": "Semanal"},
            {"accion": "Práctica de meditación guiada (10 min).", "frecuencia": "3 veces por semana"}
        ],
        "ALTO": [
            {"accion": "Meditación en silencio o Mindfulness avanzado.", "frecuencia": "Diario (20 min)"},
            {"accion": "Voluntariado o acto de servicio desinteresado.", "frecuencia": "Mensual"},
            {"accion": "Retiro o desconexión total.", "frecuencia": "Trimestral"}
        ]
    }
}

# --- FUNCIONES LOGICAS ---
def leer_informe_anterior_seguro(file_obj):
    try:
        doc = Document(file_obj)
        full_text = " ".join([p.text for p in doc.paragraphs])
        patron = re.search(r"\[DATA\]COG:(\d+);FIS:(\d+);ESP:(\d+)\[END\]", full_text)
        if patron:
            return {
                "PILAR COGNITIVO": int(patron.group(1)),
                "PILAR FÍSICO": int(patron.group(2)),
                "PILAR ESPIRITUAL": int(patron.group(3))
            }
        return None
    except:
        return None

def generar_texto_resumen(scores_act, scores_prev):
    promedios = {p: (sum(vals)/(len(vals)*4))*100 for p, vals in scores_act.items()}
    promedio_global = sum(promedios.values()) / 3
    
    texto = ""
    if promedio_global < 50:
        texto += "Tu estado actual sugiere un modo de 'supervivencia'. Los niveles de energía requieren atención prioritaria. "
    elif promedio_global < 75:
        texto += "Te encuentras en una fase funcional, pero existe potencial latente sin aprovechar. "
    else:
        texto += "Estás en un estado de alto rendimiento y bienestar. "
    
    if scores_prev:
        texto += "\n\nAnálisis Evolutivo: "
        mejoras = 0
        for pilar in scores_act.keys():
            act = sum(scores_act[pilar])
            prev = scores_prev.get(pilar, 0)
            if act > prev: mejoras += 1
        
        if mejoras == 3: texto += "¡Progreso excelente! Mejoraste en todos los pilares."
        elif mejoras > 0: texto += "Se observan avances positivos, aunque algunos pilares requieren ajuste."
        else: texto += "Se detecta un descenso en los indicadores respecto a la última vez."
    return texto

def set_cell_bg(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color)
    tcPr.append(shd)

def crear_informe_final_v7(scores_act, scores_prev, nombre, img_stream, resumen_txt):
    doc = Document()
    
    # MARCA INVISIBLE
    s_str = ";".join([f"{k[:3]}:{sum(v)}" for k, v in scores_act.items()])
    marca = f"[DATA]{s_str}[END]"
    run = doc.add_paragraph().add_run(marca)
    run.font.color.rgb = RGBColor(255, 255, 255)
    run.font.size = Pt(1)

    # HEADER
    tit = doc.add_heading('Informe de Bienestar Integral', 0)
    tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run(f"Fecha: {datetime.now().strftime('%d-%m-%Y')}   |   Evaluado: {nombre}").bold = True

    # 1. RESUMEN
    doc.add_heading('1. Resumen Ejecutivo', 1)
    doc.add_paragraph(resumen_txt)

    # 2. GRÁFICO
    doc.add_heading('2. Análisis Gráfico', 1)
    doc.add_picture(img_stream, width=Inches(6.0))
    doc.add_page_break()

    # 3. PLAN DE MEJORA
    doc.add_heading('3. Plan de Mejora Personalizado', 1)
    
    pilares = ["PILAR COGNITIVO", "PILAR FÍSICO", "PILAR ESPIRITUAL"]
    for p in pilares:
        pts = sum(scores_act[p])
        max_p = len(scores_act[p])*4
        pct = (pts/max_p)*100
        nivel = "BAJO" if pct < 50 else "MEDIO" if pct < 75 else "ALTO"
        
        doc.add_heading(f"{p.title()} (Nivel {nivel})", 2)
        
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        hdr = table.rows[0].cells
        hdr[0].text = "Acción Recomendada"
        hdr[1].text = "Periodicidad"
        
        for cell in hdr:
            set_cell_bg(cell, "EAEAEA")
            cell.paragraphs[0].runs[0].font.bold = True

        acciones = db_plan_accion[p][nivel]
        for acc in acciones:
            row = table.add_row().cells
            row[0].text = acc["accion"]
            row[1].text = acc["frecuencia"]
        doc.add_paragraph("")
    
    bio = io.BytesIO()
    doc.save(bio)
    return bio

# --- INTERFAZ DE STREAMLIT ---

st.title("📊 Diagnóstico de Bienestar Dínamo")
st.write("Responde el siguiente cuestionario para obtener tu informe de bienestar y plan de acción.")

nombre = st.text_input("Nombre completo")

# Sección Carga Historial
with st.expander("📂 ¿Tienes un informe anterior? Cárgalo aquí para comparar"):
    uploaded_file = st.file_uploader("Sube tu archivo .docx anterior", type="docx")

# Cuestionario
scores_actual = {"PILAR COGNITIVO": [], "PILAR FÍSICO": [], "PILAR ESPIRITUAL": []}

with st.form("encuesta_form"):
    for pilar, preguntas in db_encuesta.items():
        st.subheader(pilar)
        for p in preguntas:
            # En Streamlit los radio buttons necesitan una 'key' única
            respuesta = st.radio(
                p["pregunta"], 
                p["opciones"], 
                index=None, 
                key=p["pregunta"]
            )
            # Mapear respuesta a puntaje (si respondió)
            if respuesta:
                idx = p["opciones"].index(respuesta) + 1
                scores_actual[pilar].append(idx)
            else:
                # Marcador temporal para validar después
                scores_actual[pilar].append(0) 
    
    submitted = st.form_submit_button("Generar Informe")

if submitted:
    # Validar que no haya ceros (respuestas vacías)
    respuestas_planas = [item for sublist in scores_actual.values() for item in sublist]
    if 0 in respuestas_planas:
        st.error("⚠️ Por favor responde todas las preguntas antes de generar el informe.")
    else:
        # Procesar
        scores_prev = None
        if uploaded_file is not None:
            scores_prev = leer_informe_anterior_seguro(uploaded_file)
            if scores_prev:
                st.success("✅ Informe anterior cargado y leído correctamente.")
            else:
                st.warning("⚠️ No se pudo leer la data del informe anterior. Se generará un informe base.")

        # Generar Gráfico
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        colores = ['#4e79a7', '#f28e2b', '#e15759']
        pilares = ["PILAR COGNITIVO", "PILAR FÍSICO", "PILAR ESPIRITUAL"]
        
        for i, p in enumerate(pilares):
            ax = axes[i]
            act = sum(scores_actual[p])
            max_p = len(scores_actual[p])*4
            
            if scores_prev:
                prev = scores_prev.get(p, 0)
                ax.bar(["Anterior", "Actual"], [prev, act], color=['#bdc3c7', colores[i]])
                diff = act - prev
                if diff != 0:
                    c = 'green' if diff > 0 else 'red'
                    ax.annotate(f"{diff:+}", xy=(1, act), xytext=(0, prev),
                                arrowprops=dict(arrowstyle="->", color=c, lw=2))
            else:
                ax.bar(["Obtenido", "Máximo"], [act, max_p], color=[colores[i], '#eaeaea'])
            
            pct = (act/max_p)*100
            ax.set_title(f"{p}\n{pct:.0f}%")
            ax.set_ylim(0, max_p*1.2)
        
        st.pyplot(fig)
        
        # Guardar gráfico en memoria para Word
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)
        
        # Generar Word
        resumen = generar_texto_resumen(scores_actual, scores_prev)
        docx_file = crear_informe_final_v7(scores_actual, scores_prev, nombre if nombre else "Usuario", img_buf, resumen)
        
        st.success("¡Informe generado exitosamente!")
        
        # Botón de Descarga
        fecha_str = datetime.now().strftime('%d-%m-%Y')
        nombre_archivo = f"Informe_Bienestar_{nombre.replace(' ', '_')}_{fecha_str}.docx"
        
        st.download_button(
            label="⬇️ Descargar Informe en Word",
            data=docx_file,
            file_name=nombre_archivo,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )