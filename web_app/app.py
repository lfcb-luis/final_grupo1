# web_app/app.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import time
import sys
from typing import Dict, Any
import easyocr


# Añadir el directorio raíz al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.preprocessing.image_processor import ImageProcessor
from src.ocr.ocr_engine import OCREngine
from config.settings import (
    OCR_LANGUAGES, 
    OCR_GPU, 
    OCR_MODEL_STORAGE,
    STREAMLIT_TITLE, 
    STREAMLIT_DESCRIPTION,
    CONFIDENCE_THRESHOLD
)

    # Importación específica
from src.features.feature_extractor import FeatureExtractor as DocumentProcessor



class OCRApp:
    def __init__(self):
        """Inicializa la aplicación web."""
        # Configurar página
        st.set_page_config(
            page_title="Extractor de Datos de Facturas",
            page_icon="📄",
            layout="wide"
        )

        # Inicializar procesadores
        self.image_processor = ImageProcessor()

         # Inicializar Document Processor
        self.document_processor = DocumentProcessor()
        
        # Inicializar OCR Engine con manejo de errores
        self._initialize_ocr()

    def _initialize_ocr(self):
        """Inicializa el motor OCR con manejo de errores."""
        try:
            with st.spinner('⏳ Cargando motor OCR... (puede tomar unos minutos la primera vez)'):
                # Inicializar OCR Engine que contiene el modelo mejorado
                self.ocr_engine = OCREngine()
                st.success('✅ Motor OCR cargado exitosamente')
                
        except Exception as e:
            st.error(f'❌ Error al cargar el motor OCR: {str(e)}')
            raise

    def run(self):
        """Ejecuta la aplicación principal."""
        st.title("Extractor de Datos de Facturas")
        st.markdown("""
        ### Este sistema extrae automáticamente:
        - 📅 Fecha de Emisión
        - ⚠️ Fecha de Vencimiento
        - 💰 Total a Pagar
        """)
        
        # Área de carga de archivos
        uploaded_file = st.file_uploader(
            "Cargar factura",
            type=['png', 'jpg', 'jpeg'],
            help="Formatos soportados: PNG, JPG, JPEG"
        )
        
        if uploaded_file is not None:
            self._process_uploaded_file(uploaded_file)

    def _process_uploaded_file(self, uploaded_file):
        """Procesa el archivo subido."""
        # Mostrar imagen original
        st.subheader("Imagen Cargada")
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
        
        # Botón de procesamiento
        if st.button("🔍 Procesar Factura"):
            with st.spinner('⏳ Procesando imagen...'):
                try:
                    # Guardar imagen temporalmente
                    temp_path = os.path.join('data', 'temp', uploaded_file.name)
                    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                    
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Procesar documento con el nuevo procesador
                    result = self.document_processor.process_document(temp_path)
                    
                    # Limpiar archivo temporal
                    os.remove(temp_path)
                    
                    if result['success']:
                        st.success("✅ Extracción completada")
                        self.display_results(result)
                    else:
                        st.warning(f"⚠️ No se pudo extraer información: {result.get('error', 'Error desconocido')}")
                    
                except Exception as e:
                    st.error(f"❌ Error procesando la imagen: {str(e)}")

    def display_results(self, result: Dict[str, Any]):
        """Muestra los resultados extraídos."""
        st.subheader("Información Extraída")
        
        # Extraer los campos del resultado
        fields = result.get('extracted_fields', {})
        
        # Mostrar fecha si se encontró
        if 'fecha_expedicion' in fields and fields['fecha_expedicion']:
            st.write(f"📅 Fecha: **{fields['fecha_expedicion']}**")
        else:
            st.info("ℹ️ No se encontró fecha")
        
        # Mostrar total si se encontró
        if 'total' in fields and fields['total']:
            valor = f"${fields['total']}" if not str(fields['total']).startswith('$') else fields['total']
            st.write(f"💰 Total: **{valor}**")
        else:
            st.info("ℹ️ No se encontró total")
        
        # Mostrar información de depuración
        with st.expander("Mostrar información de depuración"):
            # Mostrar campos extraídos
            st.subheader("Campos Extraídos")
            st.json(fields)
            
            # Mostrar resultado de validación
            st.subheader("Validación")
            st.write(result.get('validation', {}))
            
            # Mostrar texto raw
            if 'raw_text' in result:
                st.subheader("Texto extraído")
                st.text(result['raw_text'])
                    
if __name__ == "__main__":
    app = OCRApp()
    app.run()