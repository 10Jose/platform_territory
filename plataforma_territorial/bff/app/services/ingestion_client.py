import httpx
import os
from fastapi import UploadFile, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class IngestionClient:
    def __init__(self):
        self.base_url = os.getenv("INGESTION_SERVICE_URL", "http://ms-ingestion:8000")

    async def upload(self, file: UploadFile, uploaded_by: Optional[str] = None):
        contents = await file.read()

        async with httpx.AsyncClient() as client:
            files = {"file": (file.filename, contents, file.content_type)}
            headers = {}
            if uploaded_by:
                headers["X-User-Id"] = uploaded_by

            response = await client.post(f"{self.base_url}/data/load", files=files, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_datasets(self, skip: int = 0, limit: int = 100, validation_status: Optional[str] = None):
        params = {"skip": skip, "limit": limit}
        if validation_status:
            params["validation_status"] = validation_status

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/data/datasets", params=params)
            response.raise_for_status()
            return response.json()