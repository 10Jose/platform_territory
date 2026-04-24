from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.infrastructure.database import get_db
from app.services.indicators_service import IndicatorsService
from app.core.exceptions import AnalyticsException, NoDataError
from app.domain.models import IndicatorResult
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/calculate")
async def calculate_indicators(db: AsyncSession = Depends(get_db)):
    try:
        service = IndicatorsService(db)
        result = await service.calculate_indicators()
        return result
    except NoDataError as e:
        raise e
    except AnalyticsException as e:
        raise e
    except Exception as e:
        logger.exception("Error en POST /calculate")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/")
async def get_indicators(
        db: AsyncSession = Depends(get_db),
        zone_code: Optional[str] = None
):
    try:
        service = IndicatorsService(db)
        query = select(IndicatorResult).order_by(IndicatorResult.zone_name)
        if zone_code:
            query = query.where(IndicatorResult.zone_code == zone_code)
        result = await db.execute(query)
        indicators = result.scalars().all()
        return [
            {
                "id": i.id,
                "zone_code": i.zone_code,
                "zone_name": i.zone_name,
                "population": i.population_indicator,
                "income": i.income_indicator,
                "education": i.education_indicator,
                "competition": i.competition_indicator,
                "competition_level": service.get_competition_level(i.competition_indicator),
                "calculated_at": i.calculated_at.isoformat() if i.calculated_at else None
            }
            for i in indicators
        ]
    except Exception as e:
        logger.exception("Error en GET /analytics/")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


# ==================== HU-18: Comparador ====================

def _variation_pct(values: List[float]) -> float:
    if not values:
        return 0.0
    mx, mn = max(values), min(values)
    return round(((mx - mn) / mx) * 100, 2) if mx > 0 else 0.0


@router.get("/compare")
async def compare_zones(zones: str, db: AsyncSession = Depends(get_db)):
    """Compara 2+ zonas lado a lado (HU-18)."""
    requested = list(dict.fromkeys([z.strip() for z in zones.split(",") if z.strip()]))
    if len(requested) < 2:
        raise HTTPException(400, detail="Debes seleccionar al menos 2 zonas para comparar.")

    query = (
        select(IndicatorResult)
        .where(or_(
            IndicatorResult.zone_code.in_(requested),
            IndicatorResult.zone_name.in_(requested),
        ))
        .order_by(IndicatorResult.zone_name)
    )
    result = await db.execute(query)
    rows = result.scalars().all()

    zone_map: Dict[str, Dict] = {}
    for row in rows:
        key = row.zone_code if row.zone_code in requested else (row.zone_name if row.zone_name in requested else None)
        if not key:
            continue
        zone_map[key] = {
            "zone_code": row.zone_code,
            "zone_name": row.zone_name,
            "population": row.population_indicator or 0,
            "income": row.income_indicator or 0,
            "education": row.education_indicator or 0,
            "competition": row.competition_indicator or 0,
        }

    ordered = [zone_map[k] for k in requested if k in zone_map]
    if len(ordered) < 2:
        raise HTTPException(404, detail="No se encontraron al menos 2 zonas con indicadores.")

    metrics = [("population", "Población"), ("income", "Ingreso"), ("education", "Educación"), ("competition", "Competencia")]
    metric_max = {m: max((float(z[m]) for z in ordered), default=0.0) for m, _ in metrics}

    for z in ordered:
        norms = [(float(z[m]) / metric_max[m]) if metric_max[m] > 0 else 0.0 for m, _ in metrics]
        z["score"] = round((sum(norms) / len(metrics)) * 100, 2)

    comparison = []
    for m, label in metrics:
        vals = [float(z[m]) for z in ordered]
        var = _variation_pct(vals)
        comparison.append({
            "metric": m, "label": label,
            "values": {z["zone_code"]: z[m] for z in ordered},
            "variation_pct": var, "significant_difference": var > 20,
        })

    return {"zones": ordered, "comparison": comparison}
