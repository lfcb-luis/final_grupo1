# src/validation/data_cleaner.py
import re
from typing import Dict, Any
import logging
from datetime import datetime
from config.settings import DATE_FORMATS

class DataCleaner:
    """Clase para limpiar y estandarizar los datos extraídos."""
    
    @staticmethod
    def clean_amount(amount: str) -> float:
        """
        Limpia y convierte un monto a formato numérico.
        
        Args:
            amount (str): String del monto (ej: '$8,640' o '35,643')
            
        Returns:
            float: Monto numérico
        """
        try:
            # Eliminar símbolos de moneda y espacios
            cleaned = amount.replace('$', '').replace(' ', '')
            # Eliminar comas
            cleaned = cleaned.replace(',', '')
            # Convertir a float
            return float(cleaned)
        except ValueError as e:
            logging.error(f"Error al limpiar monto '{amount}': {str(e)}")
            raise

    @staticmethod
    def clean_date(date_str: str) -> str:
        """
        Estandariza el formato de fecha.
        
        Args:
            date_str (str): String de fecha (ej: '18-Abr-2024' o '17/MAY/2024')
            
        Returns:
            str: Fecha en formato YYYY-MM-DD
        """
        for date_format in DATE_FORMATS:
            try:
                date_obj = datetime.strptime(date_str, date_format)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        raise ValueError(f"Formato de fecha no reconocido: {date_str}")

    @staticmethod
    def clean_matricula(matricula: str) -> str:
        """
        Limpia y estandariza el número de matrícula.
        
        Args:
            matricula (str): Número de matrícula
            
        Returns:
            str: Matrícula limpia
        """
        # Eliminar espacios y caracteres especiales
        return re.sub(r'[^0-9]', '', matricula)

    def clean_document_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Limpia todos los campos del documento.
        
        Args:
            data (Dict[str, Any]): Datos extraídos del documento
            
        Returns:
            Dict[str, Any]: Datos limpios y estandarizados
        """
        cleaned_data = {}
        
        try:
            for key, value in data.items():
                if value is None:
                    continue
                    
                if 'total' in key.lower():
                    cleaned_data[key] = self.clean_amount(value)
                elif any(date_word in key.lower() for date_word in ['fecha', 'date']):
                    cleaned_data[key] = self.clean_date(value)
                elif 'matricula' in key.lower():
                    cleaned_data[key] = self.clean_matricula(value)
                else:
                    cleaned_data[key] = value.strip() if isinstance(value, str) else value
                    
            return cleaned_data
            
        except Exception as e:
            logging.error(f"Error al limpiar datos: {str(e)}")
            raise

    def standardize_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estandariza las claves del diccionario.
        
        Args:
            data (Dict[str, Any]): Datos con claves originales
            
        Returns:
            Dict[str, Any]: Datos con claves estandarizadas
        """
        key_mapping = {
            'fecha_factura': ['fecha de la factura', 'fecha factura', 'fecha_emision'],
            'fecha_vencimiento': ['fecha limite sin recargo', 'fecha_limite', 'tengo plazo para pagar hasta'],
            'total': ['total a pagar', 'total', 'importe_total'],
            'matricula': ['matricula', 'numero_cliente', 'id_cliente']
        }
        
        standardized_data = {}
        
        for std_key, variants in key_mapping.items():
            for variant in variants:
                if variant in data:
                    standardized_data[std_key] = data[variant]
                    break
                    
        return standardized_data