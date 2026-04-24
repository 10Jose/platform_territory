"""
Mock mínimo de ms-ingestion para pruebas locales / demos (HU-07).
No modificar datos reales: solo sirve JSON + CSV de ejemplo.

Uso:
  uvicorn mock_ingestion_server:app --host 0.0.0.0 --port 8001
"""

from fastapi import FastAPI
from fastapi.responses import Response

# CSV válido según columnas requeridas (zona, poblacion, ingreso, educacion, negocios)
SAMPLE_CSV = (
    "zona,poblacion,ingreso,educacion,negocios,superficie_km2\n"
    "Centro,5000,45000,14,40,2.5\n"
    "Norte,1200,30000,10,15,10.0\n"
)

app = FastAPI(title="mock-ms-ingestion", version="0.0.1")

_LATEST_ID = 1001


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/datasets/latest")
def datasets_latest() -> dict:
    """Último dataset cargado (simulado)."""
    return {
        "id": _LATEST_ID,
        "filename": "zonas_demo.csv",
        "row_count": 2,
    }


@app.get("/datasets/{dataset_id}/download")
def download_csv(dataset_id: int | str) -> Response:
    """Descarga el CSV del dataset (mismo contenido de ejemplo para cualquier id)."""
    return Response(
        content=SAMPLE_CSV.encode("utf-8"),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="zonas_demo.csv"'},
    )
