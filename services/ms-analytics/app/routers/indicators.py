<<<<<<< HEAD
=======
"""Indicadores de alto nivel derivados del listado de zonas en **ms-transformation**."""
>>>>>>> origin/Miguel
from fastapi import APIRouter
import httpx
import os

router = APIRouter()

@router.get("/indicators")
async def get_indicators():
<<<<<<< HEAD
=======
    """Totales y cobertura a partir de ``GET /zones`` del servicio de transformación."""
>>>>>>> origin/Miguel
    transformation_url = os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{transformation_url}/zones", timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                zones = data.get("zones", [])
                total = data.get("total", 0)
                
                return {
                    "indicators": [
                        {"name": "Total Zonas", "value": total, "unit": "zonas"},
                        {"name": "Zonas Activas", "value": len(zones), "unit": "zonas"},
                        {"name": "Cobertura", "value": round((len(zones) / total * 100) if total > 0 else 0, 2), "unit": "%"}
                    ]
                }
    except:
        pass
    
    return {
        "indicators": [
            {"name": "Total Zonas", "value": 0, "unit": "zonas"},
            {"name": "Datasets Cargados", "value": 0, "unit": "datasets"}
        ]
    }
