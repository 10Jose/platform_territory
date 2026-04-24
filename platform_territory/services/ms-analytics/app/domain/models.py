from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Index
from sqlalchemy.sql import func
from app.infrastructure.database import Base


class IndicatorResult(Base):
    __tablename__ = "indicator_results"

    id = Column(Integer, primary_key=True, index=True)
    zone_code = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)
    transformation_run_id = Column(Integer, nullable=False)
    population_indicator = Column(Float, nullable=True)
    income_indicator = Column(Float, nullable=True)
    education_indicator = Column(Float, nullable=True)
    competition_indicator = Column(Float, nullable=True)
    composite_indicator_json = Column(JSON, nullable=True)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_indicator_results_zone_code', 'zone_code'),
    )
