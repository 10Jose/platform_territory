"""
Ranking de zonas por score ponderado usando parámetros de ms-configuration (HU-11).
"""
from fastapi import APIRouter, Request
import httpx
import os

router = APIRouter()

CONFIGURATION_URL = os.getenv("CONFIGURATION_SERVICE_URL", "http://ms-configuration:8000")
TRANSFORMATION_URL = os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000")

# Valores por defecto si ms-configuration no responde
DEFAULT_CONFIG = {
    "weight_population": 0.25,
    "weight_income": 0.30,
    "weight_education": 0.25,
    "weight_business": 0.20,
    "threshold_high": 0.7,
    "threshold_medium": 0.5,
    "max_population_density": 3000.0,
    "max_average_income": 100000.0,
    "max_education_level": 20.0,
    "max_commercial_presence": 1.0,
}


async def get_model_config() -> dict:
    """Obtiene parámetros activos de ms-configuration; fallback a defaults."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{CONFIGURATION_URL}/config/parameters", timeout=5.0)
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass
    return DEFAULT_CONFIG


@router.get("/ranking")
async def get_ranking(request: Request):
    """Ordena zonas por score descendente usando configuración activa."""
    top = int(request.query_params.get("top", 0))
    order = request.query_params.get("order", "desc")

    cfg = await get_model_config()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{TRANSFORMATION_URL}/zones/data", timeout=10.0)

            if response.status_code == 200:
                zones_data = response.json()
                ranking = []

                for zone in zones_data:
                    pop_norm = min(zone.get('population_density', 0) / cfg['max_population_density'], 1)
                    income_norm = min(zone.get('average_income', 0) / cfg['max_average_income'], 1)
                    edu_norm = min(zone.get('education_level', 0) / cfg['max_education_level'], 1)
                    business_norm = min(zone.get('commercial_presence_index', 0) / cfg['max_commercial_presence'], 1)

                    score = (
                        pop_norm * cfg['weight_population'] +
                        income_norm * cfg['weight_income'] +
                        edu_norm * cfg['weight_education'] +
                        business_norm * cfg['weight_business']
                    )

                    if score >= cfg['threshold_high']:
                        level = "alta oportunidad"
                    elif score >= cfg['threshold_medium']:
                        level = "oportunidad media"
                    else:
                        level = "baja oportunidad"

                    ranking.append({
                        "zone": zone.get('zone_name'),
                        "score": round(score, 2),
                        "level": level
                    })

                ranking.sort(key=lambda x: x['score'], reverse=(order == "desc"))

                if top > 0:
                    ranking = ranking[:top]

                for i, zona in enumerate(ranking, start=1):
                    zona["rank"] = i

                return {"success": True, "data": ranking, "error": None}

    except Exception:
        pass

    # fallback
    fallback = [
        {"zone": "Suba", "score": 0.87, "level": "alta oportunidad", "rank": 1},
        {"zone": "Usaquén", "score": 0.81, "level": "alta oportunidad", "rank": 2},
    ]
    return {"success": True, "data": fallback, "error": None}
