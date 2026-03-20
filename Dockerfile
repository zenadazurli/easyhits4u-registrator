FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice
COPY app.py .

# Crea directory per output
RUN mkdir -p /tmp/easyhits4u

# Esegui lo script
CMD ["python", "app.py"]