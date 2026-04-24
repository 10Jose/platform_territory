<<<<<<< HEAD
=======
"""
Cliente de **ms-audit**: envío de eventos con reintentos y cola local en ``/tmp/audit_fallback.jsonl``.

Usado tras cargas, sincronizaciones y errores en el BFF.
"""
>>>>>>> origin/Miguel
import httpx
import os
import logging
import asyncio
import json
from pathlib import Path

logger = logging.getLogger(__name__)

AUDIT_SERVICE_URL = os.getenv("AUDIT_SERVICE_URL", "http://ms-audit:8000")
LOCAL_AUDIT_FALLBACK = Path("/tmp/audit_fallback.jsonl")
MAX_RETRIES = 3
RETRY_DELAY = 1.0

class AuditClient:
<<<<<<< HEAD
=======
    """Abstrae ``POST /events`` en el microservicio de auditoría."""

>>>>>>> origin/Miguel
    async def log_event(self, event_type: str, data: dict, retry_count: int = 0):
        """Registra evento de auditoría con reintentos y fallback local."""
        event = {
            "event_type": event_type,
            "data": data,
            "retry_count": retry_count
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{AUDIT_SERVICE_URL}/events",
                    json=event,
                    timeout=5.0
                )
                if response.status_code == 200:
                    logger.info(f"Evento de auditoría registrado: {event_type}")
                    return True
                else:
                    raise Exception(f"Status {response.status_code}")
        except Exception as e:
            logger.warning(f"Error al enviar evento de auditoría (intento {retry_count + 1}): {e}")
            
            if retry_count < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY * (retry_count + 1))
                return await self.log_event(event_type, data, retry_count + 1)
            else:
                # Fallback: guardar localmente
                await self._save_locally(event)
                return False

    async def _save_locally(self, event: dict):
        """Guarda evento localmente cuando el servicio de auditoría no está disponible."""
        try:
            with open(LOCAL_AUDIT_FALLBACK, "a") as f:
                f.write(json.dumps(event) + "\n")
            logger.warning(f"Evento guardado localmente en {LOCAL_AUDIT_FALLBACK}")
        except Exception as e:
            logger.error(f"Error al guardar evento localmente: {e}")

    async def retry_pending_events(self):
        """Reintenta enviar eventos pendientes guardados localmente."""
        if not LOCAL_AUDIT_FALLBACK.exists():
            return 0
        
        retried = 0
        remaining = []
        
        with open(LOCAL_AUDIT_FALLBACK, "r") as f:
            for line in f:
                event = json.loads(line.strip())
                success = await self.log_event(
                    event["event_type"], 
                    event["data"], 
                    retry_count=0
                )
                if not success:
                    remaining.append(line)
                else:
                    retried += 1
        
        # Reescribir solo los que fallaron
        with open(LOCAL_AUDIT_FALLBACK, "w") as f:
            f.writelines(remaining)
        
        logger.info(f"Reintentos de auditoría: {retried} exitosos, {len(remaining)} pendientes")
        return retried
