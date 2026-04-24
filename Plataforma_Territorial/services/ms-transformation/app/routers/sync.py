from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
<<<<<<< HEAD
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database import get_db
from app.services.sync_service import SyncService
from app.core.exceptions import TransformationException

router = APIRouter()

@router.post("/zones")
async def sync_zones(db: AsyncSession = Depends(get_db)):
    """
    Endpoint para sincronizar zonas desde ms-ingestion.
    """
    try:
        service = SyncService()
        result = await service.sync_zones(db)

        return {
            "message": "Sincronización completada",
            "dataset_id": None,
            "transformation_run_id": None,
            "zones_processed": len(result.zones_data),
            "inserted": result.inserted_count,
            "updated": result.updated_count,
            "rules_version": result.rules_version
        }
    except TransformationException as e:
        raise e
    except Exception as e:
        logger.exception("Error en sync_zones")
        raise HTTPException(500, detail=f"Error interno: {str(e)}")
=======
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SyncZonesResponse
from app.services.sync_zones import run_sync_zones
from app.services.transform_service import MissingColumnsError

router = APIRouter(tags=["sync"])


@router.post("/sync/zones", response_model=SyncZonesResponse, summary="Sync Zones")
def sync_zones(db: Session = Depends(get_db)) -> SyncZonesResponse:
    try:
        run = run_sync_zones(db)
    except MissingColumnsError as e:
        raise HTTPException(
            status_code=400,
            detail={"message": str(e), "missing_columns": e.missing},
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"message": str(e)}) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail={"message": str(e)}) from e

    return SyncZonesResponse(
        message="Sincronización completada",
        transformation_run_id=run.id,
        source_dataset_id=run.source_dataset_id,
        rows_read=run.rows_read,
        rows_inserted=run.rows_inserted,
        rows_updated=run.rows_updated,
        rules_version=run.rules_version,
        rules_applied=dict(run.rules_applied or {}),
        completed_at=run.completed_at,
    )
>>>>>>> origin/Miguel
