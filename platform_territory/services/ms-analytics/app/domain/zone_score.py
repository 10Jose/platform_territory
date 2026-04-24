from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.infrastructure.database import Base


class ZoneScore(Base):
    __tablename__ = "zone_scores"

    id = Column(Integer, primary_key=True, index=True)
    zona = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    detalle = Column(JSON)
