from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routers import auth, load, zones, score
import httpx
import os
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="BFF - Plataforma de Analítica Territorial")

# 🔹 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(load.router, prefix="/api/load", tags=["Load"])
app.include_router(zones.router, prefix="/api/zones", tags=["Zones"])
app.include_router(score.router)  # 👈 AQUÍ VA

# ❌ ELIMINADO init_db porque no usas DB en BFF

@app.get("/health")
async def health():
    status = {"status": "ok", "services": {}}
    services = {
        "ingestion": os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000"),
        "transformation": os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000"),
    }
    for name, url in services.items():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=5.0)
                if response.status_code == 200:
                    status["services"][name] = "connected"
                else:
                    status["services"][name] = "unhealthy"
                    status["status"] = "degraded"
        except Exception:
            status["services"][name] = "disconnected"
            status["status"] = "degraded"
    return status


@app.get("/")
async def root():
    return {
        "message": "BFF - Plataforma Analítica Territorial",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "auth_register": "/api/auth/register (POST)",
            "auth_token": "/api/auth/token (POST)",
            "auth_me": "/api/auth/me (GET)",
            "load": "/api/load (POST)",
            "zones": "/api/zones",
            "score": "/api/score (POST)"  # 👈 lo agregamos
        }
    }