"""Cliente HTTP hacia **ms-analytics** (ranking e indicadores)."""
from app.services.base_client import BaseClient
import os


class AnalyticsClient(BaseClient):
    """Extiende ``BaseClient`` con la URL base del servicio de analítica."""

    def __init__(self):
        base_url = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8003")
        super().__init__(base_url)

    async def get_ranking(self):
        """``GET /analytics/ranking``."""
        return await self.get("/analytics/ranking")

    async def get_indicators(self, zone_code: str = None):
        """``GET /analytics/`` — indicadores por zona."""
        if zone_code:
            return await self.get(f"/analytics/?zone_code={zone_code}")
        return await self.get("/analytics/")

    async def calculate_indicators(self):
        """``POST /analytics/calculate``."""
        return await self.post("/analytics/calculate")

    async def compare_zones(self, zones: str):
        """``GET /analytics/compare?zones=...``."""
        return await self.get(f"/analytics/compare?zones={zones}")