from pydantic import BaseModel, model_validator
from typing import Optional
from datetime import datetime


class ParametersBase(BaseModel):
    name: Optional[str] = "default"
    weight_population: float = 0.25
    weight_income: float = 0.30
    weight_education: float = 0.25
    weight_business: float = 0.20
    threshold_high: float = 0.7
    threshold_medium: float = 0.5
    max_population_density: float = 3000.0
    max_average_income: float = 100000.0
    max_education_level: float = 20.0
    max_commercial_presence: float = 1.0

    @model_validator(mode="after")
    def weights_must_sum_one(self):
        total = round(
            self.weight_population
            + self.weight_income
            + self.weight_education
            + self.weight_business,
            2,
        )
        if total != 1.0:
            raise ValueError(
                f"Los pesos deben sumar 1.0 (100%). Suma actual: {total}"
            )
        if self.threshold_high <= self.threshold_medium:
            raise ValueError(
                "threshold_high debe ser mayor que threshold_medium"
            )
        return self


class ParametersCreate(ParametersBase):
    pass


class ParametersUpdate(ParametersBase):
    pass


class ParametersResponse(ParametersBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
