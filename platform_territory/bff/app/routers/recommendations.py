"""
Recomendaciones heurísticas a partir del ranking de **ms-analytics** (top 3 zonas).
"""
from fastapi import APIRouter
import httpx
import os

router = APIRouter()

@router.get("/")
async def get_recommendations():
    """Genera textos de prioridad de inversión según el score de cada zona."""
    analytics_url = os.getenv("ANALYTICS_SERVICE_URL", "http://ms-analytics:8000")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{analytics_url}/analytics/ranking", timeout=10.0)
            
            if response.status_code == 200:
                ranking = response.json()
                
                # Generar recomendaciones basadas en el ranking
                recommendations = []
                for zone in ranking[:3]:  # Top 3
                    score = zone.get('score', 0)
                    zone_name = zone.get('zone')
                    
                    if score >= 0.7:
                        rec = f"Zona de alta prioridad para inversión. Score: {score}"
                    elif score >= 0.5:
                        rec = f"Zona con potencial moderado. Requiere análisis detallado. Score: {score}"
                    else:
                        rec = f"Zona de baja prioridad. Score: {score}"
                    
                    recommendations.append({
                        "zone": zone_name,
                        "recommendation": rec,
                        "priority": "alta" if score >= 0.7 else "media" if score >= 0.5 else "baja"
                    })
                
                return recommendations
    except:
        pass
    
    # Fallback
    return [{"zone": "Suba", "recommendation": "Alta oportunidad"}]