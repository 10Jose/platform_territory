<<<<<<< HEAD
from typing import Optional
=======
from __future__ import annotations

from typing import Any

>>>>>>> origin/Miguel
import httpx
from pydantic import BaseModel, ConfigDict, Field

from app.config import settings


class LatestDatasetPayload(BaseModel):
    """Contrato flexible con ms-ingestion: último dataset cargado."""

    model_config = ConfigDict(extra="ignore")

    id: int | str = Field(..., description="Identificador de la carga en ingestion")
    filename: str | None = None
    row_count: int | None = None


class IngestionClient:
<<<<<<< HEAD

    def __init__(self):
        self.base_url = os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000")

    async def get_datasets(
            self,
            skip: int = 0,
            limit: int = 100,
            validation_status: Optional[str] = None
    ) -> list:
        """
        Obtiene la lista de datasets cargados.

        Args:
            skip: Número de registros a saltar
            limit: Máximo de registros
            validation_status: Filtro por estado de validación

        Returns:
            Lista de datasets
        """
        params = {"skip": skip, "limit": limit}
        if validation_status:
            params["validation_status"] = validation_status

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/data/datasets",
                params=params
            )
            response.raise_for_status()
            return response.json()

    async def get_dataset_file(self, dataset_id: int) -> bytes:
        """
        Descarga el archivo CSV de un dataset.

        Args:
            dataset_id: ID del dataset

        Returns:
            Contenido del archivo en bytes
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/data/file/{dataset_id}")
            response.raise_for_status()
            return response.content
=======
    def __init__(self, base_url: str | None = None) -> None:
        self._base = (base_url or settings.ingestion_base_url).rstrip("/")

    def fetch_latest_dataset(self) -> LatestDatasetPayload:
        url = f"{self._base}{settings.ingestion_latest_path}"
        try:
            r = httpx.get(url, timeout=60.0)
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeError(f"No se pudo obtener el último dataset desde ingestion ({url}): {e}") from e
        data: Any = r.json()
        return LatestDatasetPayload.model_validate(data)

    def download_csv_bytes(self, dataset_id: int | str) -> bytes:
        path = settings.ingestion_download_template.format(dataset_id=dataset_id)
        url = f"{self._base}{path}"
        try:
            r = httpx.get(url, timeout=120.0)
            r.raise_for_status()
        except httpx.HTTPError as e:
            raise RuntimeError(f"No se pudo descargar el CSV desde ingestion ({url}): {e}") from e
        return r.content
>>>>>>> origin/Miguel
