from fastapi import FastAPI
from app.infrastructure.database import engine, Base
from app.routers import parameters

app = FastAPI(
    title="Configuration Service",
    description="Parámetros del modelo de analítica territorial (HU-11).",
    version="1.0.0",
)

app.include_router(parameters.router, prefix="/config", tags=["Configuration"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
