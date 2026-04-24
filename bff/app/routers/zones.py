"""Zonas transformadas (proxy a **ms-transformation**) y disparo manual de HU-07."""
import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from app.services.transformation_client import TransformationClient
from app.routers.auth import get_current_user
from app.domain.models import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_zones(skip: int = Query(0, ge=0),
                    limit: int = Query(100, ge=1, le=500)
):
    """Listado paginado de zonas desde transformación (sin auth en esta ruta)."""
    try:
        client = TransformationClient()
        result = await client.get_zones(skip, limit)
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener zonas: {str(e)}")


@router.post("/sync")
async def sync_zones_transform(current_user: User = Depends(get_current_user)):
    """
    HU-07: dispara la transformación en ms-transformation (POST /sync/zones).
    Descarga el último CSV válido desde ms-ingestion, normaliza con Pandas,
    escribe transformed_zone_data y registra transformation_runs.
    """
    logger.info("HU-07 sync solicitado por %s", current_user.username)
    try:
        client = TransformationClient()
        result = await client.sync_zones()
        return result
    except Exception as e:
        raise HTTPException(500, detail=f"Error en sincronización / transformación: {str(e)}") from e
