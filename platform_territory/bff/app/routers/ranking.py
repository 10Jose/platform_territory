from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.analytics_client import AnalyticsClient

router = APIRouter()

@router.get("/ranking")
async def get_ranking(
    top: Optional[int] = Query(None, description="Limitar resultados (ej: top=10)"),
    order: Optional[str] = Query("desc", description="Orden: asc o desc"),
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)")
):
    """Lista zonas ordenadas por score de oportunidad con filtros opcionales."""
    try:
        client = AnalyticsClient()
        response = await client.get_ranking()
        ranking = response.get("data", []) if isinstance(response, dict) else response

        if order not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="order debe ser 'asc' o 'desc'")

        reverse = True if order == "desc" else False
        ranking.sort(key=lambda x: x["score"], reverse=reverse)

        if top is not None:
            ranking = ranking[:top]

        for i, zone in enumerate(ranking, start=1):
            zone["rank"] = i

        return {
            "success": True,
            "filters": {
                "top": top,
                "order": order,
                "start_date": start_date,
                "end_date": end_date
            },
            "data": ranking,
            "total": len(ranking)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error contacting analytics service: {str(e)}"
        )
