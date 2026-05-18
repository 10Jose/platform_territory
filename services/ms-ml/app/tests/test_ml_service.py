"""Tests unitarios para MLService (HU-20 - Predicción).

Cubre los 7 criterios de aceptación:
    1. Predicción individual de una zona.
    2. Comparación con score real (actual_score, difference).
    3. Predicción batch.
    4. Clasificación por percentiles sobre datos reales.
    5. Estadísticas de predicciones.
    6. Limpieza de predicciones antiguas.
    7. Persistencia (save_prediction es invocado).

Los tests usan mocks (AsyncMock / MagicMock) sobre las dependencias
externas (repositorio, analytics_client, audit_client, trainer) para
no requerir BD ni red.
"""
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Permitir importar el paquete `app` cuando los tests corren desde la raíz
SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SERVICE_ROOT not in sys.path:
    sys.path.insert(0, SERVICE_ROOT)


@pytest.fixture
def mock_trainer():
    trainer = MagicMock()
    trainer.predict.return_value = [42.5]
    trainer.get_algorithm_name.return_value = "random_forest"
    return trainer


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_active_model = AsyncMock(
        return_value={
            "id": 1,
            "experiment_id": 1,
            "model_name": "TerritorialPredictor_random_forest",
            "model_version": "v1.0",
            "storage_path": "/app/models/model_1.pkl",
            "trained_at": None,
        }
    )
    repo.save_prediction = AsyncMock(return_value=1)
    repo.get_all_prediction_values = AsyncMock(return_value=[])
    repo.count_predictions = AsyncMock(return_value=0)
    repo.count_predictions_by_label = AsyncMock(return_value={})
    repo.get_last_prediction_at = AsyncMock(return_value=None)
    repo.delete_old_predictions = AsyncMock(return_value=0)
    repo.get_predictions = AsyncMock(return_value=[])
    repo.get_experiments = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_analytics():
    client = MagicMock()
    client.get_zone_data = AsyncMock(
        return_value={
            "zone_code": "Z01",
            "zone_name": "Zona Uno",
            "score": 40.0,
            "contributions": {
                "population": 10,
                "income": 8,
                "education": 6,
                "competition_penalty": 2,
            },
        }
    )
    client.get_all_zones_scores = AsyncMock(
        return_value=[
            {
                "zone_code": "Z01",
                "zone_name": "Zona Uno",
                "score": 40.0,
                "contributions": {
                    "population": 10, "income": 8,
                    "education": 6, "competition_penalty": 2,
                },
            },
            {
                "zone_code": "Z02",
                "zone_name": "Zona Dos",
                "score": 30.0,
                "contributions": {
                    "population": 5, "income": 4,
                    "education": 3, "competition_penalty": 1,
                },
            },
        ]
    )
    return client


@pytest.fixture
def mock_audit():
    client = MagicMock()
    client.log_event = AsyncMock(return_value="trace-id")
    return client


@pytest.fixture
def service(mock_trainer, mock_repo, mock_analytics, mock_audit):
    """Construye MLService con todas las dependencias mockeadas."""
    # Evita que el constructor toque disco al cargar modelo
    with patch(
        "app.services.ml_service.MLService._load_model_from_disk", return_value="MODEL"
    ):
        from app.services.ml_service import MLService
        svc = MLService(
            db=MagicMock(),
            trainer=mock_trainer,
            repository=mock_repo,
            analytics_client=mock_analytics,
            audit_client=mock_audit,
        )
        # Forzar que haya modelo en memoria
        svc._current_model = "MODEL"
        return svc


# ---------------------------------------------------------------------------
# Criterio 1, 2, 7: predicción individual + comparación + persistencia
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_predict_zone_returns_predicted_value(service):
    result = await service.predict_zone("Z01")

    assert result["zone_code"] == "Z01"
    assert result["zone_name"] == "Zona Uno"
    assert result["predicted_value"] == 42.5  # del mock_trainer
    assert result["model_version"] == "v1.0"


@pytest.mark.asyncio
async def test_predict_zone_includes_actual_score_and_difference(service):
    """Criterio 2: la predicción complementa el análisis (compara con score real)."""
    result = await service.predict_zone("Z01")

    assert result["actual_score"] == 40.0
    # 42.5 - 40.0 = 2.5
    assert result["difference"] == 2.5


@pytest.mark.asyncio
async def test_predict_zone_persists_in_db(service, mock_repo):
    """Criterio 7: las predicciones se guardan en BD."""
    await service.predict_zone("Z01")
    mock_repo.save_prediction.assert_awaited_once()
    payload = mock_repo.save_prediction.await_args.args[0]
    assert payload["zone_code"] == "Z01"
    assert payload["prediction_value"] == 42.5
    assert payload["model_id"] == 1


@pytest.mark.asyncio
async def test_predict_zone_logs_audit_event(service, mock_audit):
    await service.predict_zone("Z01")
    mock_audit.log_event.assert_awaited_once()
    kwargs = mock_audit.log_event.await_args.kwargs
    assert kwargs["event_type"] == "prediction_generated"
    assert kwargs["reference_id"] == "Z01"


@pytest.mark.asyncio
async def test_predict_zone_no_model_raises(mock_trainer, mock_repo, mock_analytics, mock_audit):
    """Si no hay modelo activo ni archivo en disco, debe lanzar NoModelError."""
    from app.services.ml_service import MLService
    from app.core.exceptions import NoModelError

    mock_repo.get_active_model = AsyncMock(return_value=None)
    with patch(
        "app.services.ml_service.MLService._load_model_from_disk", return_value=None
    ):
        svc = MLService(
            db=MagicMock(),
            trainer=mock_trainer,
            repository=mock_repo,
            analytics_client=mock_analytics,
            audit_client=mock_audit,
        )
        svc._current_model = None
        with pytest.raises(NoModelError):
            await svc.predict_zone("Z01")


# ---------------------------------------------------------------------------
# Criterio 3: predicción batch
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_predict_all_zones_returns_summary(service):
    result = await service.predict_all_zones()

    assert result["total"] == 2
    assert result["predicted"] == 2
    assert result["failed"] == 0
    assert len(result["predictions"]) == 2
    assert {p["zone_code"] for p in result["predictions"]} == {"Z01", "Z02"}


@pytest.mark.asyncio
async def test_predict_all_zones_logs_batch_audit(service, mock_audit):
    await service.predict_all_zones()
    types = [c.kwargs["event_type"] for c in mock_audit.log_event.await_args_list]
    assert "prediction_batch_generated" in types


@pytest.mark.asyncio
async def test_predict_all_zones_empty_raises(service, mock_analytics):
    from app.core.exceptions import NoDataError

    mock_analytics.get_all_zones_scores = AsyncMock(return_value=[])
    with pytest.raises(NoDataError):
        await service.predict_all_zones()


# ---------------------------------------------------------------------------
# Criterio 4: clasificación por percentiles sobre datos reales
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_label_uses_percentiles_when_data_available(service, mock_repo):
    # Distribución conocida: p25=20, p75=40
    mock_repo.get_all_prediction_values = AsyncMock(
        return_value=[10.0, 20.0, 30.0, 40.0, 50.0]
    )

    assert await service._get_opportunity_label(45.0) == "Alta"
    assert await service._get_opportunity_label(25.0) == "Media"
    assert await service._get_opportunity_label(15.0) == "Baja"


@pytest.mark.asyncio
async def test_label_unclassified_when_insufficient_data(service, mock_repo):
    mock_repo.get_all_prediction_values = AsyncMock(return_value=[10.0])
    assert await service._get_opportunity_label(15.0) == "Sin clasificar"


# ---------------------------------------------------------------------------
# Criterio 5: estadísticas
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_prediction_stats_with_data(service, mock_repo):
    mock_repo.count_predictions = AsyncMock(return_value=3)
    mock_repo.count_predictions_by_label = AsyncMock(
        return_value={"Alta": 1, "Media": 1, "Baja": 1}
    )
    mock_repo.get_all_prediction_values = AsyncMock(return_value=[10.0, 20.0, 30.0])
    mock_repo.get_last_prediction_at = AsyncMock(return_value=None)

    stats = await service.get_prediction_stats()

    assert stats["total"] == 3
    assert stats["by_label"] == {"Alta": 1, "Media": 1, "Baja": 1}
    assert stats["distribution"]["min"] == 10.0
    assert stats["distribution"]["max"] == 30.0
    assert stats["distribution"]["mean"] == 20.0


@pytest.mark.asyncio
async def test_get_prediction_stats_empty(service, mock_repo):
    stats = await service.get_prediction_stats()
    assert stats["total"] == 0
    assert stats["distribution"]["mean"] is None


# ---------------------------------------------------------------------------
# Criterio 6: limpieza
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cleanup_old_predictions(service, mock_repo, mock_audit):
    mock_repo.delete_old_predictions = AsyncMock(return_value=7)

    result = await service.cleanup_old_predictions(days=30)

    assert result == {"deleted": 7, "days": 30}
    mock_repo.delete_old_predictions.assert_awaited_once_with(30)
    types = [c.kwargs["event_type"] for c in mock_audit.log_event.await_args_list]
    assert "predictions_cleanup" in types


@pytest.mark.asyncio
async def test_cleanup_negative_days_raises(service):
    with pytest.raises(ValueError):
        await service.cleanup_old_predictions(days=-5)
