FROM python:3.11

WORKDIR /app

# 🔹 copiar requirements primero
COPY requirements.txt .

# 🔹 instalar dependencias (aquí entra psycopg2)
RUN pip install --no-cache-dir -r requirements.txt

# 🔹 copiar el resto del código
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]