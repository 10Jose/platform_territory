from fastapi import FastAPI
from app.routers import ranking, indicators

app = FastAPI(title="Analytics Service")

app.include_router(ranking.router, prefix="/analytics", tags=["Analytics"])
app.include_router(indicators.router, prefix="/analytics", tags=["Analytics"])

@app.get("/health")
def health():
    return {"status": "ok"}