<<<<<<< HEAD
=======
"""
Capa de persistencia: motor SQLAlchemy async y sesiones por petición.

``DATABASE_URL`` debe usar el dialecto ``postgresql+asyncpg://`` para coincidir con ``AsyncSession``.
"""
>>>>>>> origin/Miguel
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://transform_user:transform_pass@db-transformation:5432/transform_db")

<<<<<<< HEAD
# Engine asíncrono
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Fábrica de sesiones asíncronas
=======
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

>>>>>>> origin/Miguel
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

<<<<<<< HEAD
# Base para los modelos
Base = declarative_base()

# Dependencia que inyecta una sesión en los endpoints
async def get_db():
=======
Base = declarative_base()


async def get_db():
    """Dependencia FastAPI: una sesión de BD por request, cerrada al terminar."""
>>>>>>> origin/Miguel
    async with AsyncSessionLocal() as session:
        yield session