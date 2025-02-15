# src/ocr/ocr_engine.py
import easyocr
import logging
from typing import List, Dict
import re
from config.settings import (
    OCR_LANGUAGES,
    OCR_GPU,
    OCR_MODEL_STORAGE,
    PATTERNS,
    DOCUMENT_TYPES,
    CONFIDENCE_THRESHOLD
)


from .model_setup import ModelSetup

class OCREngine:
    """Clase para manejar el procesamiento OCR de documentos."""
    
    def __init__(self):
        """Inicializa el motor OCR."""
        try:
            self.model_setup = ModelSetup()
            self.reader = self.model_setup.initialize_model()
            if not self.model_setup.verify_model_files():
                logging.warning("Algunos archivos del modelo podrían faltar")
        except Exception as e:
            logging.error(f"Error inicializando OCR Engine: {str(e)}")
            raise

    def detect_document_type(self, text_results: List[Dict]) -> str:
        """
        Detecta el tipo de documento basado en el texto extraído.
        
        Args:
            text_results (List[Dict]): Lista de resultados OCR
            
        Returns:
            str: Tipo de documento ('AGUA', 'LUZ' o 'DESCONOCIDO')
        """
        text_combined = ' '.join([result['text'].lower() for result in text_results])
        
        for doc_type, config in DOCUMENT_TYPES.items():
            for identificador in config['identificadores']:
                if identificador.lower() in text_combined:
                    return doc_type
        
        return 'DESCONOCIDO'

    def extract_fields(self, text_results: List[Dict], document_type: str) -> Dict:
        """
        Extrae campos específicos de los resultados del OCR.
        
        Args:
            text_results (List[Dict]): Lista de resultados OCR
            document_type (str): Tipo de documento ('AGUA' o 'LUZ')
            
        Returns:
            Dict: Campos extraídos
        """
        fields = {}
        
        # Filtrar resultados por nivel de confianza
        valid_results = [
            result for result in text_results 
            if result.get('confidence', 0) >= CONFIDENCE_THRESHOLD
        ]
        
        # Si no hay resultados válidos, retornar diccionario vacío
        if not valid_results:
            return fields
            
        text_combined = ' '.join([result['text'] for result in valid_results])
        
        # Extraer fecha
        fecha_match = re.search(r'Fecha de (?:la )?(?:factura|Emisión):\s*(.+?)(?=\s|$)', text_combined)
        if fecha_match:
            fields['fecha_emision'] = fecha_match.group(1).strip()
        
        # Extraer total
        total_match = re.search(r'TOTAL(?:\sA PAGAR)?:?\s*\$?\s*([\d,]+)', text_combined)
        if total_match:
            fields['total'] = total_match.group(1).strip()
        
        # Extraer matrícula si está presente
        matricula_match = re.search(r'MATRÍCULA\s*(?:>>)?\s*(\d+)', text_combined)
        if matricula_match:
            fields['matricula'] = matricula_match.group(1).strip()
        
        return fields
    
    def validate_fields(self, fields: Dict, document_type: str) -> bool:
        """
        Valida que estén todos los campos requeridos según el tipo de documento.
        
        Args:
            fields (Dict): Campos extraídos
            document_type (str): Tipo de documento
            
        Returns:
            bool: True si todos los campos requeridos están presentes
        """
        if document_type not in DOCUMENT_TYPES:
            return False
            
        required_fields = DOCUMENT_TYPES[document_type]['campos_requeridos']
        return all(field in fields for field in required_fields)

    def process_image(self, image) -> Dict:
        """
        Procesa una imagen y extrae la información relevante.
        """
        try:
            # Extraer texto de la imagen
            if isinstance(image, list):  # Si recibimos resultados pre-procesados
                text_results = image
            else:  # Si recibimos una imagen
                results = self.reader.readtext(
                    image,
                    detail=1,
                    paragraph=True
                )
                text_results = [
                    {
                        'text': result[1],
                        'confidence': result[2],
                        'bbox': result[0]
                    }
                    for result in results
                    if result[2] >= CONFIDENCE_THRESHOLD
                ]

            # Detectar tipo de documento
            document_type = self.detect_document_type(text_results)
            
            # Extraer campos según el tipo de documento
            fields = self.extract_fields(text_results, document_type)
            
            # Validar campos
            is_valid = self.validate_fields(fields, document_type)
            
            return {
                'document_type': document_type,
                'fields': fields,
                'is_valid': is_valid,
                'confidence': sum(r['confidence'] for r in text_results) / len(text_results) if text_results else 0
            }
            
        except Exception as e:
            logging.error(f"Error en el procesamiento OCR: {str(e)}")
            raise