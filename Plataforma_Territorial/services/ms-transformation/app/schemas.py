from __future__ import annotations

import datetime as dt
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Respuesta estándar de salud (HU-08 / comprobaciones)."""

    model_config = ConfigDict(json_schema_extra={"example": {"status": "ok"}})

    status: Literal["ok"] = Field(
        ...,
        description="Estado del servicio; 'ok' si responde correctamente.",
    )


class SyncZonesResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Sincronización completada",
                "transformation_run_id": 1,
                "source_dataset_id": "1001",
                "rows_read": 2,
                "rows_inserted": 2,
                "rows_updated": 0,
                "rules_version": "1.0.0",
                "rules_applied": {"version": "1.0.0", "required_columns": ["zona", "poblacion"]},
                "completed_at": "2026-04-05T12:00:00Z",
            }
        }
    )

    message: str = Field(..., description="Resumen del proceso")
    transformation_run_id: int
    source_dataset_id: str | None
    rows_read: int
    rows_inserted: int
    rows_updated: int
    rules_version: str
    rules_applied: dict[str, Any]
    completed_at: dt.datetime | None
