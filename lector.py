import streamlit as st
import PyPDF2
import docx
from gtts import gTTS
from langdetect import detect
import io

st.set_page_config(page_title="Lector de Documentos", page_icon="🎧")
st.title("🎧 Lector de PDF y Word a Voz")

velocidad = st.radio("Velocidad de la voz:", ["Normal", "Lenta"], horizontal=True)
es_lento = True if velocidad == "Lenta" else False

archivo = st.file_uploader("Sube tu archivo PDF o Word", type=["pdf", "docx"])

if archivo is not None:
    texto_a_leer = ""
    
    try:
        # SI EL ARCHIVO ES PDF
        if archivo.name.lower().endswith('.pdf'):
            lector_pdf = PyPDF2.PdfReader(archivo)
            total_paginas = len(lector_pdf.pages)
            
            st.write("---")
            st.subheader("📄 Opciones de Lectura")
            opcion = st.radio("¿Qué parte del PDF quieres escuchar?", 
                              ["Una página específica", 
                               "Un rango de páginas (Ej. de la 5 a la 10)", 
                               "Todo el documento (Puede dar error si es muy largo)"])
            
            if opcion == "Una página específica":
                pagina_elegida = st.number_input(f"Elige la página (1 a {total_paginas}):", min_value=1, max_value=total_paginas, value=1)
                texto_a_leer = lector_pdf.pages[pagina_elegida - 1].extract_text()
                st.info(f"Se leerá únicamente la página {pagina_elegida}.")
                
            elif opcion == "Un rango de páginas (Ej. de la 5 a la 10)":
                col1, col2 = st.columns(2)
                with col1:
                    pag_inicio = st.number_input("Página de inicio:", min_value=1, max_value=total_paginas, value=1)
                with col2:
                    pag_fin = st.number_input("Página final:", min_value=pag_inicio, max_value=total_paginas, value=min(pag_inicio + 4, total_paginas))
                
                for i in range(pag_inicio - 1, pag_fin):
                    txt = lector_pdf.pages[i].extract_text()
                    if txt:
                        texto_a_leer += txt + "\n"
                st.info(f"Se leerán desde la página {pag_inicio} hasta la {pag_fin}.")
                
            else:
                st.warning("⚠️ Precaución: Leer documentos de muchas páginas de un solo golpe puede bloquear el servidor de Google (Error 429).")
                for pagina in lector_pdf.pages:
                    txt = pagina.extract_text()
                    if txt:
                        texto_a_leer += txt + "\n"
                        
        # SI EL ARCHIVO ES WORD
        elif archivo.name.lower().endswith('.docx'):
            st.write("---")
            st.info("Nota: Los archivos de Word se leerán completos.")
            doc_word = docx.Document(archivo)
            for parrafo in doc_word.paragraphs:
                texto_a_leer += parrafo.text + "\n"

        # VERIFICAR QUE HAYA TEXTO Y MOSTRAR BOTÓN
        if texto_a_leer.strip() == "":
            st.error("No se encontró texto en tu selección. Puede que la página esté en blanco o sea una imagen.")
        else:
            # BOTÓN PARA GENERAR EL AUDIO
            if st.button("▶️ Generar Audio"):
                st.info("Procesando el texto y generando la voz... por favor espera.")
                
                idioma_detectado = detect(texto_a_leer)
                idioma_gtts = 'es' if idioma_detectado == 'es' else 'en'
                st.success(f"Idioma detectado: {'Español' if idioma_gtts == 'es' else 'Inglés'}")
                
                tts = gTTS(text=texto_a_leer, lang=idioma_gtts, slow=es_lento)
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                
                st.success("¡Audio listo!")
                st.audio(audio_bytes, format='audio/mp3')
                
    except Exception as e:
        st.error(f"Error al generar el audio. Tip: Si elegiste demasiadas páginas y da error, intenta con un rango más pequeño. (Detalle: {e})")
