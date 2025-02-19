@echo off
echo ================================
echo Instalando Proyecto OCR
echo ================================

:: Verificar si Python está instalado y es versión 3.9+
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no está instalado
    echo Por favor, instale Python 3.9 o superior
    exit /b 1
)

python -c "import sys; ver = sys.version_info; exit(0 if ver.major == 3 and ver.minor >= 9 else 1)"
if errorlevel 1 (
    echo Error: Se requiere Python 3.9 o superior
    echo Version actual:
    python --version
    exit /b 1
)

:: Verificar UV
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

:: Preguntar por instalación con GPU
set /p gpu_support="¿Desea instalar con soporte para GPU? (S/N): "
if /i "%gpu_support%"=="S" (
    echo Instalando dependencias completas con soporte GPU...
    uv pip install -r requirements-full.txt
) else (
    echo Instalando dependencias básicas...
    uv pip install -r requirements.txt
)

echo Instalando proyecto en modo desarrollo...
uv pip install -e .

echo ================================
echo Instalación completada!
echo Para activar el entorno virtual: .venv\Scripts\activate
echo Para ejecutar la aplicación: streamlit run web_app/app.py
echo ================================