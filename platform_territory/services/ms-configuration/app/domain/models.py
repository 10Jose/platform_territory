from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, func
from app.infrastructure.database import Base


class ModelParameters(Base):
    __tablename__ = "model_parameters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default="default")
    is_active = Column(Boolean, default=True)

    # Pesos (deben sumar 1.0 = 100%)
    weight_population = Column(Float, nullable=False, default=0.25)
    weight_income = Column(Float, nullable=False, default=0.30)
    weight_education = Column(Float, nullable=False, default=0.25)
    weight_business = Column(Float, nullable=False, default=0.20)

    # Umbrales de clasificación
    threshold_high = Column(Float, nullable=False, default=0.7)
    threshold_medium = Column(Float, nullable=False, default=0.5)

    # Normalización máxima
    max_population_density = Column(Float, nullable=False, default=3000.0)
    max_average_income = Column(Float, nullable=False, default=100000.0)
    max_education_level = Column(Float, nullable=False, default=20.0)
    max_commercial_presence = Column(Float, nullable=False, default=1.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
