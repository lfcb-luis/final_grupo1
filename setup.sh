#!/bin/bash

echo "================================"
echo "Instalando Proyecto OCR"
echo "================================"

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python no está instalado"
    echo "Por favor, instale Python 3.9 o superior"
    exit 1
fi

# Verificar versión de Python
python3 -c "import sys; ver = sys.version_info; exit(0 if ver.major == 3 and ver.minor >= 9 else 1)"
if [ $? -ne 0 ]; then
    echo "Error: Se requiere Python 3.9 o superior"
    echo "Versión actual:"
    python3 --version
    exit 1
fi

# Verificar si UV está instalado
if ! command -v uv &> /dev/null; then
    echo "Error: UV no está instalado"
    echo "Por favor, instale UV usando: pip install uv"
    exit 1
fi

echo "Creando entorno virtual..."
uv venv .venv

echo "Activando entorno virtual..."
source .venv/bin/activate

# Preguntar por instalación con GPU
read -p "¿Desea instalar con soporte para GPU? (s/N): " gpu_support
if [[ $gpu_support =~ ^[Ss]$ ]]; then
    echo "Instalando dependencias completas con soporte GPU..."
    uv pip install -r requirements-full.txt
else
    echo "Instalando dependencias básicas..."
    uv pip install -r requirements.txt
fi

# En setup.sh, añadir después de instalar dependencias:
echo "Instalando proyecto en modo desarrollo..."
uv pip install -e .

echo "================================"
echo "Instalación completada!"
echo "Para activar el entorno virtual: source .venv/bin/activate"
echo "Para ejecutar la aplicación: streamlit run web_app/app.py"
echo "================================"