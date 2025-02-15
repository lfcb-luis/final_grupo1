# src/utils/helpers.py
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
import json
import csv
from pathlib import Path
from config.settings import (
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    ALLOWED_EXTENSIONS,
    ERROR_MESSAGES
)

class FileHandler:
    """Clase para manejar operaciones con archivos."""

    @staticmethod
    def save_raw_file(file_data: bytes, filename: str) -> str:
        """
        Guarda un archivo original en el directorio de datos crudos.
        
        Args:
            file_data (bytes): Datos del archivo
            filename (str): Nombre del archivo
            
        Returns:
            str: Ruta donde se guardó el archivo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        output_path = os.path.join(RAW_DATA_DIR, safe_filename)
        
        try:
            with open(output_path, 'wb') as f:
                f.write(file_data)
            logging.info(f"Archivo original guardado en: {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Error guardando archivo original: {str(e)}")
            raise

    @staticmethod
    def get_raw_file_path(filename: str) -> str:
        """
        Obtiene la ruta completa de un archivo original.
        
        Args:
            filename (str): Nombre del archivo
            
        Returns:
            str: Ruta completa del archivo
        """
        return os.path.join(RAW_DATA_DIR, filename)
    
    @staticmethod
    def is_valid_extension(filename: str) -> bool:
        """
        Verifica si la extensión del archivo es válida.
        
        Args:
            filename (str): Nombre del archivo
            
        Returns:
            bool: True si la extensión está permitida
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def create_output_filename(base_name: str, suffix: str, extension: str) -> str:
        """
        Crea un nombre de archivo único para la salida.
        
        Args:
            base_name (str): Nombre base del archivo
            suffix (str): Sufijo a añadir
            extension (str): Extensión del archivo
            
        Returns:
            str: Nombre de archivo único
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{suffix}_{timestamp}.{extension}"

    @staticmethod
    def ensure_directory_exists(directory: str):
        """
        Asegura que un directorio exista, lo crea si no existe.
        
        Args:
            directory (str): Ruta del directorio
        """
        Path(directory).mkdir(parents=True, exist_ok=True)

class ResultsExporter:
    """Clase para exportar resultados en diferentes formatos."""
    
    def __init__(self):
        """Inicializa el exportador de resultados."""
        self.file_handler = FileHandler()

    def export_to_json(self, data: Dict[str, Any], filename: str) -> str:
        """
        Exporta los resultados a un archivo JSON.
        
        Args:
            data (Dict[str, Any]): Datos a exportar
            filename (str): Nombre base del archivo
            
        Returns:
            str: Ruta del archivo generado
        """
        output_path = os.path.join(
            PROCESSED_DATA_DIR,
            self.file_handler.create_output_filename(filename, "results", "json")
        )
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return output_path
        except Exception as e:
            logging.error(f"Error exportando a JSON: {str(e)}")
            raise

    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Exporta los resultados a un archivo CSV.
        
        Args:
            data (List[Dict[str, Any]]): Lista de datos a exportar
            filename (str): Nombre base del archivo
            
        Returns:
            str: Ruta del archivo generado
        """
        output_path = os.path.join(
            PROCESSED_DATA_DIR,
            self.file_handler.create_output_filename(filename, "results", "csv")
        )
        
        try:
            if not data:
                raise ValueError("No hay datos para exportar")
                
            fieldnames = data[0].keys()
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return output_path
        except Exception as e:
            logging.error(f"Error exportando a CSV: {str(e)}")
            raise

class Logger:
    """Clase para manejar el logging de la aplicación."""
    
    @staticmethod
    def setup_logger(name: str, log_file: str, level=logging.INFO):
        """
        Configura un logger personalizado.
        
        Args:
            name (str): Nombre del logger
            log_file (str): Ruta del archivo de log
            level: Nivel de logging
        """
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'
        )
        
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        
        return logger

class ErrorHandler:
    """Clase para manejar errores de la aplicación."""
    
    @staticmethod
    def get_error_message(error_key: str, **kwargs) -> str:
        """
        Obtiene un mensaje de error formateado.
        
        Args:
            error_key (str): Clave del error
            **kwargs: Argumentos para formatear el mensaje
            
        Returns:
            str: Mensaje de error formateado
        """
        if error_key in ERROR_MESSAGES:
            return ERROR_MESSAGES[error_key].format(**kwargs)
        return "Error desconocido"