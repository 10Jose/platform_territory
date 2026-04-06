from __future__ import annotations

from typing import Any

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
