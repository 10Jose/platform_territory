<<<<<<< HEAD
from fastapi import FastAPI

app = FastAPI(title="Nombre del Microservicio")
=======
"""
Microservicio **ML** (placeholder): reservado para modelos de machine learning sobre datos ya transformados.

Expone solo ``/health`` hasta integrar entrenamiento o inferencia.
"""
from fastapi import FastAPI

app = FastAPI(
    title="ML Service",
    description="Capa de modelos ML (en expansión).",
    version="0.1.0",
)

>>>>>>> origin/Miguel

@app.get("/health")
def health():
    return {"status": "ok"}