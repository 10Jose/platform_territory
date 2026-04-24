<<<<<<< HEAD
from app.services.base_client import BaseClient
import os

class AnalyticsClient(BaseClient):
=======
"""Cliente HTTP hacia **ms-analytics** (ranking e indicadores)."""
from app.services.base_client import BaseClient
import os


class AnalyticsClient(BaseClient):
    """Extiende ``BaseClient`` con la URL base del servicio de analítica."""

>>>>>>> origin/Miguel
    def __init__(self):
        base_url = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8003")
        super().__init__(base_url)

    async def get_ranking(self):
<<<<<<< HEAD
        return await self.get("/analytics/ranking")

    async def get_indicators(self, zone_id: str = None):
=======
        """``GET /analytics/ranking``."""
        return await self.get("/analytics/ranking")

    async def get_indicators(self, zone_id: str = None):
        """``GET /analytics/indicators`` o con sufijo de zona si aplica."""
>>>>>>> origin/Miguel
        if zone_id:
            return await self.get(f"/analytics/indicators/{zone_id}")
        return await self.get("/analytics/indicators")