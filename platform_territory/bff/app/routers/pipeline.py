"""
Pipeline Router (HU-14)

- Expone endpoints:
  POST /api/pipeline/run
  GET /api/pipeline/status
"""

from fastapi import APIRouter, Depends
from app.routers.auth import get_current_user
from app.domain.models import User
from app.services.pipeline_service import PipelineService

router = APIRouter()
pipeline_service = PipelineService()


@router.post("/pipeline/run")
async def run_pipeline(current_user: User = Depends(get_current_user)):
    """
    Ejecuta pipeline completo.

    - Requiere autenticación
    - Ejecuta flujo secuencial
    - Retorna estado final o fallo parcial
    """
    return await pipeline_service.run(user=current_user.username)


@router.get("/pipeline/status")
async def get_pipeline_status():
    """
    Devuelve estado de la última ejecución del pipeline.
    """
    return pipeline_service.get_status()