from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models import TransformationRun
from app.services.ingestion_client import IngestionClient
from app.services.transform_service import build_rules_metadata, validate_and_load_dataframe
from app.services.zone_repository import upsert_zones_from_dataframe


def run_sync_zones(db: Session) -> TransformationRun:
    """Descarga el último CSV desde ingestion, transforma y persiste (sin modificar ingestion)."""
    client = IngestionClient()
    rules_meta = build_rules_metadata(settings.transformation_rules_version)

    latest = client.fetch_latest_dataset()
    raw = client.download_csv_bytes(latest.id)
    df = validate_and_load_dataframe(raw)

    source_id = str(latest.id)
    run = TransformationRun(
        status="running",
        rules_version=settings.transformation_rules_version,
        rules_applied=rules_meta,
        source_dataset_id=source_id,
        rows_read=int(len(df)),
        rows_inserted=0,
        rows_updated=0,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    run_id = run.id

    try:
        inserted, updated = upsert_zones_from_dataframe(db, df, source_dataset_id=source_id)
        run = db.get(TransformationRun, run_id)
        assert run is not None
        run.rows_inserted = inserted
        run.rows_updated = updated
        run.rows_read = int(len(df))
        run.status = "success"
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(run)
        return run
    except Exception as e:
        db.rollback()
        run = db.get(TransformationRun, run_id)
        if run is not None:
            run.status = "failed"
            run.error_message = str(e)
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(run)
        raise
