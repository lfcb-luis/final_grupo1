# web_app/app.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import time
from typing import Dict, Any
import easyocr

from src.preprocessing.image_processor import ImageProcessor
from src.features.feature_extractor import FeatureExtractor
from config.settings import (
    OCR_LANGUAGES, 
    OCR_GPU, 
    OCR_MODEL_STORAGE,
    STREAMLIT_TITLE, 
    STREAMLIT_DESCRIPTION
)

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
        self.feature_extractor = FeatureExtractor()
        
        # Inicializar EasyOCR con manejo de errores
        self._initialize_ocr()

    def _initialize_ocr(self):
        """Inicializa el modelo OCR con manejo de errores."""
        try:
            with st.spinner('⏳ Cargando modelo OCR... (puede tomar unos minutos la primera vez)'):
                # Asegurar que el directorio de modelos existe
                os.makedirs(OCR_MODEL_STORAGE, exist_ok=True)
                
                # Primer intento de inicialización
                self.reader = easyocr.Reader(
                    OCR_LANGUAGES,
                    gpu=OCR_GPU,
                    model_storage_directory=OCR_MODEL_STORAGE,
                    download_enabled=True,
                    verbose=False
                )
                st.success('✅ Modelo OCR cargado exitosamente')
                
        except PermissionError:
            st.warning('⚠️ Error de permisos. Reiniciando la carga del modelo...')
            time.sleep(2)  # Esperar a que el sistema libere recursos
            try:
                self.reader = easyocr.Reader(
                    OCR_LANGUAGES,
                    gpu=OCR_GPU,
                    model_storage_directory=OCR_MODEL_STORAGE,
                    download_enabled=True,
                    verbose=False
                )
                st.success('✅ Modelo OCR cargado exitosamente en el segundo intento')
            except Exception as e:
                st.error(f'❌ Error al cargar el modelo OCR: {str(e)}')
                raise
        except Exception as e:
            st.error(f'❌ Error inesperado al cargar el modelo OCR: {str(e)}')
            raise

    def run(self):
        """Ejecuta la aplicación principal."""
        st.title("Extractor de Datos de Facturas")
        st.markdown("""
        ### Este sistema extrae automáticamente:
        - 📋 Número de Identificación/Matrícula
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
                    # Convertir imagen
                    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    
                    # Procesar imagen
                    processed_image = self.image_processor.process(cv_image)
                    
                    # Extraer información
                    fields = self.extract_text(processed_image)
                    
                    if fields:
                        st.success("✅ Extracción completada")
                        self.display_results(fields)
                    else:
                        st.warning("⚠️ No se pudo extraer información. Intente con otra imagen.")
                        
                except Exception as e:
                    st.error(f"❌ Error procesando la imagen: {str(e)}")

    def extract_text(self, image) -> Dict[str, Any]:
        """Extrae texto de la imagen procesada."""
        try:
            # Mejorar contraste
            enhanced = cv2.convertScaleAbs(image, alpha=1.5, beta=0)
            
            # Extraer texto
            results = self.reader.readtext(enhanced)
            
            # Convertir resultados
            text_blocks = [
                {
                    'text': text,
                    'confidence': conf,
                    'bbox': box
                }
                for box, text, conf in results
                if conf > 0.5
            ]
            
            # Extraer campos
            return self.feature_extractor.extract_fields(text_blocks)
            
        except Exception as e:
            st.error(f"Error en extracción: {str(e)}")
            return {}

    def display_results(self, fields: Dict[str, Any]):
        """Muestra los resultados extraídos."""
        st.subheader("Información Extraída")
        
        campos = {
            'identificacion': ('📋 Número de Identificación/Matrícula', 'No se encontró número de identificación'),
            'fecha_inicio': ('📅 Fecha de Emisión', 'No se encontró fecha de emisión'),
            'fecha_fin': ('⚠️ Fecha de Vencimiento', 'No se encontró fecha de vencimiento'),
            'total': ('💰 Total a Pagar', 'No se encontró monto total')
        }
        
        for campo, (label, mensaje_error) in campos.items():
            if campo in fields and fields[campo]:
                valor = f"${fields[campo]}" if campo == 'total' else fields[campo]
                st.write(f"{label}: **{valor}**")
            else:
                st.info(f"ℹ️ {mensaje_error}")

if __name__ == "__main__":
    app = OCRApp()
    app.run()