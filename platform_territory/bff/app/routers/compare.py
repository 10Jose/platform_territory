from fastapi import APIRouter, HTTPException, Depends
from app.services.analytics_client import AnalyticsClient
from app.routers.auth import get_current_user
from app.domain.models import User
import httpx

router = APIRouter()


@router.get("")
async def compare_zones(zones: str, current_user: User = Depends(get_current_user)):
    try:
        client = AnalyticsClient()
        return await client.compare_zones(zones)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(500, detail=f"Error al comparar zonas: {str(e)}")
