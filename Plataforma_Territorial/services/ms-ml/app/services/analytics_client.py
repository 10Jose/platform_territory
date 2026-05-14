import httpx
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class AnalyticsClient:
    """Cliente HTTP para ms-analytics."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv(
            "ANALYTICS_SERVICE_URL", "http://ms-analytics:8000"
        )

    async def get_training_data(self) -> Dict:
        """Obtiene datos de entrenamiento desde ms-analytics.

        Lanza:
            ValueError("not_found") si analytics responde 404 (no hay scores).
            RuntimeError(detalle) para cualquier otro fallo de comunicación.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/analytics/training-data"
                )
                if response.status_code == 404:
                    raise ValueError("not_found")
                response.raise_for_status()
                return response.json()
        except ValueError:
            raise
        except httpx.TimeoutException as e:
            logger.error(f"Timeout consultando training-data: {e}")
            raise RuntimeError("timeout consultando ms-analytics")
        except httpx.ConnectError as e:
            logger.error(f"Error de conexión con ms-analytics: {e}")
            raise RuntimeError("no se pudo conectar con ms-analytics")
        except Exception as e:
            logger.error(f"Error obteniendo datos de entrenamiento: {e}")
            raise RuntimeError(str(e))

    async def get_zone_data(self, zone_code: str) -> Dict:
        """Obtiene datos de una zona específica (incluye score real y contributions)."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/scoring/scores/{zone_code}"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo datos de zona {zone_code}: {e}")
            raise

    async def get_all_zones_scores(self) -> List[Dict]:
        """Lista todas las zonas con su score y contribuciones (criterio 3: batch)."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/scoring/scores")
                response.raise_for_status()
                return response.json() or []
        except Exception as e:
            logger.error(f"Error obteniendo lista de scores: {e}")
            raise
