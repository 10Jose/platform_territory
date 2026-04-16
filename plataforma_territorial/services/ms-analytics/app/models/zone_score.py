from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.infrastructure.db import Base
from datetime import datetime

class ZoneScore(Base):
    __tablename__ = "zone_scores"

    id = Column(Integer, primary_key=True, index=True)
    zona = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    detalle = Column(JSON)