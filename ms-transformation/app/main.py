from fastapi import FastAPI
import requests
import uuid
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)

INGESTION_URL = "http://ms-ingestion:8000/health"

@app.get("/health")
def health():
    trace_id = str(uuid.uuid4())

    try:
        response = requests.get(INGESTION_URL)
        ingestion_status = response.json()  # ← CORRECTO (con paréntesis)
    except:
        ingestion_status = "error"

    logging.info(f"Transformation health - {trace_id}")

    return {
        "service": "transformation",
        "status": "ok",
        "trace_id": trace_id,
        "ingestion_check": ingestion_status
    }