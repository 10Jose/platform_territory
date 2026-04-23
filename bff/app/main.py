from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware  # 🔥 IMPORTANTE (cambiado)
from app.routers import load
from app.routers import zones, indicators, ranking, recommendations
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

# Trace ID para logs distribuidos
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        record.trace_id = trace_id_var.get() or "no-trace"
        return True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)
logger.addFilter(TraceIdFilter())

app = FastAPI(title="BFF - Plataforma de Analítica Territorial")

# Middleware para trace_id
@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4())[:8])
    trace_id_var.set(trace_id)
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers["X-Trace-ID"] = trace_id
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response

# 🔥 CORS CORREGIDO (AQUÍ ESTABA EL ERROR)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 permite frontend en cualquier puerto (3001)
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

# Ranking
app.include_router(ranking.router, prefix="/api", tags=["Ranking"])

app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])

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
    return {
        "message": "BFF - Plataforma Analítica Territorial",
        "docs": "/docs",
        "endpoints": {
            "ranking": "/api/ranking",
            "indicators": "/api/indicators"
        }
    }

# DB INIT
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)