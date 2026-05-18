from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from pydantic import BaseModel

from app.services.ml_client import MLClient
from app.routers.auth import get_current_user
from app.domain.models import User

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


class ExperimentResponse(BaseModel):
    id: int
    name: str
    algorithm: str
    target_variable: str
    evaluation_metric: str
    metric_value: float
    status: str
    executed_at: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/train", response_model=TrainResponse)
async def train_model(
    request: TrainRequest = TrainRequest(),
    current_user: User = Depends(get_current_user),
):
    """Entrena un modelo de ML."""
    try:
        client = MLClient()
        return await client.train_model(request.dict())
    except Exception as e:
        raise HTTPException(500, detail=f"Error al entrenar modelo: {str(e)}")


@router.get("/predict/{zone_code}", response_model=PredictionResponse)
async def predict_zone(
    zone_code: str,
    current_user: User = Depends(get_current_user),
):
    """Criterio 1, 2: predice el potencial de una zona y compara con score real."""
    try:
        client = MLClient()
        return await client.predict_zone(zone_code)
    except Exception as e:
        raise HTTPException(500, detail=f"Error al predecir: {str(e)}")


@router.post("/predict-all", response_model=BatchPredictionResponse)
async def predict_all_zones(
    current_user: User = Depends(get_current_user),
):
    """Criterio 3: predice todas las zonas."""
    try:
        client = MLClient()
        return await client.predict_all_zones()
    except Exception as e:
        raise HTTPException(500, detail=f"Error al predecir todas las zonas: {str(e)}")


@router.get("/predictions/stats")
async def get_predictions_stats(
    current_user: User = Depends(get_current_user),
):
    """Criterio 5: estadísticas de predicciones."""
    try:
        client = MLClient()
        return await client.get_prediction_stats()
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener estadísticas: {str(e)}")


@router.delete("/predictions/old", response_model=CleanupResponse)
async def delete_old_predictions(
    days: int = Query(30, ge=0, description="Edad mínima en días"),
    current_user: User = Depends(get_current_user),
):
    """Criterio 6: limpia predicciones más antiguas que N días."""
    try:
        client = MLClient()
        return await client.delete_old_predictions(days)
    except Exception as e:
        raise HTTPException(500, detail=f"Error al limpiar predicciones: {str(e)}")


@router.get("/experiments", response_model=List[ExperimentResponse])
async def get_experiments(current_user: User = Depends(get_current_user)):
    """Obtiene todos los experimentos de ML."""
    try:
        client = MLClient()
        return await client.get_experiments()
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener experimentos: {str(e)}")


@router.get("/predictions")
async def get_predictions(
    zone_code: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Obtiene predicciones realizadas (filtro opcional por zona)."""
    try:
        client = MLClient()
        return await client.get_predictions(zone_code)
    except Exception as e:
        raise HTTPException(500, detail=f"Error al obtener predicciones: {str(e)}")
