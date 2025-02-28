# src/features/feature_extractor.py
import re
import logging
from typing import List, Dict, Any, Optional
from config.settings import CONFIDENCE_THRESHOLD

class FeatureExtractor:
    def __init__(self):
        """Inicializa los patrones de extracción para campos comunes en cualquier factura."""
        # Patrones base que deberían funcionar en cualquier factura
        self.patrones_base = {
            #'identificacion': r'(?:Nro\.? (?:de )?(?:identificación|documento)|ID|NIT|MATRÍCULA|código)[\s:>>]*([A-Z0-9-]+)',
            'identificacion': r'(?:Nro\.?\s*(?:de\s*)?)?\b\w*(?:NIT|ID|MATRÍCULA|código|identificación|documento)\w*\b[\s:>>]*([A-Z0-9-]+)', #Modificación del patron para permitir matches parciales
            
            'fecha_expedicion': (
                r'(?:generada|expedida|emisión|emitido|fecha)(?:\s+(?:de|el))?\s*'
                r'(?:expedición|emisión|generación)?[:\s]*'
                r'(\d{1,2}[-/\s][A-Za-z]{3,10}[-/\s]\d{4}|\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})'
            ),
            
            'fecha_vencimiento': (
                r'(?:vence|vencimiento|pagar hasta|límite|plazo|si no pagas antes de|fecha de pago oportuno)[:\s]*(\d{1,2}\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{4}(?:-\d{4})?)'
            ),

            
            'total': r'(?:total|valor total|total a pagar|valor a pagar|pago total)[:\s]*\$?\s*([\d,.]+)',
        }
        
        # Patrones adicionales específicos por tipo de documento
        self.patrones_especificos = {
            'gas': {
                'consumo': r'consumo[:\s]*(\d+)',
                'lectura_actual': r'lectura actual[:\s]*(\d+)',
            },
            'luz': {
                'energia': r'energía[:\s]*\$?\s*([\d,.]+)',
                'alumbrado': r'alumbrado[:\s]*\$?\s*([\d,.]+)',
            },
            # Se pueden agregar más tipos de facturas
        }

    def extract_fields(self, text_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self._validate_input(text_blocks):
            return {}

        fields = {}
        text_combined = self._get_combined_text(text_blocks)

        # Procesar cada bloque individualmente para fechas
        for block in text_blocks:
            text = block['text']
            # Buscar fecha de expedición
            if re.search(r'(?:generada|expedida|emisión)', text, re.IGNORECASE):
                match = re.search(self.patrones_base['fecha_expedicion'], text, re.IGNORECASE)
                if match:
                    fields['fecha_expedicion'] = self._clean_value(match.group(1), 'fecha')

        # Procesar texto combinado para otros campos
        for campo, patron in self.patrones_base.items():
            if campo not in fields:  # No sobrescribir fechas ya encontradas
                match = re.search(patron, text_combined, re.IGNORECASE)
                if match:
                    fields[campo] = self._clean_value(match.group(1), campo)

        return fields

    def _validate_input(self, text_blocks: List[Dict[str, Any]]) -> bool:
        """Valida la entrada de texto."""
        if text_blocks is None:
            raise ValueError("text_blocks no puede ser None")
        if not isinstance(text_blocks, list):
            raise ValueError("text_blocks debe ser una lista")
        return bool(text_blocks)

    def _get_combined_text(self, text_blocks: List[Dict[str, Any]]) -> str:
        """Combina los bloques de texto con confianza suficiente."""
        return ' '.join(
            block['text'] for block in text_blocks 
            if block.get('confidence', 0) >= CONFIDENCE_THRESHOLD
        )

    def _clean_value(self, value: str, field_type: str) -> str:
        """Limpia y formatea el valor según el tipo de campo."""
        value = value.strip()
        
        """Remover total de la función clean_values para preservar el formato de la moneda."""
        
        if field_type in ['energia', 'alumbrado']:
            # Eliminar símbolos de moneda, comas y puntos
            cleaned = re.sub(r'[^\d]', '', value)  # Elimina todo excepto dígitos 
            return cleaned
            
        elif field_type.startswith('fecha'):
            # Estandarizar formato de fecha
            value = value.replace('/', '-')
            # Convertir nombres de meses completos a abreviados
            for mes_completo, mes_abrev in [
                ('Mayo', 'MAY'), ('Junio', 'JUN'), ('Julio', 'JUL'),
                ('Enero', 'ENE'), ('Febrero', 'FEB'), ('Marzo', 'MAR'),
                ('Abril', 'ABR'), ('Agosto', 'AGO'), ('Septiembre', 'SEP'),
                ('Octubre', 'OCT'), ('Noviembre', 'NOV'), ('Diciembre', 'DIC')
            ]:
                value = value.replace(mes_completo, mes_abrev)
            return value
            
        return value

    def _detect_document_type(self, text: str) -> Optional[str]:
        """Detecta el tipo de documento basado en palabras clave."""
        text_lower = text.lower()
        keywords = {
            'gas': ['gas natural', 'consumo de gas', 'efigas'],
            'luz': ['energía eléctrica', 'consumo de energía', 'alumbrado'],
            'agua': ['acueducto', 'consumo de agua', 'alcantarillado'],
            'telefono': ['plan móvil', 'telefonía', 'minutos', 'telecomunicaciones'],
            'internet': ['megabytes', 'fibra óptica', 'banda ancha', 'telecomunicaciones']
        }
        
        for doc_type, words in keywords.items():
            if any(word in text_lower for word in words):
                return doc_type
        return None