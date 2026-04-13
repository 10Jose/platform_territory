from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import TransformedZoneData


def upsert_zones_from_dataframe(
    db: Session, df: pd.DataFrame, source_dataset_id: str | None
) -> tuple[int, int]:
    rows_inserted = 0
    rows_updated = 0
    now = datetime.now(timezone.utc)

    for row in df.to_dict("records"):
        zk = str(row["zone_key"])
        stmt = select(TransformedZoneData).where(TransformedZoneData.zone_key == zk)
        existing = db.execute(stmt).scalar_one_or_none()

        payload: dict[str, Any] = {
            "zone_key": zk,
            "zona": str(row["zona"]),
            "poblacion": _float_or_none(row.get("poblacion")),
            "ingreso": _float_or_none(row.get("ingreso")),
            "educacion": _float_or_none(row.get("educacion")),
            "negocios": _float_or_none(row.get("negocios")),
            "superficie_km2": _float_or_none(row.get("superficie_km2")),
            "densidad_poblacional": _float_or_none(row.get("densidad_poblacional")),
            "indice_desarrollo": _float_or_none(row.get("indice_desarrollo")),
            "source_dataset_id": source_dataset_id,
            "updated_at": now,
        }

        if existing is None:
            payload["created_at"] = now
            db.add(TransformedZoneData(**payload))
            rows_inserted += 1
        else:
            for k, v in payload.items():
                setattr(existing, k, v)
            rows_updated += 1

    return rows_inserted, rows_updated


def _float_or_none(v: Any) -> float | None:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None
