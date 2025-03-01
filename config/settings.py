# config/settings.py
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuraciones generales
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')



# Configuraciones de archivos
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'pdf']
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Configuraciones de EasyOCR
OCR_LANGUAGES = ['es', 'en']  # Español e Inglés
OCR_GPU = False  # Cambiar a True si se dispone de GPU
OCR_MODEL_STORAGE = os.path.join(PROJECT_ROOT, 'models')

# Configuraciones de procesamiento de imágenes
IMAGE_MIN_SIZE = 800  # Tamaño mínimo del lado más corto
IMAGE_MAX_SIZE = 2400  # Tamaño máximo del lado más largo
IMAGE_QUALITY = 90  # Calidad de imagen procesada (0-100)

# Asegurarse de que los directorios existan
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(OCR_MODEL_STORAGE, exist_ok=True)

# Configuraciones de la aplicación web
STREAMLIT_TITLE = "Sistema de Procesamiento de Documentos"
STREAMLIT_DESCRIPTION = """
Sistema de procesamiento automático de documentos basado en EasyOCR 
para la digitalización y extracción estructurada de información de facturas y recibos.
"""

# Configuraciones de validación
CONFIDENCE_THRESHOLD = 0.50  # Umbral de confianza para la extracción de texto

# Formatos de fecha encontrados en las facturas
DATE_FORMATS = [
    '%d-%b-%Y',    # 18-Abr-2024
    '%d-%b-%y',    # 18-Abr-24
    '%d-%B-%Y',    # 18-Abril-2024
    '%d/%b/%Y',    # 18/Abr/2024
    '%d/%B/%Y',    # 18/Abril/2024
    '%Y-%m-%d',    # 2024-04-18
    '%d/%m/%Y',    # 18/04/2024
    '%m/%d/%Y',    # 04/18/2024
    '%d-%m-%Y',    # 18-04-2024
    '%Y/%m/%d',    # 2024/04/18
    '%d-%b-%Y',
]

# Patrones de expresiones regulares para validación
# Eliminar la configuración de tipos de documentos y reemplazarla con:

# Patrones principales para la extracción
PATTERNS = {
    # Patrones de fechas mejorados
    'date': r'(?:\d{1,2}-[A-Za-z]{3}-\d{2,4}|\d{1,2}/[A-Za-z]{3}/\d{2,4}|\d{4}-\d{1,2}-\d{1,2}|\d{1,2}[A-Za-z]{3}\'\d{2}|\d{1,2}/\d{1,2}/\d{2,4})',
    
    # Patrón para totales
    'amount': r'(?:total|balance|due|importe)?\s*(?:\$|€|£)?\s*\d{1,3}(?:[,.]\d{3})*(?:[,.]\d{2})?',
    
    # Patrón para identificadores
    'id': r'\b(?:ID|VAT|NIT|RUT|RFC|No\.|Number)?\s*:?\s*([A-Z0-9][\dA-Z-]{5,})\b',
}

# Palabras clave para fechas
DATE_KEYWORDS = [
    # Español
    'fecha', 'emisión', 'expedición', 'generada',
    # Inglés
    'date', 'issued', 'generated'
]

# Palabras clave para totales
TOTAL_KEYWORDS = [
    # Español
    'total', 'importe', 'monto', 'pagar', 'balance', 'suma',
    # Inglés
    'total', 'amount', 'due', 'balance', 'pay'
]

# Configuraciones de exportación
EXPORT_FORMATS = ['json', 'csv']
DEFAULT_EXPORT_FORMAT = 'json'

# Configuraciones de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(PROJECT_ROOT, 'logs', 'app.log')

# Asegurarse de que el directorio de logs exista
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Mensajes de error personalizados
ERROR_MESSAGES = {
    'file_type': 'Tipo de archivo no permitido. Use: {}'.format(', '.join(ALLOWED_EXTENSIONS)),
    'file_size': f'Tamaño de archivo excede el límite de {MAX_FILE_SIZE/1024/1024}MB',
    'ocr_failed': 'Error en el procesamiento OCR. Intente con una imagen más clara.',
    'validation_failed': 'El documento no cumple con los criterios de validación requeridos.',
    'missing_fields': 'Campos requeridos faltantes: {}',
}