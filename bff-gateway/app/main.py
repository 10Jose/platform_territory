from fastapi import FastAPI
import requests
import uuid
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)

TRANSFORMATION_URL = "http://ms-transformation:8001/health"

@app.get("/health")
def health():
    trace_id = str(uuid.uuid4())

    try:
        response = requests.get(TRANSFORMATION_URL)
        transformation_status = response.json()
    except Exception:
        transformation_status = "error"

    logging.info(f"BFF health - {trace_id}")

    return {
        "service": "bff-gateway",
        "status": "ok",
        "trace_id": trace_id,
        "transformation_check": transformation_status
    }