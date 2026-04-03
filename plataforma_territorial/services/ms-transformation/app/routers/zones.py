from fastapi import APIRouter

router = APIRouter()


@router.get("/zones")
async def get_zones(skip: int = 0, limit: int = 100):
    """
    Lista zonas disponibles tras transformación.
    Respuesta alineada con lo que consume el BFF y el front (data.zones).
    """
    return {
        "zones": [],
        "total": 0,
        "skip": skip,
        "limit": limit,
    }


@router.post("/sync/zones")
async def sync_zones():
    """
    Disparado por el BFF tras una carga; aquí se conectaría la lógica real
    de sincronización desde ingesta/transformación.
    """
    return {"status": "ok", "zones_updated": 0}
