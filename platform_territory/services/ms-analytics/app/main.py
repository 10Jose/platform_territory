from fastapi import FastAPI
from app.routers import ranking, indicators
from app.routers.score import router as score_router
from app.infrastructure.database import engine, Base
from app.domain import models
from app.domain.zone_score import ZoneScore

app = FastAPI(
    title="Analytics Service",
    description="Indicadores, ranking, scoring y comparador territorial.",
    version="1.0.0",
)

app.include_router(ranking.router, prefix="/analytics", tags=["Analytics"])
app.include_router(indicators.router, prefix="/analytics", tags=["Analytics"])
app.include_router(score_router, prefix="/analytics", tags=["Scoring"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
