"""HU-12: Scoring territorial — calcula y persiste scores por zona."""
import httpx
import os
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database import get_db
from app.domain.zone_score import ZoneScore

logger = logging.getLogger(__name__)
router = APIRouter()

CONFIGURATION_URL = os.getenv("CONFIGURATION_SERVICE_URL", "http://ms-configuration:8000")
TRANSFORMATION_URL = os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000")
AUDIT_URL = os.getenv("AUDIT_SERVICE_URL", "http://ms-audit:8000")


async def get_weights() -> dict:
    """Obtiene pesos y max de ms-configuration; fallback a defaults."""
    defaults = {
        "weights": {"poblacion": 0.25, "ingresos": 0.30, "educacion": 0.25, "competencia": 0.20},
        "max": {"poblacion": 3000, "ingresos": 100000, "educacion": 20, "competencia": 1},
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{CONFIGURATION_URL}/config/parameters", timeout=5.0)
            if resp.status_code == 200:
                cfg = resp.json()
                return {
                    "weights": {
                        "poblacion": cfg.get("weight_population", 0.25),
                        "ingresos": cfg.get("weight_income", 0.30),
                        "educacion": cfg.get("weight_education", 0.25),
                        "competencia": cfg.get("weight_business", 0.20),
                    },
                    "max": {
                        "poblacion": cfg.get("max_population_density", 3000),
                        "ingresos": cfg.get("max_average_income", 100000),
                        "educacion": cfg.get("max_education_level", 20),
                        "competencia": cfg.get("max_commercial_presence", 1),
                    },
                }
    except Exception:
        pass
    return defaults


def calcular_score(indicadores: dict, pesos: dict):
    total = 0
    detalle = {}
    for key in indicadores:
        valor = indicadores[key]
        peso = pesos.get(key, 0)
        parcial = valor * peso
        detalle[key] = {"valor": valor, "peso": peso, "resultado": round(parcial, 4)}
        total += parcial
    score_final = round(total * 100, 2)
    return score_final, detalle


@router.post("/score")
async def calcular_score_endpoint(db: AsyncSession = Depends(get_db)):
    """Calcula score para todas las zonas usando indicadores + pesos de configuración."""
    pesos = await get_weights()
    weights = pesos["weights"]
    maxvals = pesos["max"]

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{TRANSFORMATION_URL}/zones/data", timeout=10.0)
            if resp.status_code != 200:
                raise HTTPException(503, detail="No se pudo obtener datos de transformación")
            zones_data = resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(503, detail=f"Error contactando ms-transformation: {str(e)}")

    if not zones_data:
        raise HTTPException(404, detail="No hay datos disponibles para calcular scores")

    resultados = []
    for zone in zones_data:
        zona_name = zone.get("zone_name", "")
        indicadores = {
            "poblacion": min(zone.get("population_density", 0) / maxvals["poblacion"], 1),
            "ingresos": min(zone.get("average_income", 0) / maxvals["ingresos"], 1),
            "educacion": min(zone.get("education_level", 0) / maxvals["educacion"], 1),
            "competencia": min(zone.get("commercial_presence_index", 0) / maxvals["competencia"], 1),
        }

        score, detalle = calcular_score(indicadores, weights)

        nuevo = ZoneScore(zona=zona_name, score=score, detalle=detalle)
        db.add(nuevo)

        resultados.append({
            "zona": zona_name,
            "score": score,
            "fecha": datetime.utcnow().isoformat(),
            "detalle": detalle,
        })

    await db.commit()

    # Evento de auditoría
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{AUDIT_URL}/events", json={
                "event_type": "SCORE_CALCULATED",
                "data": {"zones_processed": len(resultados), "timestamp": datetime.utcnow().isoformat()},
            }, timeout=5.0)
    except Exception:
        logger.warning("No se pudo enviar evento de auditoría")

    return {"success": True, "zones_processed": len(resultados), "data": resultados}


@router.get("/scores")
async def get_scores(db: AsyncSession = Depends(get_db)):
    """Retorna los últimos scores calculados."""
    result = await db.execute(select(ZoneScore).order_by(ZoneScore.fecha.desc()).limit(100))
    scores = result.scalars().all()
    return [
        {"id": s.id, "zona": s.zona, "score": s.score, "fecha": s.fecha.isoformat() if s.fecha else None, "detalle": s.detalle}
        for s in scores
    ]
