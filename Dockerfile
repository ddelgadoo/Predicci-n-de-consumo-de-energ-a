FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto completo
COPY src .

# Copiar mlruns con el modelo entrenado
COPY mlruns/ mlruns/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
