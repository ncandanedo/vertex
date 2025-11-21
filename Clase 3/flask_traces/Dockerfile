# Usar imagen oficial ligera de Python
FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y habilitar logs en stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# --- NUEVO BLOQUE: Instalar dependencias del sistema ---
# google-cloud-profiler necesita g++ para compilarse
RUN apt-get update && apt-get install -y \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
# -------------------------------------------------------

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Cloud Run inyecta la variable PORT (por defecto 8080)
ENV PORT=8080

# Comando para ejecutar la aplicación con Gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app