from app.services.base_client import BaseClient
import os
from typing import Optional, Dict, List


class MLClient(BaseClient):
    """Cliente HTTP para ms-ml."""

    def __init__(self):
        base_url = os.getenv("ML_SERVICE_URL", "http://ms-ml:8000")
        super().__init__(base_url)

    async def train_model(self, config: Optional[Dict] = None) -> Dict:
        """Entrena un modelo de ML."""
        return await self.post("/ml/train", config or {})

    async def predict_zone(self, zone_code: str) -> Dict:
        """Criterio 1, 2: predice el potencial de una zona (incluye score real)."""
        return await self.get(f"/ml/predict/{zone_code}")

    async def predict_all_zones(self) -> Dict:
        """Criterio 3: predice todas las zonas."""
        return await self.post("/ml/predict-all", {})

    async def get_prediction_stats(self) -> Dict:
        """Criterio 5: estadísticas agregadas de predicciones."""
        return await self.get("/ml/predictions/stats")

    async def delete_old_predictions(self, days: int = 30) -> Dict:
        """Criterio 6: limpia predicciones más antiguas que N días."""
        return await self.delete(f"/ml/predictions/old?days={days}")

    async def get_experiments(self) -> List[Dict]:
        return await self.get("/ml/experiments")

    async def get_predictions(self, zone_code: Optional[str] = None) -> List[Dict]:
        if zone_code:
            return await self.get(f"/ml/predictions?zone_code={zone_code}")
        return await self.get("/ml/predictions")
