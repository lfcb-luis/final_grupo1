# web_app/app.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import json
from datetime import datetime


# Importar nuestros módulos
from src.preprocessing.image_processor import ImageProcessor
from src.ocr.ocr_engine import OCREngine
from src.validation.field_validator import FieldValidator
from config.settings import (
    STREAMLIT_TITLE,
    STREAMLIT_DESCRIPTION,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE
)

class OCRApp:
    def __init__(self):
        """Inicializa la aplicación web."""
        self.image_processor = ImageProcessor()
        self.ocr_engine = OCREngine()
        self.validator = FieldValidator()
        
        # Configurar página
        st.set_page_config(
            page_title="Sistema OCR",
            page_icon="📄",
            layout="wide"
        )

    def setup_sidebar(self):
        """Configura la barra lateral."""
        st.sidebar.title("Configuración")
        st.sidebar.markdown("### Opciones de Procesamiento")
        
        options = {
            'deskew': st.sidebar.checkbox('Corregir inclinación', value=True),
            'denoise': st.sidebar.checkbox('Reducir ruido', value=True),
            'enhance_contrast': st.sidebar.checkbox('Mejorar contraste', value=True)
        }
        
        return options

    def save_results(self, results, image_name):
        """Guarda los resultados en un archivo JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resultados_{timestamp}_{image_name}.json"
        
        with open(os.path.join("data", "processed", filename), 'w') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        return filename

    def run(self):
        """Ejecuta la aplicación principal."""
        st.title(STREAMLIT_TITLE)
        st.markdown(STREAMLIT_DESCRIPTION)
        
        # Configurar sidebar
        options = self.setup_sidebar()
        
        # Área de carga de archivos
        uploaded_file = st.file_uploader(
            "Cargar documento",
            type=ALLOWED_EXTENSIONS
        )
        
        if uploaded_file is not None:
            # Verificar tamaño del archivo
            if uploaded_file.size > MAX_FILE_SIZE:
                st.error(f"El archivo excede el tamaño máximo permitido de {MAX_FILE_SIZE/1024/1024}MB")
                return
            
            # Mostrar imagen original
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Imagen Original")
                image = Image.open(uploaded_file)
                st.image(image, use_column_width=True)
            
            # Procesar imagen cuando se presione el botón
            if st.button("Procesar Documento"):
                with st.spinner('Procesando...'):
                    try:
                        # Convertir imagen a formato OpenCV
                        cv_image = cv2.cvtColor(
                            np.array(image),
                            cv2.COLOR_RGB2BGR
                        )
                        
                        # Procesar imagen
                        processed_image = self.image_processor.process(cv_image)
                        
                        # Mostrar imagen procesada
                        with col2:
                            st.subheader("Imagen Procesada")
                            processed_pil = Image.fromarray(processed_image)
                            st.image(processed_pil, use_column_width=True)
                        
                        # Extraer texto
                        results = self.ocr_engine.process_image(processed_image)
                        
                        # Validar campos
                        validation_results = self.validator.validate_fields(
                            results['fields'],
                            results['document_type']
                        )
                        
                        # Mostrar resultados
                        st.subheader("Resultados")
                        col3, col4 = st.columns(2)
                        
                        with col3:
                            st.markdown("### Información Extraída")
                            st.json(results['fields'])
                            
                        with col4:
                            st.markdown("### Validación")
                            if validation_results['is_valid']:
                                st.success("✅ Todos los campos son válidos")
                            else:
                                st.error("❌ Se encontraron errores")
                                for error in validation_results['errors']:
                                    st.warning(error)
                        
                        # Guardar resultados
                        if st.button("Exportar Resultados"):
                            filename = self.save_results(
                                results,
                                uploaded_file.name
                            )
                            st.success(f"Resultados guardados en {filename}")
                            
                    except Exception as e:
                        st.error(f"Error procesando el documento: {str(e)}")

if __name__ == "__main__":
    app = OCRApp()
    app.run()