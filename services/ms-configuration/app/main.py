"""
Microservicio de **configuración** (placeholder): parámetros globales o por tenant.

Solo ``/health`` mientras se define el dominio de configuración.
"""
from fastapi import FastAPI

app = FastAPI(
    title="Configuration Service",
    description="Parámetros y feature flags (en expansión).",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}