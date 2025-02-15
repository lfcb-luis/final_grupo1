# web_app/app.py
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
from typing import Dict, Any
import easyocr

from src.preprocessing.image_processor import ImageProcessor
from src.features.feature_extractor import FeatureExtractor
from config.settings import STREAMLIT_TITLE, STREAMLIT_DESCRIPTION, OCR_LANGUAGES, OCR_GPU


class OCRApp:
    def __init__(self):
        """Inicializa la aplicación web."""
        self.image_processor = ImageProcessor()
        self.feature_extractor = FeatureExtractor()
        # Inicializar EasyOCR
        self.reader = easyocr.Reader(OCR_LANGUAGES, gpu=OCR_GPU)
        
        # Configurar página
        st.set_page_config(
            page_title="Sistema OCR para Facturas",
            page_icon="📄",
            layout="wide"
        )
    
    def run(self):
        """Ejecuta la aplicación principal."""
        st.title("Sistema OCR para Facturas")
        st.markdown("""
        Este sistema procesa facturas y extrae automáticamente información relevante como:
        - Números de identificación
        - Fechas de emisión y vencimiento
        - Montos totales
        - Otros campos específicos
        """)
        
        # Área de carga de archivos
        uploaded_file = st.file_uploader(
            "Cargar factura",
            type=['png', 'jpg', 'jpeg'],
            help="Seleccione una imagen de factura para procesar"
        )
        
        if uploaded_file is not None:
            # Mostrar imagen original y procesada
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Imagen Original")
                image = Image.open(uploaded_file)
                st.image(image, use_column_width=True)
            
            # Procesar imagen cuando se presione el botón
            if st.button("Procesar Factura"):
                with st.spinner('Procesando imagen...'):
                    try:
                        # Convertir imagen a formato OpenCV
                        cv_image = cv2.cvtColor(
                            np.array(image),
                            cv2.COLOR_RGB2BGR
                        )
                        
                        # Procesar imagen
                        with col2:
                            st.subheader("Imagen Procesada")
                            processed_image = self.image_processor.process(cv_image)
                            st.image(processed_image, use_column_width=True)
                        
                        # Extraer información
                        texto_extraido = self.extract_text(processed_image)
                        if texto_extraido:
                            self.display_results(texto_extraido)
                            
                    except Exception as e:
                        st.error(f"Error procesando la imagen: {str(e)}")

    def extract_text(self, image) -> Dict[str, Any]:
        """
        Extrae texto de la imagen procesada usando EasyOCR.
        """
        try:
            # Usar el reader de la clase
            results = self.reader.readtext(image)
            # Convertir resultados al formato esperado por el extractor
            text_blocks = [
                {
                    'text': text,
                    'confidence': conf,
                    'bbox': box
                }
                for box, text, conf in results
            ]
            # Extraer campos usando el feature extractor
            fields = self.feature_extractor.extract_fields(text_blocks)
            return fields
        except Exception as e:
            st.error(f"Error extrayendo texto: {str(e)}")
            return {}

    def display_results(self, fields: Dict[str, Any]):
        """
        Muestra los resultados extraídos.
        """
        st.subheader("Información Extraída")
        
        # Crear columnas para mostrar resultados
        col1, col2 = st.columns(2)
        
        with col1:
            # Campos principales
            st.markdown("### Campos Principales")
            if 'identificacion' in fields:
                st.write(f"📋 **ID/Matrícula:** {fields['identificacion']}")
            if 'fecha_expedicion' in fields:
                st.write(f"📅 **Fecha Expedición:** {fields['fecha_expedicion']}")
            if 'fecha_vencimiento' in fields:
                st.write(f"⚠️ **Fecha Vencimiento:** {fields['fecha_vencimiento']}")
            if 'total' in fields:
                st.write(f"💰 **Total:** ${fields['total']}")
        
        with col2:
            # Campos adicionales
            st.markdown("### Campos Adicionales")
            for key, value in fields.items():
                if key not in ['identificacion', 'fecha_expedicion', 'fecha_vencimiento', 'total']:
                    st.write(f"🔹 **{key.replace('_', ' ').title()}:** {value}")
        
        # Opción para exportar resultados
        if st.button("Exportar Resultados"):
            # TODO: Implementar exportación
            st.info("Función de exportación en desarrollo")

if __name__ == "__main__":
    app = OCRApp()
    app.run()