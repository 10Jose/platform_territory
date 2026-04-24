<<<<<<< HEAD
from fastapi import FastAPI

app = FastAPI(title="Nombre del Microservicio")
=======
"""
Microservicio de **recomendaciones** (placeholder): consumiría analítica/ML para sugerencias por zona.

Actualmente solo ``/health`` para el grafo de Compose.
"""
from fastapi import FastAPI

app = FastAPI(
    title="Recommendations Service",
    description="Motor de recomendaciones territoriales (en expansión).",
    version="0.1.0",
)

>>>>>>> origin/Miguel

@app.get("/health")
def health():
    return {"status": "ok"}