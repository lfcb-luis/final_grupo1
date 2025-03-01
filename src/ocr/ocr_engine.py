import easyocr
import logging
from typing import List, Dict
import re
import cv2
import numpy as np
from config.settings import (
    OCR_LANGUAGES,
    OCR_GPU,
    OCR_MODEL_STORAGE,
    PATTERNS,
    CONFIDENCE_THRESHOLD,
    DATE_KEYWORDS,
    TOTAL_KEYWORDS
)

from .model_setup import ModelSetup

class OCREngine:
    """Clase para manejar el procesamiento OCR de documentos."""
    
    def __init__(self):
        """Inicializa el motor OCR."""
        try:
            self.model_setup = ModelSetup()
            self.reader = self.model_setup.initialize_model()
            
            # Importación tardía de FeatureExtractor
            from src.features.feature_extractor import FeatureExtractor
            self.feature_extractor = FeatureExtractor()
            
            if not self.model_setup.verify_model_files():
                logging.warning("Algunos archivos del modelo podrían faltar")
        except Exception as e:
            logging.error(f"Error inicializando OCR Engine: {str(e)}")
            raise

    def process_image(self, image) -> Dict:
        """
        Procesa una imagen y extrae la información relevante.
        """
        try:
            # Extraer texto de la imagen
            if isinstance(image, list):  # Si recibimos resultados pre-procesados
                text_results = image
            else:  # Si recibimos una imagen
                try:
                    # Asegurarse de que la imagen se pueda procesar
                    
                    # Si es una ruta de archivo, leer la imagen
                    if isinstance(image, str):
                        image = cv2.imread(image)
                    
                    # Validar que la imagen no esté vacía
                    if image is None or image.size == 0:
                        logging.error("Imagen vacía o no se pudo cargar")
                        return {
                            'fields': {},
                            'confidence': 0,
                            'raw_text': "Error: Imagen no válida",
                            'error': "Imagen vacía o no se pudo cargar"
                        }
                    
                    # Redimensionar si es muy grande
                    max_width = 1600
                    if image.shape[1] > max_width:
                        scale = max_width / image.shape[1]
                        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
                    
                    # Convertir a escala de grises si es un problema de color
                    if len(image.shape) == 3 and image.shape[2] == 3:
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    else:
                        gray = image
                    
                    # Intentar diferentes métodos de extracción
                    results = self.reader.readtext(
                        gray,
                        detail=1,
                        paragraph=True
                    )
                    
                    # Manejar caso donde no hay resultados
                    if not results:
                        logging.warning("No se detectó texto en la imagen")
                        return {
                            'fields': {},
                            'confidence': 0,
                            'raw_text': "No se detectó texto",
                            'raw_results': [],
                            'date_details': [],
                            'total_details': []
                        }
                    
                    # Filtrar resultados por confianza
                    text_results = []
                    for result in results:
                        # Verificar que el resultado tenga al menos 3 elementos
                        if len(result) >= 3:
                            try:
                                confidence = float(result[2])
                                if confidence >= CONFIDENCE_THRESHOLD:
                                    text_results.append({
                                        'text': result[1],
                                        'confidence': confidence,
                                        'bbox': result[0]
                                    })
                            except (IndexError, ValueError):
                                logging.warning(f"Resultado OCR con formato inesperado: {result}")
                    
                    # Si no hay resultados con el umbral de confianza
                    if not text_results:
                        logging.warning("No se encontraron resultados con el umbral de confianza")
                        text_results = [{
                            'text': result[1],
                            'confidence': result[2] if len(result) > 2 else 0,
                            'bbox': result[0]
                        } for result in results]
                
                except Exception as e:
                    logging.error(f"Error en la extracción de texto: {str(e)}")
                    import traceback
                    logging.error(traceback.format_exc())
                    return {
                        'fields': {},
                        'confidence': 0,
                        'raw_text': "Error en OCR",
                        'error': str(e)
                    }
            
            # Si no hay resultados de texto, devolver diccionario vacío
            if not text_results:
                return {
                    'fields': {},
                    'confidence': 0,
                    'raw_text': "No se detectó texto",
                    'raw_results': [],
                    'date_details': [],
                    'total_details': []
                }

            # Extraer fechas y totales
            try:
                date_info = self.extract_date(text_results)
            except Exception as e:
                logging.error(f"Error en la extracción de fechas: {str(e)}")
                date_info = {'fecha_emision': None, 'raw_dates': []}
                
            try:
                total_info = self.extract_total(text_results)
            except Exception as e:
                logging.error(f"Error en la extracción de totales: {str(e)}")
                total_info = {'total': None, 'raw_amounts': []}
            
            # Combinar los campos extraídos
            fields = {}
            
            if date_info.get('fecha_emision'):
                fields['fecha_emision'] = date_info.get('fecha_emision')
                
            if total_info.get('total'):
                fields['total'] = total_info.get('total')
            
            # Calcular confianza promedio
            avg_confidence = (
                sum(r['confidence'] for r in text_results) / len(text_results) 
                if text_results else 0
            )
            
            # Añadir campos detallados para debugging
            raw_text = ' '.join([result['text'] for result in text_results]) if text_results else ""
            
            return {
                'fields': fields,
                'confidence': avg_confidence,
                'raw_text': raw_text,
                'raw_results': text_results,
                'date_details': date_info.get('raw_dates', []),
                'total_details': total_info.get('raw_amounts', [])
            }
            
        except Exception as e:
            logging.error(f"Error en el procesamiento OCR: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return {
                'fields': {},
                'confidence': 0,
                'raw_text': "Error en procesamiento",
                'error': str(e)
            }

    def extract_date(self, text_results: List[Dict]) -> Dict:
        """
        Extrae fechas de los resultados del OCR usando múltiples patrones.
        
        Args:
            text_results (List[Dict]): Lista de resultados OCR
            
        Returns:
            Dict: Información sobre las fechas encontradas
        """
        from config.settings import DATE_KEYWORDS, PATTERNS
        
        # Combinar todo el texto para buscar fechas
        text_combined = ' '.join([result['text'] for result in text_results])
        
        found_dates = []
        
        # Buscar fechas con todos los patrones
        date_pattern = PATTERNS.get('date', '')
        matches = re.findall(date_pattern, text_combined, re.IGNORECASE)
        if matches:
            for match in matches:
                found_dates.append({
                    'date_str': match,
                    'pattern': date_pattern
                })
        
        # Buscar fechas en contextos con palabras clave
        for block in text_results:
            text = block['text'].lower()
            # Verificar si alguna palabra clave está en este bloque
            if any(palabra in text for palabra in DATE_KEYWORDS):
                date_pattern = PATTERNS.get('date', '')
                matches = re.findall(date_pattern, text, re.IGNORECASE)
                if matches:
                    for match in matches:
                        found_dates.append({
                            'date_str': match,
                            'pattern': date_pattern,
                            'has_keyword': True,
                            'confidence': block.get('confidence', 0)
                        })
        
        # Si encontramos fechas, intentar estandarizarlas
        if found_dates:
            # Priorizar fechas con palabras clave
            found_dates.sort(key=lambda x: (0 if x.get('has_keyword', False) else 1, 
                                        -x.get('confidence', 0)))
            
            # Estandarizar la primera fecha (la más probable)
            if found_dates:  # Verificar nuevamente después de ordenar (por seguridad)
                standardized_date = self._standardize_date(found_dates[0]['date_str'])
                return {
                    'fecha_emision': standardized_date,
                    'raw_dates': found_dates
                }
        
        return {'fecha_emision': None, 'raw_dates': []}

    def _standardize_date(self, date_str: str) -> str:
        """
        Estandariza una fecha al formato YYYY-MM-DD.
        """
        from config.settings import DATE_FORMATS
        DATE_FORMATS.append('%d-%b-%Y')  # Agregar el formato '%d-%b-%
        from datetime import datetime
        
        # Limpieza básica
        date_str = date_str.strip()
        
        # Probar con los formatos conocidos
        for fmt in DATE_FORMATS:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Si no se pudo estandarizar, devolver la cadena original
        return date_str

    def extract_total(self, text_results: List[Dict]) -> Dict:
        """
        Extrae importes totales de los resultados del OCR.
        
        Args:
            text_results (List[Dict]): Lista de resultados OCR
            
        Returns:
            Dict: Información sobre los totales encontrados
        """
        from config.settings import TOTAL_KEYWORDS, PATTERNS
        
        # Combinar todo el texto para buscar totales
        text_combined = ' '.join([result['text'] for result in text_results])
        
        found_amounts = []
        
        # Buscar palabras clave de total en bloques individuales
        for block in text_results:
            text = block['text'].lower()
            if 'total' in text:
                # Buscar patrones de monto
                amount_pattern = PATTERNS.get('amount', '')
                matches = re.findall(amount_pattern, text, re.IGNORECASE)
                if matches:
                    for match in matches:
                        found_amounts.append({
                            'amount_str': match,
                            'has_keyword': True,
                            'confidence': block.get('confidence', 0)
                        })
        
        # Si no encontramos montos con palabras clave, buscar cualquier patrón que parezca un monto
        if not found_amounts:
            amount_pattern = PATTERNS.get('amount', '')
            matches = re.findall(amount_pattern, text_combined, re.IGNORECASE)
            if matches:
                for match in matches:
                    found_amounts.append({'amount_str': match, 'has_keyword': False})
        
        # Buscar específicamente patrones como "Balance Due" o "Total a pagar"
        for balance_pattern in [
            r'balance\s+due\s*(?:\$|€|£)?\s*(\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?)',
            r'total\s+a\s+pagar\s*(?:\$|€|£)?\s*(\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?)'
        ]:
            matches = re.findall(balance_pattern, text_combined, re.IGNORECASE)
            if matches:
                for match in matches:
                    found_amounts.append({'amount_str': match, 'has_keyword': True, 'specific_pattern': True})
        
        # Si encontramos totales, intentar estandarizarlos
        if found_amounts:
            # Ordenar por prioridad (específico > palabras clave > resto)
            found_amounts.sort(key=lambda x: (
                0 if x.get('specific_pattern', False) else 
                (1 if x.get('has_keyword', False) else 2)
            ))
            
            # Estandarizar el primer total (el más probable)
            if found_amounts:  # Verificar nuevamente después de ordenar
                standardized_amount = self._standardize_amount(found_amounts[0]['amount_str'])
                return {
                    'total': standardized_amount,
                    'raw_amounts': found_amounts
                }
        
        return {'total': None, 'raw_amounts': []}
    
    def _standardize_amount(self, amount_str: str) -> str:
        """
        Estandariza un importe a formato numérico.
        """
        # Eliminar símbolos de moneda y espacios
        amount_str = re.sub(r'[^\d,.]', '', amount_str)
        
        # Determinar el formato (usar coma o punto para decimales)
        if ',' in amount_str and '.' in amount_str:
            # Si tiene ambos, el último es el decimal
            if amount_str.rindex('.') > amount_str.rindex(','):
                # Punto como decimal
                amount_str = amount_str.replace(',', '')
            else:
                # Coma como decimal
                amount_str = amount_str.replace('.', '')
                amount_str = amount_str.replace(',', '.')
        elif ',' in amount_str:
            # Si solo tiene comas, asumir que es decimal si está al final con 2 dígitos
            if amount_str.rindex(',') >= len(amount_str) - 3:
                amount_str = amount_str.replace(',', '.')
            else:
                # Es separador de miles
                amount_str = amount_str.replace(',', '')
        
        # Convertir a float y redondear a 2 decimales
        try:
            amount = float(amount_str)
            return "{:.2f}".format(amount)
        except ValueError:
            return amount_str