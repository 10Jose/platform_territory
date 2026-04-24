"""
Capa de persistencia: motor SQLAlchemy async y sesiones por petición.

``DATABASE_URL`` debe usar el dialecto ``postgresql+asyncpg://`` para coincidir con ``AsyncSession``.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://transform_user:transform_pass@db-transformation:5432/transform_db")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    """Dependencia FastAPI: una sesión de BD por request, cerrada al terminar."""
    async with AsyncSessionLocal() as session:
        yield session