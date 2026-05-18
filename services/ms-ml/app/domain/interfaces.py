from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class TrainingData:
    """datos de entrenamiento."""
    features: list
    target: list
    feature_names: list
    target_name: str


@dataclass
class ModelInfo:
    """información del modelo."""
    id: int
    name: str
    version: str
    algorithm: str
    features_used: list
    target_variable: str
    evaluation_metric: str
    metric_value: float
    is_active: bool


@dataclass
class PredictionData:
    """resultado de predicción."""
    zone_code: str
    zone_name: str
    predicted_value: float
    confidence_score: Optional[float]
    model_version: str


class IModelTrainer(ABC):
    """Interfaz para entrenador de modelos."""

    @abstractmethod
    def train(self, features: list, target: list) -> Any:
        ...

    @abstractmethod
    def predict(self, model: Any, features: list) -> list:
        ...

    @abstractmethod
    def evaluate(self, model: Any, features: list, target: list) -> Dict[str, float]:
        ...

    @abstractmethod
    def get_algorithm_name(self) -> str:
        ...


class IMLRepository(ABC):
    """Interfaz para repositorio de ML."""

    @abstractmethod
    async def save_experiment(self, experiment_data: Dict) -> int:
        ...

    @abstractmethod
    async def save_model(self, model_data: Dict) -> int:
        ...

    @abstractmethod
    async def save_prediction(self, prediction_data: Dict) -> int:
        ...

    @abstractmethod
    async def get_active_model(self) -> Optional[Dict]:
        ...

    @abstractmethod
    async def get_experiments(self) -> list:
        ...

    @abstractmethod
    async def get_predictions(self, zone_code: Optional[str] = None) -> list:
        ...

    @abstractmethod
    async def get_all_prediction_values(self) -> List[float]:
        """Lista de prediction_value de todas las predicciones (criterio 4)."""
        ...

    @abstractmethod
    async def count_predictions(self) -> int:
        ...

    @abstractmethod
    async def count_predictions_by_label(self) -> Dict[str, int]:
        ...

    @abstractmethod
    async def get_last_prediction_at(self) -> Optional[datetime]:
        ...

    @abstractmethod
    async def delete_old_predictions(self, days: int) -> int:
        """Elimina predicciones más antiguas que `days`. Devuelve eliminadas."""
        ...
