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


def _safe_variation_percentage(values: List[float]) -> float:
    if not values:
        return 0.0
    max_value = max(values)
    min_value = min(values)
    if max_value == 0:
        return 0.0
    return ((max_value - min_value) / max_value) * 100


@router.get("/compare")
async def compare_zones(
        zones: str,
        db: AsyncSession = Depends(get_db)
):
    try:
        requested_zones = [zone.strip() for zone in zones.split(",") if zone.strip()]
        unique_requested_zones = list(dict.fromkeys(requested_zones))

        if len(unique_requested_zones) < 2:
            raise HTTPException(
                status_code=400,
                detail="Debes seleccionar al menos 2 zonas para comparar."
            )

        query = (
            select(IndicatorResult)
            .where(
                or_(
                    IndicatorResult.zone_code.in_(unique_requested_zones),
                    IndicatorResult.zone_name.in_(unique_requested_zones),
                )
            )
            .order_by(IndicatorResult.zone_name)
        )

        result = await db.execute(query)
        indicator_rows = result.scalars().all()

        zone_map: Dict[str, Dict] = {}
        for row in indicator_rows:
            if row.zone_code in unique_requested_zones:
                key = row.zone_code
            elif row.zone_name in unique_requested_zones:
                key = row.zone_name
            else:
                continue

            zone_map[key] = {
                "zone_code": row.zone_code,
                "zone_name": row.zone_name,
                "population": row.population_indicator or 0,
                "income": row.income_indicator or 0,
                "education": row.education_indicator or 0,
                "competition": row.competition_indicator or 0,
            }

        ordered_zones = [zone_map[key] for key in unique_requested_zones if key in zone_map]
        if len(ordered_zones) < 2:
            raise HTTPException(
                status_code=404,
                detail="No se encontraron al menos 2 zonas con indicadores para comparar."
            )

        metric_definitions = [
            ("population", "Población"),
            ("income", "Ingreso"),
            ("education", "Educación"),
            ("competition", "Competencia"),
        ]

        metric_max = {
            metric: max((float(zone[metric]) for zone in ordered_zones), default=0.0)
            for metric, _ in metric_definitions
        }

        for zone in ordered_zones:
            normalized_values = []
            for metric, _ in metric_definitions:
                max_value = metric_max[metric]
                value = float(zone[metric])
                normalized_values.append((value / max_value) if max_value > 0 else 0.0)
            zone["score"] = round((sum(normalized_values) / len(metric_definitions)) * 100, 2)

        comparison_rows = []
        for metric, label in metric_definitions:
            raw_values = [float(zone[metric]) for zone in ordered_zones]
            row_values = {zone["zone_code"]: zone[metric] for zone in ordered_zones}
            row_values["label"] = label
            variation_pct = round(_safe_variation_percentage(raw_values), 2)
            comparison_rows.append({
                "metric": metric,
                "label": label,
                "values": row_values,
                "variation_pct": variation_pct,
                "significant_difference": variation_pct > 20,
            })

        return {
            "zones": ordered_zones,
            "comparison": comparison_rows
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en GET /analytics/compare")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")
