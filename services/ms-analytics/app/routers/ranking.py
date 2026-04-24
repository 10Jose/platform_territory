<<<<<<< HEAD
=======
"""
Ranking de zonas por score ponderado (densidad, ingreso, educación, presencia comercial)
usando ``GET /zones/data`` de **ms-transformation**.
"""
>>>>>>> origin/Miguel
from fastapi import APIRouter
import httpx
import os

router = APIRouter()

@router.get("/ranking")
async def get_ranking():
<<<<<<< HEAD
=======
    """Ordena zonas por score descendente; incluye fallback de ejemplo si falla la llamada."""
>>>>>>> origin/Miguel
    transformation_url = os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000")
    
    try:
        async with httpx.AsyncClient() as client:
            # Obtener zonas transformadas
            response = await client.get(f"{transformation_url}/zones/data", timeout=10.0)
            
            if response.status_code == 200:
                zones_data = response.json()
                
                # Calcular score para cada zona
                ranking = []
                for zone in zones_data:
                    # Normalizar valores (0-1)
                    pop_norm = min(zone.get('population_density', 0) / 3000, 1)
                    income_norm = min(zone.get('average_income', 0) / 100000, 1)
                    edu_norm = min(zone.get('education_level', 0) / 20, 1)
                    business_norm = min(zone.get('commercial_presence_index', 0) / 1, 1)
                    
                    # Score ponderado
                    score = (pop_norm * 0.25 + income_norm * 0.30 + 
                            edu_norm * 0.25 + business_norm * 0.20)
                    
                    # Clasificar nivel
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
                
                # Ordenar por score descendente
                ranking.sort(key=lambda x: x['score'], reverse=True)
                return ranking
    except:
        pass
    
    # Fallback con datos de ejemplo
    return [
        {"zone": "Suba", "score": 0.87, "level": "alta oportunidad"},
        {"zone": "Usaquén", "score": 0.81, "level": "alta oportunidad"},
    ]