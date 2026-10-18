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
    st.info("Procesando el documento...")
    try:
        texto_completo = ""
        if archivo.name.lower().endswith('.pdf'):
            lector_pdf = PyPDF2.PdfReader(archivo)
            for pagina in lector_pdf.pages:
                texto = pagina.extract_text()
                if texto:
                    texto_completo += texto + "\n"
        elif archivo.name.lower().endswith('.docx'):
            doc_word = docx.Document(archivo)
            for parrafo in doc_word.paragraphs:
                texto_completo += parrafo.text + "\n"
        
        if texto_completo.strip() == "":
            st.error("No se encontró texto.")
        else:
            idioma_detectado = detect(texto_completo)
            idioma_gtts = 'es' if idioma_detectado == 'es' else 'en'
            
            st.success(f"Idioma detectado: {'Español' if idioma_gtts == 'es' else 'Inglés'}")
            st.warning("Generando audio, por favor espera...")
            
            tts = gTTS(text=texto_completo, lang=idioma_gtts, slow=es_lento)
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            
            st.success("¡Audio listo!")
            st.audio(audio_bytes, format='audio/mp3')
    except Exception as e:
        st.error(f"Error: {e}")