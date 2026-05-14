import os
import pickle
import uuid
import logging
from typing import Dict, List, Optional

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NoDataError, NoModelError, TrainingError, UpstreamError
from app.domain.interfaces import IMLRepository, IModelTrainer
from app.repositories.ml_repository import MLRepository
from app.services.analytics_client import AnalyticsClient
from app.services.audit_client import AuditClient
from app.services.model_trainer import RandomForestTrainer

logger = logging.getLogger(__name__)


class MLService:
    """Servicio de Machine Learning para HU-20 (Predicción).

    Cumple los 7 criterios de aceptación:
        1. Predicción individual de una zona.
        2. Comparación con score real (predicted_value vs actual_score, difference).
        3. Predicción batch de todas las zonas.
        4. Clasificación por percentiles sobre datos reales (consulta a BD).
        5. Estadísticas de predicciones.
        6. Limpieza de predicciones antiguas.
        7. Persistencia en BD (PredictionResult).
    """

    def __init__(
        self,
        db: AsyncSession,
        trainer: Optional[IModelTrainer] = None,
        repository: Optional[IMLRepository] = None,
        analytics_client: Optional[AnalyticsClient] = None,
        audit_client: Optional[AuditClient] = None,
    ):
        self.db = db
        self.trainer = trainer or RandomForestTrainer()
        self.repository = repository or MLRepository(db)
        self.analytics_client = analytics_client or AnalyticsClient()
        self.audit_client = audit_client or AuditClient()
        self._model_path = "/app/models"
        os.makedirs(self._model_path, exist_ok=True)
        self._current_model = self._load_model_from_disk()

    # ------------------------------------------------------------------
    # Persistencia del modelo en disco
    # ------------------------------------------------------------------

    def _save_model_to_disk(self, model, model_id: int) -> str:
        path = f"{self._model_path}/model_{model_id}.pkl"
        with open(path, "wb") as f:
            pickle.dump(model, f)
        return path

    def _load_model_from_disk(self):
        if not os.path.exists(self._model_path):
            return None
        files = [f for f in os.listdir(self._model_path) if f.endswith(".pkl")]
        if not files:
            return None
        latest_file = sorted(files)[-1]
        path = f"{self._model_path}/{latest_file}"
        with open(path, "rb") as f:
            return pickle.load(f)

    # ------------------------------------------------------------------
    # Entrenamiento (HU-19)
    # ------------------------------------------------------------------

    async def train_model(self, config: Optional[Dict] = None) -> Dict:
        config = config or {}
        algorithm = config.get("algorithm", "random_forest")
        target_variable = config.get("target_variable", "score")

        try:
            training_data = await self.analytics_client.get_training_data()
        except ValueError:
            raise NoDataError("No hay datos de scoring disponibles. Ejecuta el cálculo de scoring primero.")
        except RuntimeError as e:
            raise UpstreamError(f"ms-analytics: {e}")

        if not training_data or not training_data.get("features"):
            raise NoDataError()

        features = training_data["features"]
        target = training_data["target"]
        feature_names = training_data.get("feature_names", [])

        if algorithm == "linear_regression":
            from app.services.model_trainer import LinearRegressionTrainer
            self.trainer = LinearRegressionTrainer()
        else:
            self.trainer = RandomForestTrainer()

        try:
            model = self.trainer.train(features, target)
            self._current_model = model
        except Exception as e:
            raise TrainingError(str(e))

        metrics = self.trainer.evaluate(model, features, target)

        experiment_id = await self.repository.save_experiment(
            {
                "name": f"Experiment_{uuid.uuid4().hex[:8]}",
                "target_variable": target_variable,
                "algorithm": algorithm,
                "features_used": feature_names,
                "evaluation_metric": "r2",
                "metric_value": metrics.get("r2", 0),
            }
        )

        self._save_model_to_disk(model, experiment_id)

        model_version = f"v{experiment_id}.0"
        await self.repository.save_model(
            {
                "experiment_id": experiment_id,
                "model_name": f"TerritorialPredictor_{algorithm}",
                "model_version": model_version,
                "storage_path": f"/app/models/model_{experiment_id}.pkl",
            }
        )

        await self.audit_client.log_event(
            event_type="model_trained",
            reference_id=str(experiment_id),
            details={
                "algorithm": algorithm,
                "metrics": metrics,
                "samples": len(features),
            },
        )

        return {
            "status": "completed",
            "experiment_id": experiment_id,
            "algorithm": algorithm,
            "metrics": metrics,
            "model_version": model_version,
        }

    # ------------------------------------------------------------------
    # Criterio 1, 2, 4, 7: predicción individual
    # ------------------------------------------------------------------

    async def predict_zone(self, zone_code: str) -> Dict:
        """Predice el potencial de UNA zona. Cumple criterios 1, 2, 4, 7."""
        await self._ensure_model_loaded()

        try:
            zone_data = await self.analytics_client.get_zone_data(zone_code)
        except Exception:
            raise NoDataError()

        result = await self._predict_from_zone_data(zone_data)

        await self.audit_client.log_event(
            event_type="prediction_generated",
            reference_id=zone_code,
            details={
                "predicted_value": result["predicted_value"],
                "actual_score": result["actual_score"],
                "label": result["prediction_label"],
            },
        )

        return result

    # ------------------------------------------------------------------
    # Criterio 3: predicción batch
    # ------------------------------------------------------------------

    async def predict_all_zones(self) -> Dict:
        """Predice TODAS las zonas con score disponible."""
        await self._ensure_model_loaded()

        try:
            zones = await self.analytics_client.get_all_zones_scores()
        except Exception:
            raise NoDataError()

        if not zones:
            raise NoDataError()

        predictions: List[Dict] = []
        errors: List[Dict] = []
        for zone in zones:
            try:
                pred = await self._predict_from_zone_data(zone)
                predictions.append(pred)
            except Exception as e:
                logger.warning(
                    f"Predicción falló para zona {zone.get('zone_code')}: {e}"
                )
                errors.append(
                    {"zone_code": zone.get("zone_code"), "error": str(e)}
                )

        await self.audit_client.log_event(
            event_type="prediction_batch_generated",
            details={
                "zones_predicted": len(predictions),
                "errors": len(errors),
            },
        )

        return {
            "total": len(zones),
            "predicted": len(predictions),
            "failed": len(errors),
            "predictions": predictions,
            "errors": errors,
        }

    # ------------------------------------------------------------------
    # Criterio 5: estadísticas
    # ------------------------------------------------------------------

    async def get_prediction_stats(self) -> Dict:
        total = await self.repository.count_predictions()
        by_label = await self.repository.count_predictions_by_label()
        last_at = await self.repository.get_last_prediction_at()
        values = await self.repository.get_all_prediction_values()

        if values:
            arr = np.asarray(values, dtype=float)
            distribution = {
                "min": float(arr.min()),
                "max": float(arr.max()),
                "mean": float(arr.mean()),
                "p25": float(np.percentile(arr, 25)),
                "p50": float(np.percentile(arr, 50)),
                "p75": float(np.percentile(arr, 75)),
            }
        else:
            distribution = {
                "min": None, "max": None, "mean": None,
                "p25": None, "p50": None, "p75": None,
            }

        return {
            "total": total,
            "by_label": by_label,
            "last_prediction_at": last_at.isoformat() if last_at else None,
            "distribution": distribution,
        }

    # ------------------------------------------------------------------
    # Criterio 6: limpieza
    # ------------------------------------------------------------------

    async def cleanup_old_predictions(self, days: int = 30) -> Dict:
        if days < 0:
            raise ValueError("days debe ser >= 0")

        deleted = await self.repository.delete_old_predictions(days)

        await self.audit_client.log_event(
            event_type="predictions_cleanup",
            details={"days": days, "deleted": deleted},
        )

        return {"deleted": deleted, "days": days}

    # ------------------------------------------------------------------
    # Listados
    # ------------------------------------------------------------------

    async def get_experiments(self) -> list:
        return await self.repository.get_experiments()

    async def get_predictions(self, zone_code: Optional[str] = None) -> list:
        return await self.repository.get_predictions(zone_code)

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    async def _ensure_model_loaded(self) -> Dict:
        """Carga el modelo activo o lanza NoModelError."""
        model_info = await self.repository.get_active_model()
        if not model_info and self._current_model is None:
            raise NoModelError()

        if self._current_model is None:
            self._current_model = self._load_model_from_disk()
            if self._current_model is None:
                raise NoModelError()

        self._active_model_info = model_info
        return model_info

    async def _predict_from_zone_data(self, zone_data: Dict) -> Dict:
        """Genera predicción a partir de un dict de datos de zona.

        Comparte lógica entre predict_zone y predict_all_zones.
        Cumple criterios 1, 2, 4, 7 de HU-20.
        """
        zone_code = zone_data.get("zone_code", "")
        zone_name = zone_data.get("zone_name", "")
        contributions = zone_data.get("contributions", {}) or {}
        actual_score = zone_data.get("score")

        features = [[
            contributions.get("population", 0) or 0,
            contributions.get("income", 0) or 0,
            contributions.get("education", 0) or 0,
            contributions.get("competition_penalty", 0) or 0,
        ]]

        prediction = self.trainer.predict(self._current_model, features)[0]
        predicted_value = round(float(prediction), 2)
        label = await self._get_opportunity_label(predicted_value)

        # Criterio 2: comparación con score real
        difference: Optional[float] = None
        if isinstance(actual_score, (int, float)):
            difference = round(predicted_value - float(actual_score), 2)

        # Criterio 7: persistencia
        model_info = getattr(self, "_active_model_info", None)
        if model_info:
            await self.repository.save_prediction(
                {
                    "model_id": model_info["id"],
                    "zone_code": zone_code,
                    "zone_name": zone_name,
                    "prediction_value": predicted_value,
                    "prediction_label": label,
                    "confidence_score": None,
                }
            )

        return {
            "zone_code": zone_code,
            "zone_name": zone_name,
            "predicted_value": predicted_value,
            "prediction_label": label,
            "actual_score": (
                round(float(actual_score), 2)
                if isinstance(actual_score, (int, float))
                else None
            ),
            "difference": difference,
            "model_version": (
                model_info["model_version"] if model_info else "unknown"
            ),
        }

    async def _get_opportunity_label(self, value: float) -> str:
        """Clasifica el nivel de oportunidad usando percentiles reales (criterio 4)."""
        all_values = await self.repository.get_all_prediction_values()

        if all_values and len(all_values) >= 3:
            p75 = float(np.percentile(all_values, 75))
            p25 = float(np.percentile(all_values, 25))
            if value >= p75:
                return "Alta"
            if value >= p25:
                return "Media"
            return "Baja"

        return "Sin clasificar"
