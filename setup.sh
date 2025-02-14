#!/bin/bash

echo "================================"
echo "Instalando Proyecto OCR"
echo "================================"

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python no está instalado"
    echo "Por favor, instale Python 3.8 o superior"
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

echo "Instalando dependencias..."
uv pip install -r requirements.txt

echo "================================"
echo "Instalación completada!"
echo "Para activar el entorno virtual: source .venv/bin/activate"
echo "Para ejecutar la aplicación: streamlit run web_app/app.py"
echo "================================"