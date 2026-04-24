<<<<<<< HEAD
=======
"""
Microservicio de **ingesta** de datasets CSV.

Persiste metadatos y archivos en ``db-ingestion``; validación fila a fila en ``validators``.
"""
>>>>>>> origin/Miguel
from fastapi import FastAPI
from app.routers import data
from app.infrastructure.database import engine, Base
from app.domain import models

<<<<<<< HEAD
app = FastAPI(title="Data Ingestion Service")

app.include_router(data.router, prefix="/data", tags=["Data"])

@app.get("/health")
def health():
    return {"status": "ok"}

=======
app = FastAPI(
    title="Data Ingestion Service",
    description="Recepción, validación y almacenamiento de archivos territoriales (CSV).",
    version="1.0.0",
)

app.include_router(data.router, prefix="/data", tags=["Data"])


@app.get("/health")
def health():
    """Salud del contenedor / orquestación."""
    return {"status": "ok"}


>>>>>>> origin/Miguel
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)