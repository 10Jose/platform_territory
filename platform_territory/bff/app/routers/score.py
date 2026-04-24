from fastapi import APIRouter, HTTPException, Depends
from app.routers.auth import get_current_user
from app.domain.models import User
import httpx
import os

router = APIRouter()

ANALYTICS_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://ms-analytics:8000")


@router.post("/")
async def calculate_scores(current_user: User = Depends(get_current_user)):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{ANALYTICS_URL}/analytics/score", timeout=30.0)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(503, detail=f"Error al calcular scores: {str(e)}")


@router.get("/")
async def get_scores(current_user: User = Depends(get_current_user)):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{ANALYTICS_URL}/analytics/scores", timeout=10.0)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(503, detail=f"Error al obtener scores: {str(e)}")
