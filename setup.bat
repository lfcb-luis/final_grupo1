@echo off
echo ================================
echo Instalando Proyecto OCR
echo ================================

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no está instalado
    echo Por favor, instale Python 3.8 o superior
    exit /b 1
)

:: Verificar si UV está instalado
uv --version >nul 2>&1
if errorlevel 1 (
    echo Error: UV no está instalado
    echo Por favor, instale UV usando: pip install uv
    exit /b 1
)

echo Creando entorno virtual...
uv venv .venv

echo Activando entorno virtual...
call .venv\Scripts\activate

echo Instalando dependencias...
uv pip install -r requirements.txt

echo ================================
echo Instalación completada!
echo Para activar el entorno virtual: .venv\Scripts\activate
echo Para ejecutar la aplicación: streamlit run web_app/app.py
echo ================================