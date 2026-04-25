"""
Pipeline Service (HU-14)

- Orquesta ejecución secuencial de:
  ingestion → transformation → scoring → ranking → audit
- Maneja errores parciales
- Registra auditoría en cada paso
- Mantiene estado del pipeline
"""

import time
import logging
from typing import List, Dict, Any

from app.services.transformation_client import TransformationClient
from app.services.analytics_client import AnalyticsClient
from app.services.audit_client import AuditClient

logger = logging.getLogger(__name__)


class PipelineService:
    """Encapsula la lógica de ejecución del pipeline."""

    def __init__(self):
        self.transformation_client = TransformationClient()
        self.analytics_client = AnalyticsClient()
        self.audit_client = AuditClient()

        self._status = {
            "status": "idle",
            "last_run": None,
            "steps": []
        }

    def get_status(self) -> Dict[str, Any]:
        """Devuelve estado actual del pipeline."""
        return self._status

    async def run(self, user: str) -> Dict[str, Any]:
        """
        Ejecuta pipeline completo.

        Flujo:
        1. Transformation (incluye normalización en tu HU-17)
        2. Scoring
        3. Ranking

        - Si un paso falla → se detiene
        - Registra auditoría por paso
        """

        self._status = {
            "status": "running",
            "last_run": time.time(),
            "steps": []
        }

        steps_result: List[Dict[str, Any]] = []

        # -------- STEP 1: TRANSFORMATION --------
        try:
            logger.info("Pipeline step: transformation")
            result = await self.transformation_client.sync_zones()

            await self.audit_client.log_event("PIPELINE_TRANSFORMATION_SUCCESS", result)

            steps_result.append({"step": "transformation", "status": "success"})
        except Exception as e:
            return await self._handle_failure("transformation", e, steps_result)

        # -------- STEP 2: SCORING --------
        try:
            logger.info("Pipeline step: scoring")
            result = await self.analytics_client.post("/analytics/score")

            await self.audit_client.log_event("PIPELINE_SCORING_SUCCESS", result)

            steps_result.append({"step": "scoring", "status": "success"})
        except Exception as e:
            return await self._handle_failure("scoring", e, steps_result)

        # -------- STEP 3: RANKING --------
        try:
            logger.info("Pipeline step: ranking")
            result = await self.analytics_client.get_ranking()

            await self.audit_client.log_event("PIPELINE_RANKING_SUCCESS", result)

            steps_result.append({"step": "ranking", "status": "success"})
        except Exception as e:
            return await self._handle_failure("ranking", e, steps_result)

        # -------- SUCCESS --------
        self._status["status"] = "completed"
        self._status["steps"] = steps_result

        await self.audit_client.log_event("PIPELINE_COMPLETED", {
            "user": user,
            "steps": steps_result
        })

        return {
            "status": "completed",
            "steps": steps_result
        }

    async def _handle_failure(self, step: str, error: Exception, steps_result: List[Dict]):
        """Manejo centralizado de errores (SRP)."""

        logger.error(f"Pipeline failed at {step}: {error}")

        await self.audit_client.log_event(f"PIPELINE_{step.upper()}_FAILED", {
            "error": str(error)
        })

        steps_result.append({"step": step, "status": "failed"})

        self._status["status"] = "failed"
        self._status["steps"] = steps_result

        return {
            "status": "failed",
            "failed_step": step,
            "error": str(error),
            "steps": steps_result
        }