from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TransformedZoneData(Base):
    __tablename__ = "transformed_zone_data"
    __table_args__ = (UniqueConstraint("zone_key", name="uq_transformed_zone_zone_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    zona: Mapped[str] = mapped_column(String(512), nullable=False)
    poblacion: Mapped[float | None] = mapped_column(Float, nullable=True)
    ingreso: Mapped[float | None] = mapped_column(Float, nullable=True)
    educacion: Mapped[float | None] = mapped_column(Float, nullable=True)
    negocios: Mapped[float | None] = mapped_column(Float, nullable=True)
    superficie_km2: Mapped[float | None] = mapped_column(Float, nullable=True)
    densidad_poblacional: Mapped[float | None] = mapped_column(Float, nullable=True)
    indice_desarrollo: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_dataset_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TransformationRun(Base):
    __tablename__ = "transformation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")
    rules_version: Mapped[str] = mapped_column(String(32), nullable=False)
    rules_applied: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=lambda: {})
    source_dataset_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    rows_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
