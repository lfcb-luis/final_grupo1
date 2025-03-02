FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema (incluye lo necesario para OpenCV)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar primero solo los archivos de requisitos para aprovechar el caché de Docker
COPY requirements.txt setup.py ./

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Instalar el paquete en modo desarrollo
RUN pip install -e .

# Puerto para Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación de Streamlit
CMD ["streamlit", "run", "web_app/app.py"]