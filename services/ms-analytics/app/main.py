<<<<<<< HEAD
from fastapi import FastAPI
from app.routers import ranking, indicators

app = FastAPI(title="Analytics Service")
=======
"""
Microservicio de **analítica**: agrega datos desde transformación (zonas) y expone ranking e indicadores.
"""
from fastapi import FastAPI
from app.routers import ranking, indicators

app = FastAPI(
    title="Analytics Service",
    description="Indicadores agregados y ranking de oportunidad territorial.",
    version="1.0.0",
)
>>>>>>> origin/Miguel

app.include_router(ranking.router, prefix="/analytics", tags=["Analytics"])
app.include_router(indicators.router, prefix="/analytics", tags=["Analytics"])

<<<<<<< HEAD
=======

>>>>>>> origin/Miguel
@app.get("/health")
def health():
    return {"status": "ok"}