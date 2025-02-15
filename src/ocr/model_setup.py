# src/ocr/model_setup.py
import os
import logging
from pathlib import Path
import easyocr
from config.settings import OCR_LANGUAGES, OCR_MODEL_STORAGE, OCR_GPU

class ModelSetup:
    """Clase para manejar la configuración inicial del modelo OCR."""
    
    @staticmethod
    def initialize_model():
        """
        Inicializa y verifica el modelo OCR.
        Descarga el modelo si no existe.
        """
        try:
            # Asegurar que existe el directorio para el modelo
            Path(OCR_MODEL_STORAGE).mkdir(parents=True, exist_ok=True)
            
            logging.info("Iniciando configuración del modelo OCR...")
            
            # Inicializar EasyOCR
            reader = easyocr.Reader(
                lang_list=OCR_LANGUAGES,
                gpu=OCR_GPU,
                model_storage_directory=OCR_MODEL_STORAGE
            )
            
            logging.info("Modelo OCR inicializado correctamente")
            return reader
            
        except Exception as e:
            logging.error(f"Error inicializando el modelo OCR: {str(e)}")
            raise

    @staticmethod
    def verify_model_files():
        """
        Verifica que los archivos necesarios del modelo existan.
        
        Returns:
            bool: True si todos los archivos necesarios están presentes
        """
        required_files = [
            'craft_mlt_25k.pth',
            'latin.pth'
        ]
        
        for file in required_files:
            file_path = os.path.join(OCR_MODEL_STORAGE, file)
            if not os.path.exists(file_path):
                logging.warning(f"Archivo de modelo faltante: {file}")
                return False
                
        return True

    @staticmethod
    def get_model_info():
        """
        Obtiene información sobre el modelo instalado.
        
        Returns:
            Dict: Información del modelo
        """
        return {
            'languages': OCR_LANGUAGES,
            'gpu_enabled': OCR_GPU,
            'model_path': OCR_MODEL_STORAGE,
            'files_present': ModelSetup.verify_model_files()
        }