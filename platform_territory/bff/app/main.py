"""
Backend-for-Frontend (BFF) de la plataforma de analítica territorial.

- Expone API unificada bajo ``/api/*`` para el front y herramientas (Postman).
- Autenticación JWT y usuarios en ``db-auth`` (SQLAlchemy async).
- Agrega llamadas HTTP a microservicios: ingesta, transformación, analítica, ML,
  recomendaciones, configuración y auditoría.
- Middleware de ``X-Trace-ID`` para correlación de logs.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import load
from app.routers import zones, indicators, ranking, recommendations, configuration, compare
from app.routers.score import router as score_router
from app.routers import datasets
from app.routers import auth
import httpx
import os
import logging
import uuid
import time
from contextvars import ContextVar
from app.infrastructure.database import engine, Base
from app.domain import models
from app.routers import pipeline

# Trace ID para logs distribuidos
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

class TraceIdFilter(logging.Filter):
    """Inyecta ``trace_id`` en cada registro de log (contexto por petición)."""

    def filter(self, record):
        record.trace_id = trace_id_var.get() or "no-trace"
        return True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)
logger.addFilter(TraceIdFilter())

app = FastAPI(
    title="BFF - Plataforma de Analítica Territorial",
    description="Capa de agregación y seguridad entre el cliente y los microservicios.",
    version="1.0.0",
)

@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    """Asigna o reenvía ``X-Trace-ID`` y registra duración por petición."""
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4())[:8])
    trace_id_var.set(trace_id)
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers["X-Trace-ID"] = trace_id
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(load.router, prefix="/api/load", tags=["Load"])
app.include_router(zones.router, prefix="/api/zones", tags=["Zones"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["Indicators"])
app.include_router(ranking.router, prefix="/api", tags=["Ranking"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(configuration.router, prefix="/api/configuration", tags=["Configuration"])
app.include_router(compare.router, prefix="/api/compare", tags=["Compare"])
app.include_router(score_router, prefix="/api/score", tags=["Score"])
app.include_router(pipeline.router, prefix="/api", tags=["Pipeline"])

# HEALTH CHECK COMPLETO
@app.get("/health")
async def health():
    status = {
        "status": "ok",
        "services": {},
        "timestamp": time.time()
    }

    services = {
        "ingestion": os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000"),
        "transformation": os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000"),
        "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://ms-analytics:8000"),
        "ml": os.getenv("ML_SERVICE_URL", "http://ms-ml:8000"),
        "recommendations": os.getenv("RECOMMENDATIONS_SERVICE_URL", "http://ms-recommendations:8000"),
        "configuration": os.getenv("CONFIGURATION_SERVICE_URL", "http://ms-configuration:8000"),
        "audit": os.getenv("AUDIT_SERVICE_URL", "http://ms-audit:8000"),
    }

    any_degraded = False

    for name, url in services.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5.0)
                if response.status_code == 200:
                    status["services"][name] = "connected"
                else:
                    status["services"][name] = "unhealthy"
                    any_degraded = True
        except:
            status["services"][name] = "down"
            any_degraded = True

    if any_degraded:
        status["status"] = "degraded"

    return status

# HEALTH SIMPLE
@app.get("/health/summary")
async def health_summary():
    status = {"status": "ok", "services": {}}

    services = {
        "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://ms-analytics:8000"),
    }

    for name, url in services.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=3.0)
                status["services"][name] = "ok" if response.status_code == 200 else "error"
        except:
            status["services"][name] = "down"
            status["status"] = "degraded"

    return status

# ROOT
@app.get("/")
async def root():
    """Índice de descubrimiento con rutas principales."""
    return {
        "message": "BFF - Plataforma Analítica Territorial",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "health_summary": "/health/summary",
            "auth_register": "/api/auth/register (POST)",
            "auth_token": "/api/auth/token (POST)",
            "auth_me": "/api/auth/me (GET)",
            "load": "/api/load (POST)",
            "zones": "/api/zones",
            "zones_sync_hu07": "/api/zones/sync (POST, auth)",
            "datasets": "/api/datasets",
            "indicators": "/api/indicators",
            "ranking": "/api/ranking",
            "configuration": "/api/configuration (GET/PUT)",
            "compare": "/api/compare?zones=z1,z2 (GET)",
            "score": "/api/score (POST calcular, GET consultar)",
        }
    }

# DB INIT
@app.on_event("startup")
async def init_db():
    """Crea tablas de usuarios en ``db-auth`` si no existen."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
