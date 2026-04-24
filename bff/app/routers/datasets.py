"""Proxy de listado de datasets desde **ms-ingestion** (``GET /data/datasets``)."""
from fastapi import APIRouter, HTTPException
from app.services.ingestion_client import IngestionClient

router = APIRouter()

@router.get("/")
async def get_datasets(skip: int = 0, limit: int = 100):
    """Devuelve metadatos de cargas (paginado)."""
    try:
        client = IngestionClient()
        datasets = await client.get_datasets(skip, limit)
        return datasets
    except Exception as e:
        raise HTTPException(500, detail=str(e))