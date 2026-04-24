"""
Persistencia del BFF: solo modelos de **autenticación** (usuarios).

La URL por defecto apunta a ``db-auth`` en Docker Compose.
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("AUTH_DATABASE_URL", "postgresql+asyncpg://auth_user:auth_pass@db-auth:5432/auth_db")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    """Sesión SQLAlchemy async por petición (inyectada en rutas con ``Depends``)."""
    async with AsyncSessionLocal() as session:
        yield session