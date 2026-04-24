<<<<<<< HEAD
=======
"""
Backend-for-Frontend (BFF) de la plataforma de analítica territorial.

- Expone API unificada bajo ``/api/*`` para el front y herramientas (Postman).
- Autenticación JWT y usuarios en ``db-auth`` (SQLAlchemy async).
- Agrega llamadas HTTP a microservicios: ingesta, transformación, analítica, ML,
  recomendaciones, configuración y auditoría.
- Middleware de ``X-Trace-ID`` para correlación de logs.

Variables de entorno típicas: ``AUTH_DATABASE_URL``, ``INGESTION_SERVICE_URL``,
``TRANSFORMATION_SERVICE_URL``, ``ANALYTICS_SERVICE_URL``, etc.
"""
>>>>>>> origin/Miguel
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from app.routers import load
from app.routers import zones, indicators, ranking, recommendations
from app.routers import datasets
import httpx
import os
import logging
import uuid
import time
from contextvars import ContextVar
from app.routers import auth
from app.infrastructure.database import engine, Base
from app.domain import models

# Trace ID para logs distribuidos
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

class TraceIdFilter(logging.Filter):
<<<<<<< HEAD
=======
    """Inyecta ``trace_id`` en cada registro de log (contexto por petición)."""

>>>>>>> origin/Miguel
    def filter(self, record):
        record.trace_id = trace_id_var.get() or "no-trace"
        return True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [trace_id=%(trace_id)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)
logger.addFilter(TraceIdFilter())

<<<<<<< HEAD
app = FastAPI(title="BFF - Plataforma de Analítica Territorial")

@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
=======
app = FastAPI(
    title="BFF - Plataforma de Analítica Territorial",
    description="Capa de agregación y seguridad entre el cliente y los microservicios.",
    version="1.0.0",
)

@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    """Asigna o reenvía ``X-Trace-ID`` y registra duración por petición."""
>>>>>>> origin/Miguel
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4())[:8])
    trace_id_var.set(trace_id)
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers["X-Trace-ID"] = trace_id
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(load.router, prefix="/api/load", tags=["Load"])
app.include_router(zones.router, prefix="/api/zones", tags=["Zones"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["Indicators"])
app.include_router(ranking.router, prefix="/api/ranking", tags=["Ranking"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])


@app.get("/health")
async def health():
    """
    Endpoint de salud que verifica el estado de todos los microservicios.
    """
    status = {
        "status": "ok",
        "services": {},
        "timestamp": None
    }

    import time
    status["timestamp"] = time.time()

    # Todos los microservicios del proyecto
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
                    status["services"][name] = {
                        "status": "connected",
                        "response": response.json() if response.content else None
                    }
                else:
                    status["services"][name] = {
                        "status": "unhealthy",
                        "status_code": response.status_code
                    }
                    any_degraded = True
                    logger.warning(f"Servicio {name} respondió con estado {response.status_code}")
        except httpx.TimeoutException:
            status["services"][name] = {
                "status": "timeout",
                "error": "No respondió en 5 segundos"
            }
            any_degraded = True
            logger.warning(f"Timeout al conectar con {name}")
        except httpx.ConnectError:
            status["services"][name] = {
                "status": "disconnected",
                "error": "No se pudo conectar"
            }
            any_degraded = True
            logger.error(f"No se pudo conectar con {name}")
        except Exception as e:
            status["services"][name] = {
                "status": "error",
                "error": str(e)
            }
            any_degraded = True
            logger.error(f"Error al conectar con {name}: {e}")

    if any_degraded:
        status["status"] = "degraded"

    return status


@app.get("/health/summary")
async def health_summary():
    """
    Endpoint de resumen rápido (solo estados principales).
    """
    status = {"status": "ok", "services": {}}

    services = {
        "ingestion": os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000"),
        "transformation": os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000"),
        "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://ms-analytics:8000"),
        "ml": os.getenv("ML_SERVICE_URL", "http://ms-ml:8000"),
        "recommendations": os.getenv("RECOMMENDATIONS_SERVICE_URL", "http://ms-recommendations:8000"),
        "configuration": os.getenv("CONFIGURATION_SERVICE_URL", "http://ms-configuration:8000"),
        "audit": os.getenv("AUDIT_SERVICE_URL", "http://ms-audit:8000"),
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


@app.get("/")
async def root():
<<<<<<< HEAD
=======
    """Índice de descubrimiento con rutas principales (sin OpenAPI)."""
>>>>>>> origin/Miguel
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
<<<<<<< HEAD
=======
            "zones_sync_hu07": "/api/zones/sync (POST, auth)",
>>>>>>> origin/Miguel
            "datasets": "/api/datasets",
            "indicators": "/api/indicators",
            "ranking": "/api/ranking",
            "recommendations": "/api/recommendations"
        }
    }

@app.on_event("startup")
async def init_db():
<<<<<<< HEAD
=======
    """Crea tablas de usuarios en ``db-auth`` si no existen."""
>>>>>>> origin/Miguel
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)