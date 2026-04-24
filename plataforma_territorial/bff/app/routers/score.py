from fastapi import APIRouter
import httpx

router = APIRouter()

@router.post("/api/score")
async def proxy_score(data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://ms-analytics:8000/analytics/score",
            json=data
        )
    return response.json()