"""
Microservicio de transformación territorial (HU-07).

Expone:
- ``POST /sync/zones``: sincroniza desde ms-ingestion el último dataset CSV,
  transforma con Pandas y persiste en ``transformation_runs`` y ``transformed_zone_data``.
- ``GET /zones`` y ``GET /zones/data``: consulta de zonas ya transformadas.

Variable de entorno típica: ``DATABASE_URL`` (PostgreSQL async). En Docker Compose apunta a ``db-transformation``.
"""
from fastapi import FastAPI
from app.routers import sync, zones
from app.infrastructure.database import engine, Base
from app.domain import models

app = FastAPI(
    title="Transformation Service",
    description="Transforma datos estructurados cargados en ingesta y los deja listos para analítica (HU-07).",
    version="1.0.0",
)

app.include_router(sync.router, prefix="/sync", tags=["Sync"])
app.include_router(zones.router, prefix="/zones", tags=["Zones"])


@app.get("/health")
def health():
    """Comprobación de vida para orquestación (Docker healthcheck, etc.)."""
    return {"status": "ok"}


@app.on_event("startup")
async def init_db():
    """Crea tablas en PostgreSQL si no existen (desarrollo / primer arranque)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)