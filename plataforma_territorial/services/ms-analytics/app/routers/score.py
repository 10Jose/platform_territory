import httpx
from fastapi import APIRouter
from datetime import datetime
from app.infrastructure.db import SessionLocal
from app.models.zone_score import ZoneScore

router = APIRouter()


# 🔹 Simulación (luego conectas con otros MS)
def obtener_pesos():
    return {
        "poblacion": 0.3,
        "ingresos": 0.3,
        "educacion": 0.2,
        "competencia": 0.2
    }


def calcular_score(indicadores, pesos):
    total = 0
    detalle = {}

    for key in indicadores:
        valor = indicadores[key]
        peso = pesos.get(key, 0)

        parcial = valor * peso
        detalle[key] = {
            "valor": valor,
            "peso": peso,
            "resultado": parcial
        }

        total += parcial

    score_final = total * 100
    return score_final, detalle


@router.post("/analytics/score")
def calcular_score_endpoint(data: dict):

    zona = data.get("zona")
    indicadores = data.get("indicadores")

    pesos = obtener_pesos()

    score, detalle = calcular_score(indicadores, pesos)

    resultado = {
        "zona": zona,
        "score": score,
        "fecha": datetime.now(),
        "detalle": detalle
    }

    # 🔥 GUARDAR EN DB
    db = SessionLocal()

    nuevo_score = ZoneScore(
        zona=zona,
        score=score,
        detalle=detalle
    )

    db.add(nuevo_score)
    db.commit()
    db.refresh(nuevo_score)

    # 🔥 EVENTO DE AUDITORÍA (AQUÍ SÍ)
    try:
        httpx.post("http://ms-audit:8000/audit", json={
            "evento": "score_calculado",
            "zona": zona,
            "score": score,
            "fecha": str(datetime.now())
        })
    except:
        print("No se pudo enviar evento de auditoría")

    db.close()

    return resultado