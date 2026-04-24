from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database import get_db
from app.domain.models import ModelParameters
from app.schemas.parameters import ParametersCreate, ParametersUpdate, ParametersResponse

router = APIRouter()


@router.get("/parameters", response_model=ParametersResponse)
async def get_active_parameters(db: AsyncSession = Depends(get_db)):
    """Retorna la configuración activa."""
    result = await db.execute(
        select(ModelParameters).where(ModelParameters.is_active.is_(True)).limit(1)
    )
    params = result.scalar_one_or_none()
    if not params:
        # Crear configuración por defecto si no existe
        params = ModelParameters()
        db.add(params)
        await db.commit()
        await db.refresh(params)
    return params


@router.post("/parameters", response_model=ParametersResponse, status_code=201)
async def create_parameters(data: ParametersCreate, db: AsyncSession = Depends(get_db)):
    """Crea nueva configuración y desactiva las anteriores."""
    # Desactivar todas las configuraciones previas
    result = await db.execute(
        select(ModelParameters).where(ModelParameters.is_active.is_(True))
    )
    for old in result.scalars().all():
        old.is_active = False

    params = ModelParameters(**data.model_dump())
    params.is_active = True
    db.add(params)
    await db.commit()
    await db.refresh(params)
    return params


@router.put("/parameters", response_model=ParametersResponse)
async def update_parameters(data: ParametersUpdate, db: AsyncSession = Depends(get_db)):
    """Actualiza la configuración activa."""
    result = await db.execute(
        select(ModelParameters).where(ModelParameters.is_active.is_(True)).limit(1)
    )
    params = result.scalar_one_or_none()
    if not params:
        raise HTTPException(status_code=404, detail="No hay configuración activa")

    for key, value in data.model_dump().items():
        setattr(params, key, value)

    await db.commit()
    await db.refresh(params)
    return params
