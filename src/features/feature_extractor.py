# src/features/feature_extractor.py
import re
import logging
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from config.settings import CONFIDENCE_THRESHOLD

class FeatureExtractor:
    def __init__(self):
        """Inicializa los patrones de extracción para campos comunes en cualquier factura."""
        # Patrones para fechas - funcionan en español e inglés
        self.patrones_fecha = [
            # DD/MM/YYYY o DD-MM-YYYY con separadores y meses en mayúsculas o minúsculas (más flexible)
            r'(\d{1,2})[/.-]([A-Za-z]{3})[/.-](\d{2,4})',
            r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})',
            # YYYY/MM/DD o YYYY-MM-DD
            r'(\d{4})[/.-](\d{1,2})[/.-](\d{1,2})',
            # Fechas con nombres de mes en español (case-insensitive)
            r'(\d{1,2})?\s*(?:de)?\s*(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s*(?:de|del)?\s*(\d{2,4})',
            r'(\d{1,2})[-\s]*(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)[-\s]*(\d{2,4})',
            # Fechas con nombres de mes en inglés
            r'(\d{1,2})?\s?(january|february|march|april|may|june|july|august|september|october|november|december)\s?(?:of)?\s?(\d{2,4})',
            # Fechas abreviadas en español
            r'(\d{1,2})[-\s]?(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)[-\s]?(\d{2,4})',
            # Fechas abreviadas en inglés
            r'(\d{1,2})[-\s]?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[-\s]?(\d{2,4})'
        ]
        
        # Palabras clave para fechas con mayor flexibilidad
        self.palabras_clave_fecha = [
            # Español
            'fecha', 'emision', 'emisión', 'expedicion', 'expedición', 
            'generacion', 'generación', 'emitido', 'emitida', 'expedido', 'expedida',
            'limite', 'generada', 'generado', 'el', 'de', 'hasta',
            # Inglés
            'date', 'issue', 'issued', 'generation', 'created', 'invoice date',
            'limit', 'generated', 'on', 'until'
        ]
        
        # Mapeo de meses para conversión
        self.meses_es = {
            'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04', 
            'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08', 
            'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12',
            'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04', 
            'may': '05', 'jun': '06', 'jul': '07', 'ago': '08', 
            'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12',
            # Meses en inglés
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08', 
            'september': '09', 'october': '10', 'november': '11', 'december': '12',
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 
            'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09', 
            'oct': '10', 'nov': '11', 'dec': '12'
        }
        
        # Patrones para montos
        self.patrones_monto = [
            r'(?:total|importe|monto|suma|amount|total amount|due|balance)?\s*(?:\$|€|£|usd|eur|mxn)?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2}))',
            r'(?:total|importe|monto|suma|amount|total amount|due|balance)?\s*(?:\$|€|£|usd|eur|mxn)?\s*(\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2}))',
            r'(?:total|importe|monto|suma|amount|total amount|due|balance|a pagar|to pay)\s*(?:[\w\s:]*?)\s*(?:\$|€|£|usd|eur|mxn)?\s*(\d+(?:[,.]\d+)?)',
            r'(?:\$|€|£|usd|eur|mxn)\s*(\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?)'
        ]

    def extract_fields(self, text_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extrae campos de una lista de bloques de texto.
        
        Args:
            text_blocks (List[Dict[str, Any]]): Lista de bloques de texto con confianza
        
        Returns:
            Dict[str, Any]: Diccionario de campos extraídos
        """
        # Validar entrada
        if text_blocks is None:
            raise ValueError("text_blocks no puede ser None")
        if not isinstance(text_blocks, list):
            raise ValueError("text_blocks debe ser una lista")
        
        # Si no hay bloques o están vacíos, devolver diccionario vacío
        if not text_blocks or (len(text_blocks) == 1 and not text_blocks[0].get('text', '').strip()):
            return {}
        
        # Diccionario para almacenar campos extraídos
        fields = {}
        
        # Revisar cada bloque de texto
        for block in text_blocks:
            texto = block['text']
            
            # Intentar extraer fecha
            fecha = self._extract_date([block], texto)
            if fecha:
                # Verificar si es una fecha de emisión o vencimiento
                if 'fecha_expedicion' not in fields:
                    fields['fecha_expedicion'] = fecha
                elif 'fecha_vencimiento' not in fields:
                    fields['fecha_vencimiento'] = fecha
        
        # Si no se encontró ninguna fecha, intentar con texto combinado
        if not fields:
            text_combined = ' '.join(block['text'] for block in text_blocks)
            fecha = self._extract_date(text_blocks, text_combined)
            if fecha:
                fields['fecha_expedicion'] = fecha
        
        # Extraer total
        text_combined = ' '.join(block['text'] for block in text_blocks)
        total = self._extract_amount(text_blocks, text_combined)
        if total:
            fields['total'] = total
        
        return fields

    def _extract_date(self, text_blocks: List[Dict[str, Any]], text_combined: str) -> Optional[str]:
        """
        Extrae fechas de los bloques de texto.
        """
        # Buscar primero en bloques individuales
        for block in text_blocks:
            texto = block['text'].lower()
            
            # Verificar si hay palabras clave de fecha
            if any(palabra in texto for palabra in self.palabras_clave_fecha):
                for patron in self.patrones_fecha:
                    matches = re.findall(patron, texto, re.IGNORECASE)
                    if matches:
                        # Tomar el primer match
                        for match in matches:
                            # Normalizar componentes de la fecha
                            components = [comp.strip() for comp in match if comp]
                            
                            if len(components) == 3:
                                # Determinar orden de los componentes
                                if len(components[0]) == 4 and components[0].isdigit():
                                    # Formato YYYY-MM-DD
                                    year, month, day = components
                                else:
                                    # Formato DD-MM-YYYY o MM-DD-YYYY
                                    if len(components[2]) == 4:
                                        day, month, year = components
                                    else:
                                        day, month, year = components
                                
                                # Convertir mes si es textual
                                if not month.isdigit():
                                    month = self.meses_es.get(month.lower(), '01')
                                
                                # Ajustar año si es de dos dígitos
                                if len(year) == 2:
                                    year = '20' + year if int(year) < 50 else '19' + year
                                
                                # Formatear fecha
                                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Si no se encuentra en bloques individuales, buscar en texto combinado
        for patron in self.patrones_fecha:
            matches = re.findall(patron, text_combined, re.IGNORECASE)
            if matches:
                for match in matches:
                    # Similar al procesamiento anterior
                    components = [comp.strip() for comp in match if comp]
                    
                    if len(components) == 3:
                        # Lógica de procesamiento igual a la anterior
                        if len(components[0]) == 4 and components[0].isdigit():
                            year, month, day = components
                        else:
                            if len(components[2]) == 4:
                                day, month, year = components
                            else:
                                day, month, year = components
                        
                        # Convertir mes si es textual
                        if not month.isdigit():
                            month = self.meses_es.get(month.lower(), '01')
                        
                        # Ajustar año si es de dos dígitos
                        if len(year) == 2:
                            year = '20' + year if int(year) < 50 else '19' + year
                        
                        # Formatear fecha
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None

    # Los métodos _extract_amount y _standardize_amount permanecen igual
    def _extract_amount(self, text_blocks: List[Dict[str, Any]], text_combined: str) -> Optional[str]:
        """
        Extrae montos totales de los bloques de texto.
        """
        # Palabras clave para totales
        palabras_clave_total = [
            'total', 'importe', 'monto', 'suma', 'a pagar', 'valor total'
        ]
        
        # Buscar en bloques individuales primero
        for block in text_blocks:
            text = block['text'].lower()
            if any(palabra in text for palabra in palabras_clave_total):
                for patron in self.patrones_monto:
                    matches = re.findall(patron, text, re.IGNORECASE)
                    if matches:
                        # Tomar el primer match
                        total_estandarizado = self._standardize_amount(matches[0])
                        if total_estandarizado:
                            return total_estandarizado
        
        # Si no se encuentra, buscar en texto combinado
        for patron in self.patrones_monto:
            matches = re.findall(patron, text_combined, re.IGNORECASE)
            if matches:
                # Tomar el primer match
                total_estandarizado = self._standardize_amount(matches[0])
                if total_estandarizado:
                    return total_estandarizado
        
        return None

    def _standardize_amount(self, amount_str: str) -> Optional[str]:
        """
        Estandariza un monto a formato numérico.
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
            return f"{amount:.2f}"
        except ValueError:
            return None

    def process_document(self, image_path: str) -> Dict[str, Any]:
        """
        Procesa un documento completo utilizando OCR y extracción de características.
        
        Args:
            image_path (str): Ruta del archivo de imagen a procesar
        
        Returns:
            Dict: Resultado del procesamiento con campos extraídos y validación
        """
        try:
            # Importaciones locales para evitar dependencias circulares
            from src.ocr.ocr_engine import OCREngine
            from src.preprocessing.image_processor import ImageProcessor
            from src.validation.data_cleaner import DataCleaner
            from src.validation.field_validator import FieldValidator

            # Inicializar componentes
            ocr_engine = OCREngine()
            image_processor = ImageProcessor()
            data_cleaner = DataCleaner()
            field_validator = FieldValidator()

            # Leer y procesar la imagen
            image = cv2.imread(image_path)
            
            # Validar que la imagen se haya cargado correctamente
            if image is None:
                return {
                    'success': False,
                    'error': 'No se pudo cargar la imagen',
                    'raw_text': ''
                }
            
            # Preprocesar imagen
            processed_image = image_processor.process(image)
            
            # Extraer información con OCR
            ocr_result = ocr_engine.process_image(processed_image)
            
            # Manejar errores de OCR
            if 'error' in ocr_result:
                return {
                    'success': False,
                    'error': ocr_result.get('error', 'Error en procesamiento OCR'),
                    'raw_text': ocr_result.get('raw_text', '')
                }
            
            # Obtener campos extraídos
            extracted_fields = ocr_result.get('fields', {})
            
            # Si no se extrajeron campos, intentar con imagen original
            if not extracted_fields:
                ocr_result = ocr_engine.process_image(image)
                extracted_fields = ocr_result.get('fields', {})
            
            # Si aún no hay campos, devolver error
            if not extracted_fields:
                return {
                    'success': False,
                    'error': 'No se pudieron extraer campos del documento',
                    'raw_text': ocr_result.get('raw_text', '')
                }
            
            # Limpiar campos extraídos
            try:
                cleaned_fields = data_cleaner.clean_document_data(extracted_fields)
            except Exception as e:
                logging.error(f"Error limpiando datos: {str(e)}")
                cleaned_fields = extracted_fields
            
            # Validar campos
            validation_result = field_validator.validate_fields(cleaned_fields)
            
            # Preparar resultado final
            return {
                'success': True,
                'extracted_fields': cleaned_fields,
                'validation': validation_result,
                'raw_text': ocr_result.get('raw_text', ''),
                'raw_results': ocr_result.get('raw_results', []),
                'confidence': ocr_result.get('confidence', 0),
                'date_details': ocr_result.get('date_details', []),
                'total_details': ocr_result.get('total_details', [])
            }
        
        except Exception as e:
            logging.error(f"Error procesando documento: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }