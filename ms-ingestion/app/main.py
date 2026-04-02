from fastapi import FastAPI
import uuid
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)

@app.get("/health")
def health():
    trace_id = str(uuid.uuid4())
    logging.info(f"Health check - {trace_id}")
    return {
        "service": "ingestion",
        "status": "ok",
        "trace_id": trace_id
    }