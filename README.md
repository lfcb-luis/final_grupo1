# Proyecto OCR - Procesamiento de Documentos

## Requisitos previos
- Python 3.8 o superior
- UV (Astral) instalado

## Instalación

### Windows
1. Doble clic en `setup.bat`
   o ejecutar en terminal:
```bash
setup.bat
```
### Linux/Mac
1. Abrir terminal en el directorio del proyecto 
2. Dar permisos de ejecución al script: 
```bash
chmod +x setup.sh
```
3. Ejecutar el script
```bash
./setup.sh
```

## Ejecutar el Proyecto
1. Activar el entorno virtual: 
◦ Windows: .venv\Scripts\activate 
◦ Linux/Mac: source .venv/bin/activate 
2. Ejecutar la aplicación:
```bash
streamlit run web_app/app.py
```
## Estructura del Proyecto
proyecto_ocr/
├── data/                  # Datos y documentos
│   ├── raw/              # Documentos originales
│   ├── processed/        # Documentos procesados
│   └── external/         # Datos externos
├── notebooks/            # Jupyter notebooks
├── src/                  # Código fuente
├── tests/               # Pruebas unitarias
├── web_app/             # Aplicación web
└── docs/                # Documentación

## Funcionalidades Principales
• Carga y procesamiento de imágenes de documentos 
• Extracción de texto mediante EasyOCR 
• Validación automática de campos 
• Interfaz web intuitiva con Streamlit 
• Exportación de datos en formatos JSON y CSV 

## Documentación
Para más información, consulte la documentación en la carpeta docs/:
• Guía de Instalación 
• Manual de Usuario 
• Documentación API


