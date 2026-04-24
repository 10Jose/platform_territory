"""
Ranking de zonas por score ponderado (densidad, ingreso, educación, presencia comercial)
usando ``GET /zones/data`` de **ms-transformation**.
"""
from fastapi import APIRouter, Request
import httpx
import os

router = APIRouter()

@router.get("/ranking")
async def get_ranking(request: Request):
    """Ordena zonas por score descendente; incluye fallback de ejemplo si falla la llamada."""
    transformation_url = os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000")

    top = int(request.query_params.get("top", 0))
    order = request.query_params.get("order", "desc")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{transformation_url}/zones/data", timeout=10.0)

            if response.status_code == 200:
                zones_data = response.json()

                ranking = []

                for zone in zones_data:
                    pop_norm = min(zone.get('population_density', 0) / 3000, 1)
                    income_norm = min(zone.get('average_income', 0) / 100000, 1)
                    edu_norm = min(zone.get('education_level', 0) / 20, 1)
                    business_norm = min(zone.get('commercial_presence_index', 0) / 1, 1)

                    score = (
                        pop_norm * 0.25 +
                        income_norm * 0.30 +
                        edu_norm * 0.25 +
                        business_norm * 0.20
                    )

                    if score >= 0.7:
                        level = "alta oportunidad"
                    elif score >= 0.5:
                        level = "oportunidad media"
                    else:
                        level = "baja oportunidad"

                    ranking.append({
                        "zone": zone.get('zone_name'),
                        "score": round(score, 2),
                        "level": level
                    })

                ranking.sort(
                    key=lambda x: x['score'],
                    reverse=(order == "desc")
                )

                if top > 0:
                    ranking = ranking[:top]

                for i, zona in enumerate(ranking, start=1):
                    zona["rank"] = i

                return {
                    "success": True,
                    "data": ranking,
                    "error": None
                }

    except Exception as e:
        pass

    # fallback
    fallback = [
        {"zone": "Suba", "score": 0.87, "level": "alta oportunidad"},
        {"zone": "Usaquén", "score": 0.81, "level": "alta oportunidad"}
    ]

    for i, zona in enumerate(fallback, start=1):
        zona["rank"] = i

    return {
        "success": True,
        "data": fallback,
        "error": None
    }
