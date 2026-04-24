from fastapi import APIRouter, HTTPException
from app.services.configuration_client import ConfigurationClient

router = APIRouter()


@router.get("/")
async def get_configuration():
    """Obtiene la configuración activa del modelo."""
    try:
        client = ConfigurationClient()
        return await client.get_parameters()
    except Exception as e:
        raise HTTPException(503, detail=f"Error al obtener configuración: {str(e)}")


@router.put("/")
async def update_configuration(data: dict):
    """Actualiza la configuración activa del modelo."""
    try:
        client = ConfigurationClient()
        return await client.update_parameters(data)
    except Exception as e:
        raise HTTPException(503, detail=f"Error al actualizar configuración: {str(e)}")
