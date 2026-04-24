from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.post("/audit")
def registrar_evento(data: dict):
    return {
        "mensaje": "Evento registrado",
        "data": data,
        "fecha": datetime.now()
    }