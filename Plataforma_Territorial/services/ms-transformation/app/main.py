from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import TransformationRun, TransformedZoneData  # noqa: F401
from app.routers import sync
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="ms-transformation", version="1.0.0", lifespan=lifespan)
app.include_router(sync.router)


@app.get("/health", response_model=HealthResponse, summary="Health")
def health() -> HealthResponse:
    return HealthResponse(status="ok")
