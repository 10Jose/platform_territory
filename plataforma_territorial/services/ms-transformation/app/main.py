from fastapi import FastAPI
from app.routers import zones

app = FastAPI(title="Data Transformation Service")

app.include_router(zones.router, tags=["Zones"])


@app.get("/health")
def health():
    return {"status": "ok"}