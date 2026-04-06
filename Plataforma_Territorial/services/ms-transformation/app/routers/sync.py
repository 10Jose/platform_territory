from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
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
