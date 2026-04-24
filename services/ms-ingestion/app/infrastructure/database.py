<<<<<<< HEAD
=======
"""Motor SQLAlchemy async y sesiones para **db-ingestion**."""
>>>>>>> origin/Miguel
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://ingestion_user:ingestion_pass@db-ingestion:5432/ingestion_db")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base para los modelos
Base = declarative_base()

<<<<<<< HEAD
# Dependencia que inyecta una sesión en los endpoints
async def get_db():
=======
async def get_db():
    """Sesión async por petición para los routers de ``data``."""
>>>>>>> origin/Miguel
    async with AsyncSessionLocal() as session:
        yield session