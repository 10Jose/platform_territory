from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.exceptions import NoDataError, NoModelError, TrainingError, UpstreamError
from app.infrastructure.database import get_db
from app.services.ml_service import MLService

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TrainRequest(BaseModel):
    algorithm: str = "random_forest"
    target_variable: str = "score"
    test_size: float = 0.2


class TrainResponse(BaseModel):
    status: str
    experiment_id: int
    algorithm: str
    metrics: dict
    model_version: str


class PredictionResponse(BaseModel):
    zone_code: str
    zone_name: str
    predicted_value: float
    prediction_label: str
    actual_score: Optional[float] = None
    difference: Optional[float] = None
    model_version: str


class BatchPredictionResponse(BaseModel):
    total: int
    predicted: int
    failed: int
    predictions: list
    errors: list


class CleanupResponse(BaseModel):
    deleted: int
    days: int


def get_ml_service(db: AsyncSession = Depends(get_db)) -> MLService:
    return MLService(db)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/train", response_model=TrainResponse)
async def train_model(
    request: TrainRequest = TrainRequest(),
    service: MLService = Depends(get_ml_service),
):
    """Entrena un modelo de ML."""
    try:
        return await service.train_model(request.dict())
    except (NoDataError, NoModelError, TrainingError, UpstreamError):
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/predict/{zone_code}", response_model=PredictionResponse)
async def predict_zone(
    zone_code: str,
    service: MLService = Depends(get_ml_service),
):
    """Criterio 1, 2, 4, 7: predice el potencial de una zona."""
    try:
        return await service.predict_zone(zone_code)
    except (NoModelError, NoDataError):
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.post("/predict-all", response_model=BatchPredictionResponse)
async def predict_all_zones(
    service: MLService = Depends(get_ml_service),
):
    """Criterio 3: predice todas las zonas disponibles."""
    try:
        return await service.predict_all_zones()
    except (NoModelError, NoDataError):
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/predictions/stats")
async def get_predictions_stats(
    service: MLService = Depends(get_ml_service),
):
    """Criterio 5: estadísticas de predicciones."""
    try:
        return await service.get_prediction_stats()
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.delete("/predictions/old", response_model=CleanupResponse)
async def cleanup_old_predictions(
    days: int = Query(30, ge=0, description="Edad mínima en días para borrar"),
    service: MLService = Depends(get_ml_service),
):
    """Criterio 6: elimina predicciones más antiguas que N días."""
    try:
        return await service.cleanup_old_predictions(days)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/experiments")
async def get_experiments(service: MLService = Depends(get_ml_service)):
    """Lista los experimentos de ML."""
    try:
        return await service.get_experiments()
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")


@router.get("/predictions")
async def get_predictions(
    zone_code: Optional[str] = None,
    service: MLService = Depends(get_ml_service),
):
    """Lista predicciones realizadas (filtro opcional por zona)."""
    try:
        return await service.get_predictions(zone_code)
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")
