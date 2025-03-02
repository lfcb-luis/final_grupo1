# Proyecto OCR - Procesamiento de Documentos

## Requisitos previos
- Python 3.9 o superior
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

## Pruebas
El proyecto incluye un conjunto de pruebas automatizadas para verificar el funcionamiento del extractor de características de facturas.

### Requisitos para las pruebas
- Entorno virtual activado
- Dependencias instaladas (ver sección de Instalación)
- pytest instalado (incluido en requirements.txt)

### Ejecutar las pruebas
Puede ejecutar las pruebas de diferentes maneras:

1. **Ejecutar todas las pruebas**
```bash
pytest -v
```

2. Ejecutar pruebas específicas
# Pruebas del extractor de características
```bash
pytest tests/test_features_extractor.py -v
```

# Pruebas de preprocesamiento de imágenes
```bash
pytest tests/test_preprocessing.py -v
```

3. Ver detalles de las pruebas
```bash
pytest -v --full-trace  # Muestra trazas completas de errores
```

### Conjunto de pruebas
El proyecto incluye pruebas para:

#### Campos comunes

* Identificación/matrícula 
* Fechas de expedición y vencimiento
* Totales y subtotales
* Validación de formatos


#### Manejo de errores

* Datos con baja confianza
* Entradas inválidas
* Campos vacíos


#### Flexibilidad de formatos

* Diferentes formatos de fecha
* Diferentes formatos de montos
* Diferentes tipos de identificadores



