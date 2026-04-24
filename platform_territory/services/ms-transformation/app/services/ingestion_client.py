"""
Cliente HTTP hacia **ms-ingestion**: solo lectura de metadatos y del CSV en disco.

La transformación no modifica nada en ingesta; únicamente consume ``GET /data/datasets`` y ``GET /data/file/{id}``.
"""
from typing import Optional

import httpx
import os
import logging

logger = logging.getLogger(__name__)


class IngestionClient:
    """Encapsula las llamadas al servicio de ingesta definidas por la API de ``ms-ingestion``."""

    def __init__(self):
        self.base_url = os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000")

    async def get_datasets(
        self, skip: int = 0, limit: int = 100, validation_status: Optional[str] = None
    ):
        """
        Lista datasets ordenados por fecha de carga (más reciente primero en ingesta).

        Parameters
        ----------
        validation_status:
            Por ejemplo ``"valid"`` o ``"partial"`` para filtrar el estado de validación.
        """
        params = {"skip": skip, "limit": limit}
        if validation_status:
            params["validation_status"] = validation_status

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/data/datasets",
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def get_dataset_file(self, dataset_id: int) -> bytes:
        """Devuelve el contenido binario del CSV asociado al id de carga en ingesta."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/data/file/{dataset_id}")
            response.raise_for_status()
            return response.content