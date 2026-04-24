"""
Modelos ORM para la base ``db-transformation`` (HU-07).

- ``TransformationRun``: trazabilidad de cada ejecución de transformación.
- ``TransformedZoneData``: una fila por zona (lógica de negocio); ``zone_code`` es único (upsert).
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Index, UniqueConstraint
from sqlalchemy.sql import func
from app.infrastructure.database import Base


class TransformationRun(Base):
    """Metadatos de una corrida de transformación vinculada a un ``dataset_load_id`` en ingesta."""

    __tablename__ = "transformation_runs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_load_id = Column(Integer, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="pending")
    rules_applied = Column(JSON, nullable=True)
    output_version = Column(String, nullable=True)


class TransformedZoneData(Base):
    """Indicadores por zona tras aplicar reglas de transformación (salida analítica)."""

    __tablename__ = "transformed_zone_data"

    id = Column(Integer, primary_key=True, index=True)
    transformation_run_id = Column(Integer, ForeignKey("transformation_runs.id"), nullable=False, index=True)
    zone_code = Column(String, nullable=False, index=True)
    zone_name = Column(String, nullable=False, index=True)
    population_density = Column(Integer, nullable=False)
    average_income = Column(Integer, nullable=False)
    education_level = Column(Integer, nullable=False)
    economic_activity_index = Column(Float, nullable=True)
    commercial_presence_index = Column(Float, nullable=True)
    other_variables_json = Column(JSON, nullable=True)

    __table_args__ = (
        UniqueConstraint("zone_code", name="uq_transformed_zone_zone_code"),
        Index('ix_transformed_zone_run_code', 'transformation_run_id', 'zone_code'),
        Index('ix_transformed_zone_run_name', 'transformation_run_id', 'zone_name'),
    )