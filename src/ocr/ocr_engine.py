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

class OCREngine:
    """Clase para manejar el procesamiento OCR de documentos."""
    
    def __init__(self):
        """Inicializa el motor OCR."""
        try:
            self.reader = easyocr.Reader(
                OCR_LANGUAGES,
                gpu=OCR_GPU,
                model_storage_directory=OCR_MODEL_STORAGE
            )
        except Exception as e:
            logging.error(f"Error inicializando EasyOCR: {str(e)}")
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
        Extrae campos específicos según el tipo de documento.
        
        Args:
            text_results (List[Dict]): Lista de resultados OCR
            document_type (str): Tipo de documento
            
        Returns:
            Dict: Campos extraídos
        """
        fields = {}
        text_combined = ' '.join([result['text'] for result in text_results])
        
        # Extraer matrícula
        if 'matricula' in PATTERNS:
            matricula_match = re.search(PATTERNS['matricula'], text_combined)
            if matricula_match:
                fields['matricula'] = matricula_match.group(0)
        
        # Extraer fechas
        date_matches = re.finditer(PATTERNS['date'], text_combined)
        for match in date_matches:
            date_text = match.group(0)
            # Asignar fecha según contexto
            if 'fecha de la factura' in text_combined.lower():
                fields['fecha_factura'] = date_text
            elif 'fecha limite' in text_combined.lower():
                fields['fecha_vencimiento'] = date_text
            elif 'fecha de emisión' in text_combined.lower():
                fields['fecha_emision'] = date_text
        
        # Extraer monto total
        amount_matches = re.finditer(PATTERNS['amount'], text_combined)
        for match in amount_matches:
            amount_text = match.group(0)
            if 'total' in text_combined.lower():
                fields['total'] = amount_text.replace('$', '').replace(',', '')
        
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
        
        Args:
            image: Imagen procesada
            
        Returns:
            Dict: Información extraída y validada
        """
        try:
            # Extraer texto de la imagen
            results = self.reader.readtext(
                image,
                detail=1,
                paragraph=True
            )
            
            # Convertir resultados a formato estandarizado
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
                'confidence': sum(r['confidence'] for r in text_results) / len(text_results)
            }
            
        except Exception as e:
            logging.error(f"Error en el procesamiento OCR: {str(e)}")
            raise