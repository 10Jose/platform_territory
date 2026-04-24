<<<<<<< HEAD
import httpx
import os

class TransformationClient:
=======
"""
Cliente del BFF hacia **ms-transformation**: listado de zonas y ejecución HU-07 (``POST /sync/zones``).
"""
import httpx
import os


class TransformationClient:
    """Llamadas tipadas a los endpoints públicos del servicio de transformación."""

>>>>>>> origin/Miguel
    def __init__(self):
        self.base_url = os.getenv("TRANSFORMATION_SERVICE_URL", "http://ms-transformation:8000")

    async def get_zones(self, skip: int = 0, limit : int = 100):
<<<<<<< HEAD
=======
        """``GET /zones/`` con paginación."""
>>>>>>> origin/Miguel
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/zones/", params={"skip": skip, "limit": limit})
            response.raise_for_status()
            return response.json()


    async def sync_zones(self):
<<<<<<< HEAD
        async with httpx.AsyncClient() as client:
=======
        """Ejecuta pipeline HU-07 (timeout extendido 120s)."""
        async with httpx.AsyncClient(timeout=120.0) as client:
>>>>>>> origin/Miguel
            response = await client.post(f"{self.base_url}/sync/zones")
            response.raise_for_status()
            return response.json()