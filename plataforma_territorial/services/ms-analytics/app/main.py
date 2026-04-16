from fastapi import FastAPI

from app.routers import ranking
from app.routers import score

# 🔥 IMPORTANTE
from app.infrastructure.db import engine, Base
from app.models.zone_score import ZoneScore

app = FastAPI(title="Analytics Service")

# 🔥 CREA LAS TABLAS
Base.metadata.create_all(bind=engine)

app.include_router(ranking.router, prefix="/analytics", tags=["Analytics"])
app.include_router(score.router)

@app.get("/health")
def health():
    return {"status": "ok"}