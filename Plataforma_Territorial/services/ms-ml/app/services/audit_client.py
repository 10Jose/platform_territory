import httpx
import os
import uuid
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AuditClient:
    """Cliente HTTP tolerante a fallos para enviar eventos a ms-audit.

    Si ms-audit no responde, el evento se descarta silenciosamente
    (registrado a nivel WARNING) sin interrumpir el flujo principal.
    """

    def __init__(self, service_name: str = "ms-ml", base_url: Optional[str] = None):
        self.service_name = service_name
        self.base_url = base_url or os.getenv(
            "AUDIT_SERVICE_URL", "http://ms-audit:8000"
        )

    async def log_event(
        self,
        event_type: str,
        reference_id: Optional[str] = None,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        trace_id: Optional[str] = None,
    ) -> Optional[str]:
        """Envía un evento de auditoría. Devuelve trace_id o None."""
        trace_id = trace_id or str(uuid.uuid4())

        payload = {
            "trace_id": trace_id,
            "service_name": self.service_name,
            "event_type": event_type,
            "reference_id": reference_id,
            "user_id": user_id,
            "username": username,
            "details_json": details,
            "status": status,
        }

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.post(
                    f"{self.base_url}/audit/events", json=payload
                )
                response.raise_for_status()
                return trace_id
        except httpx.TimeoutException:
            logger.warning(f"Timeout enviando evento de auditoría: {event_type}")
            return None
        except httpx.ConnectError:
            logger.warning(f"Error de conexión con ms-audit: {event_type}")
            return None
        except Exception as e:
            logger.error(f"Error enviando evento de auditoría: {e}")
            return None
