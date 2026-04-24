<<<<<<< HEAD
=======
"""Agrega indicadores agregados desde **ms-analytics** (requiere usuario autenticado)."""
>>>>>>> origin/Miguel
from fastapi import APIRouter, Depends
from app.routers.auth import get_current_user
from app.domain.models import User
import httpx
import os

router = APIRouter()

@router.get("/")
async def get_indicators(current_user: User = Depends(get_current_user)):
<<<<<<< HEAD
=======
    """Delega en ``/analytics/indicators`` del servicio de analítica."""
>>>>>>> origin/Miguel
    analytics_url = os.getenv("ANALYTICS_SERVICE_URL", "http://ms-analytics:8000")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{analytics_url}/analytics/indicators", timeout=10.0)
            if response.status_code == 200:
                return response.json()
            else:
                return {"indicators": [], "error": "Analytics service unavailable"}
    except Exception as e:
        return {"indicators": [], "error": str(e)}