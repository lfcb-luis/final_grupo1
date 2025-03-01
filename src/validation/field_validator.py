# src/validation/field_validator.py
import re
from datetime import datetime
import logging
from typing import Dict, Union, List
from config.settings import DATE_FORMATS, PATTERNS

class FieldValidator:
    """Clase para validar los campos extraídos del OCR."""
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """
        Valida que una fecha tenga un formato válido.
        
        Args:
            date_str (str): String de fecha a validar
            
        Returns:
            bool: True si la fecha es válida
        """
        for date_format in DATE_FORMATS:
            try:
                datetime.strptime(date_str, date_format)
                return True
            except ValueError:
                continue
        return False

    @staticmethod
    def validate_amount(amount_str: str) -> bool:
        """
        Valida que un monto tenga el formato correcto.
        
        Args:
            amount_str (str): String de monto a validar
            
        Returns:
            bool: True si el monto es válido
        """
        # Eliminar símbolos de moneda y espacios
        amount_str = str(amount_str).replace('$', '').replace(' ', '')
        
        # Verificar formato con comas y decimales opcionales
        pattern = r'^\d{1,3}(,\d{3})*(\.\d{1,2})?$'
        return bool(re.match(pattern, amount_str))

    @staticmethod
    def validate_matricula(matricula: str) -> bool:
        """
        Valida que una matrícula tenga el formato correcto.
        
        Args:
            matricula (str): Matrícula a validar
            
        Returns:
            bool: True si la matrícula es válida
        """
        # Usar un patrón genérico si no se especifica en PATTERNS
        matricula_pattern = PATTERNS.get('matricula', r'^[A-Z0-9-]+$')
        return bool(re.match(matricula_pattern, str(matricula)))

    def validate_fields(self, fields: Dict) -> Dict[str, Union[bool, List[str]]]:
        """
        Valida todos los campos extraídos.
        
        Args:
            fields (Dict): Campos extraídos
            
        Returns:
            Dict: Resultado de la validación con errores si existen
        """
        validation_result = {
            'is_valid': True,
            'errors': []
        }

        # Campos que esperamos encontrar, pero no como requeridos
        optional_fields = ['fecha_expedicion', 'fecha_vencimiento', 'total']

        # Validar cada campo si está presente
        for field in optional_fields:
            if field in fields:
                if 'fecha' in field:
                    if not self.validate_date(fields[field]):
                        validation_result['is_valid'] = False
                        validation_result['errors'].append(f"Formato de fecha inválido: {field}")

                elif field == 'total':
                    # Convertir a string por si acaso ya es un número
                    total_str = str(fields[field])
                    if not self.validate_amount(total_str):
                        validation_result['is_valid'] = False
                        validation_result['errors'].append(f"Formato de monto inválido: {field}")

        return validation_result

    def clean_amount(self, amount_str: str) -> float:
        """
        Limpia y convierte un monto a formato numérico.
        
        Args:
            amount_str (str): String de monto a limpiar
            
        Returns:
            float: Monto en formato numérico
        """
        try:
            # Eliminar símbolos de moneda y espacios
            amount_str = str(amount_str).replace('$', '').replace(' ', '')
            # Eliminar comas
            amount_str = amount_str.replace(',', '')
            return float(amount_str)
        except ValueError as e:
            logging.error(f"Error al convertir monto: {str(e)}")
            raise

    def clean_date(self, date_str: str) -> str:
        """
        Estandariza el formato de fecha.
        
        Args:
            date_str (str): String de fecha a estandarizar
            
        Returns:
            str: Fecha en formato estándar YYYY-MM-DD
        """
        for date_format in DATE_FORMATS:
            try:
                date_obj = datetime.strptime(date_str, date_format)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        raise ValueError(f"Formato de fecha no reconocido: {date_str}")