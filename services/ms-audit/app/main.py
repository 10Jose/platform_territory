<<<<<<< HEAD
=======
"""
Servicio de **auditoría**: recibe eventos JSON del BFF (cargas, sync, errores).

Persistencia en memoria para desarrollo; en producción sustituir por base de datos.
"""
>>>>>>> origin/Miguel
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

<<<<<<< HEAD
app = FastAPI(title="Audit Service")

# Almacenamiento en memoria (en producción sería BD)
audit_events = []

=======
app = FastAPI(
    title="Audit Service",
    description="Registro de eventos de negocio para trazabilidad.",
    version="1.0.0",
)

audit_events = []


>>>>>>> origin/Miguel
class AuditEvent(BaseModel):
    event_type: str
    data: dict
    retry_count: Optional[int] = 0

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/events")
async def log_event(event: AuditEvent):
    """Registra un evento de auditoría."""
    record = {
        "id": len(audit_events) + 1,
        "event_type": event.event_type,
        "data": event.data,
        "retry_count": event.retry_count,
        "timestamp": datetime.utcnow().isoformat()
    }
    audit_events.append(record)
    logger.info(f"Evento registrado: {event.event_type}")
    return {"status": "ok", "event_id": record["id"]}

@app.get("/events")
async def get_events(limit: int = 100, event_type: Optional[str] = None):
    """Obtiene eventos de auditoría."""
    filtered = audit_events
    if event_type:
        filtered = [e for e in audit_events if e["event_type"] == event_type]
    return {"events": filtered[-limit:], "total": len(filtered)}
