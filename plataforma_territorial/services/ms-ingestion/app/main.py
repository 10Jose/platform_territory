from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import data
from app.infrastructure.database import engine, Base
from app.domain import models

app = FastAPI(title="Data Ingestion Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router, prefix="/data", tags=["Data"])


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)