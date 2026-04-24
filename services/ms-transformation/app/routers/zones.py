<<<<<<< HEAD
=======
"""
Consulta de zonas ya materializadas en ``transformed_zone_data``.

- Sin ``run_id``: vista “actual” (todas las filas; el upsert HU-07 mantiene una fila por ``zone_code``).
- Con ``run_id``: filas asociadas a esa corrida histórica.
"""
>>>>>>> origin/Miguel
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.infrastructure.database import get_db
from app.domain.models import TransformedZoneData, TransformationRun
import time
import logging
import httpx
import os

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_zones(
        db: AsyncSession = Depends(get_db),
        skip: int = Query(0, ge=0, description="Número de registros a saltar"),
        limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a retornar"),
        run_id: int = Query(None, description="ID del transformation run (opcional, por defecto el último)")
):
<<<<<<< HEAD
    start_time = time.time()

    # Obtener el último transformation_run si no se especifica
    if run_id is None:
        latest_run = await db.execute(
            select(TransformationRun.id).order_by(desc(TransformationRun.id)).limit(1)
        )
        run_id = latest_run.scalar()
        if run_id is None:
            return {"zones": [], "total": 0, "skip": skip, "limit": limit, "next": None}

    # Validar que el run corresponde a un dataset válido
=======
    """Listado paginado de códigos y nombres de zona; incluye puntero al último ``TransformationRun`` si aplica."""
    start_time = time.time()

    # Sin run_id: estado actual (una fila por zone_code tras upsert HU-07)
    if run_id is None:
        result = await db.execute(
            select(TransformedZoneData.zone_code, TransformedZoneData.zone_name)
            .order_by(TransformedZoneData.zone_name)
            .offset(skip)
            .limit(limit)
        )
        zones = [{"code": code, "name": name} for code, name in result.all()]
        total_result = await db.execute(select(func.count(TransformedZoneData.id)))
        total = total_result.scalar()
        latest_run = await db.execute(
            select(TransformationRun.id).order_by(desc(TransformationRun.id)).limit(1)
        )
        latest_run_id = latest_run.scalar()
        elapsed = time.time() - start_time
        logger.info(
            "GET /zones (actual) en %.3fs (skip=%s, limit=%s, total=%s)",
            elapsed,
            skip,
            limit,
            total,
        )
        return {
            "zones": zones,
            "total": total,
            "skip": skip,
            "limit": limit,
            "transformation_run_id": latest_run_id,
            "next": f"/zones?skip={skip + limit}&limit={limit}" if skip + limit < total else None,
        }

>>>>>>> origin/Miguel
    run_result = await db.execute(
        select(TransformationRun).where(TransformationRun.id == run_id)
    )
    run = run_result.scalar_one_or_none()
<<<<<<< HEAD
    
    if run:
        # Verificar estado del dataset en ms-ingestion
=======

    if run:
>>>>>>> origin/Miguel
        ingestion_url = os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{ingestion_url}/data/datasets", timeout=5.0)
                if response.status_code == 200:
                    datasets = response.json()
<<<<<<< HEAD
                    # Buscar el dataset correspondiente y verificar su estado
=======
>>>>>>> origin/Miguel
                    valid_dataset = any(
                        ds.get("validation_status") == "valid" and ds.get("status") in ["loaded", "TRANSFORMED"]
                        for ds in datasets
                    )
                    if not valid_dataset:
<<<<<<< HEAD
                        logger.warning(f"Run {run_id} no tiene dataset válido asociado")
        except Exception as e:
            logger.warning(f"No se pudo validar estado del dataset: {e}")

    # Consulta zonas del run específico (inmutabilidad - cada run tiene sus datos)
    result = await db.execute(
        select(TransformedZoneData.zone_code, TransformedZoneData.zone_name)
        .where(TransformedZoneData.transformation_run_id == run_id)
        .distinct()
=======
                        logger.warning("Run %s no tiene dataset válido asociado", run_id)
        except Exception as e:
            logger.warning("No se pudo validar estado del dataset: %s", e)

    result = await db.execute(
        select(TransformedZoneData.zone_code, TransformedZoneData.zone_name)
        .where(TransformedZoneData.transformation_run_id == run_id)
>>>>>>> origin/Miguel
        .order_by(TransformedZoneData.zone_name)
        .offset(skip)
        .limit(limit)
    )
    zones = [{"code": code, "name": name} for code, name in result.all()]

<<<<<<< HEAD
    # Total de zonas únicas en este run
=======
>>>>>>> origin/Miguel
    total_result = await db.execute(
        select(func.count(TransformedZoneData.id))
        .where(TransformedZoneData.transformation_run_id == run_id)
    )
    total = total_result.scalar()

    elapsed = time.time() - start_time
    logger.info(f"GET /zones completado en {elapsed:.3f}s (run_id={run_id}, skip={skip}, limit={limit}, total={total})")

    return {
        "zones": zones,
        "total": total,
        "skip": skip,
        "limit": limit,
        "transformation_run_id": run_id,
        "next": f"/zones?skip={skip + limit}&limit={limit}&run_id={run_id}" if skip + limit < total else None
    }


@router.get("/data")
async def get_zones_data(
        db: AsyncSession = Depends(get_db),
        run_id: int = Query(None, description="ID del transformation run")
):
<<<<<<< HEAD
    """Devuelve datos completos de las zonas para análisis"""
    
    if run_id is None:
        latest_run = await db.execute(
            select(TransformationRun.id).order_by(desc(TransformationRun.id)).limit(1)
        )
        run_id = latest_run.scalar()
        if run_id is None:
            return []
    
    result = await db.execute(
        select(TransformedZoneData)
        .where(TransformedZoneData.transformation_run_id == run_id)
        .order_by(TransformedZoneData.zone_name)
    )
=======
    """Indicadores numéricos completos por zona (densidad, ingreso, educación, índices) para analítica downstream."""
    
    if run_id is None:
        result = await db.execute(
            select(TransformedZoneData).order_by(TransformedZoneData.zone_name)
        )
    else:
        result = await db.execute(
            select(TransformedZoneData)
            .where(TransformedZoneData.transformation_run_id == run_id)
            .order_by(TransformedZoneData.zone_name)
        )
>>>>>>> origin/Miguel
    zones = result.scalars().all()
    
    return [
        {
            "zone_code": z.zone_code,
            "zone_name": z.zone_name,
            "population_density": z.population_density,
            "average_income": z.average_income,
            "education_level": z.education_level,
            "economic_activity_index": z.economic_activity_index,
            "commercial_presence_index": z.commercial_presence_index
        }
        for z in zones
    ]