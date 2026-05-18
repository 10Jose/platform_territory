from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.services.comparison.comparator import ZoneComparator
import logging
import uuid

from app.domain.interfaces import (
    IScoringCalculator,
    IScoringRepository,
    ComparisonResult
)

from app.services.configuration_client import ConfigurationClient
from app.services.scoring.calculator import ScoringCalculator
from app.services.scoring.repository import ScoringRepository
from app.services.analytics_service import AnalyticsService
from app.services.audit_client import AuditClient

from app.domain.models import IndicatorResult, ZoneScore

from app.core.exceptions import NoDataError

logger = logging.getLogger(__name__)


class ScoringService:

    def __init__(
        self,
        db: AsyncSession,
        calculator: Optional[IScoringCalculator] = None,
        repository: Optional[IScoringRepository] = None,
        config_client: Optional[ConfigurationClient] = None,
        audit_client: Optional[AuditClient] = None
    ):
        self.db = db
        self.calculator = calculator or ScoringCalculator()
        self.repository = repository or ScoringRepository(db)
        self.config_client = config_client or ConfigurationClient()
        self.audit_client = audit_client or AuditClient("ms-analytics")
        # ✅ HU-21: ml_client eliminado de aquí — la combinación
        #           score + predicción la hace el BFF, no este servicio.

    async def _get_active_weights(self) -> Dict[str, float]:
        try:
            return await self.config_client.get_active_weights()
        except Exception as e:
            logger.warning(f"Error obteniendo pesos, usando defaults: {e}")
            return {
                "population": 25,
                "income": 25,
                "education": 25,
                "competition": 25
            }

    async def calculate_scores(
        self,
        user_id: Optional[int] = None,
        username: Optional[str] = None
    ) -> Dict:

        trace_id = str(uuid.uuid4())

        try:
            scaled_data = await self.repository.get_scaled_data()

            if not scaled_data:
                logger.info("No hay datos reescalados. Ejecutando scaling automático...")

                stmt = select(IndicatorResult).limit(1)
                result = await self.db.execute(stmt)
                has_indicators = result.scalar_one_or_none() is not None

                if not has_indicators:
                    raise NoDataError("No existen indicadores calculados")

                analytics_service = AnalyticsService(self.db)
                await analytics_service.run_scaling()

                scaled_data = await self.repository.get_scaled_data()

                if not scaled_data:
                    raise NoDataError("No se pudieron generar datos escalados")

            await self.db.execute(delete(ZoneScore))
            await self.db.commit()

            weights = await self._get_active_weights()

            execution_id = await self.repository.save_execution({
                "weights": weights,
                "formula_version": "1.0.0"
            })

            scores = await self.calculator.calculate(scaled_data, weights)

            saved_count = await self.repository.save_scores(execution_id, scores)

            await self.repository.update_execution_status(execution_id, "completed")

            # Reentrenar modelo ML en background (fallo silencioso)
            try:
                await self._auto_train_ml_model()
            except Exception as e:
                logger.warning(f"ML deshabilitado temporalmente: {e}")

            return {
                "status": "completed",
                "execution_id": execution_id,
                "zones_processed": saved_count,
                "weights_used": weights,
                "trace_id": trace_id
            }

        except Exception as e:
            logger.exception("Error calculando scoring")
            if 'execution_id' in locals():
                await self.repository.update_execution_status(execution_id, "failed")
            raise Exception(f"Error al calcular scoring: {str(e)}")

    async def _auto_train_ml_model(self):
        """Intenta reentrenar el modelo ML tras un cálculo. Fallo silencioso."""
        try:
            import httpx
            ml_url = "http://ms-ml:8000"
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{ml_url}/ml/train",
                    json={"algorithm": "random_forest"}
                )
                logger.info(f"Respuesta ML train: {response.status_code}")
        except Exception as e:
            logger.warning(f"ML no disponible: {e}")

    async def get_scores(
        self,
        zone_code: Optional[str] = None
    ) -> List[Dict]:
        """
        Retorna los scores analíticos puros desde la BD.
        ✅ HU-21: NO llama a ms-ml aquí. La combinación score+predicción
                  se hace en el BFF vía /scoring/scores-with-predictions.
        """
        try:
            query = select(ZoneScore).order_by(ZoneScore.score_value.desc())

            if zone_code:
                query = query.where(ZoneScore.zone_code == zone_code)

            result = await self.db.execute(query)
            scores = result.scalars().all()

            response = []
            for score in scores:
                try:
                    score_value = float(score.score_value or 0)
                except Exception:
                    score_value = 0

                try:
                    population = float(score.population_contribution or 0)
                except Exception:
                    population = 0

                try:
                    income = float(score.income_contribution or 0)
                except Exception:
                    income = 0

                try:
                    education = float(score.education_contribution or 0)
                except Exception:
                    education = 0

                try:
                    competition = float(score.competition_penalty or 0)
                except Exception:
                    competition = 0

                response.append({
                    "id": score.id,
                    "zone_code": str(score.zone_code or ""),
                    "zone_name": str(score.zone_name or ""),
                    "score": score_value,
                    "opportunity_level": str(score.opportunity_level or ""),
                    "contributions": {
                        "population": population,
                        "income": income,
                        "education": education,
                        "competition_penalty": competition
                    },
                    "weights_used": {
                        "population": 25,
                        "income": 25,
                        "education": 25,
                        "competition": 25
                    },
                    "calculated_at": (
                        str(score.created_at) if score.created_at else None
                    )
                })

            return response

        except Exception as e:
            logger.exception("Error obteniendo scores")
            raise Exception(f"Error al obtener scores: {str(e)}")

    async def get_score_details(
        self,
        zone_code: str
    ) -> Optional[Dict]:
        scores = await self.get_scores(zone_code)
        return scores[0] if scores else None

    async def get_ranking(
        self,
        limit: Optional[int] = None,
        opportunity_level: Optional[str] = None
    ) -> List[Dict]:
        try:
            scores = await self.get_scores()

            if opportunity_level:
                scores = [
                    s for s in scores
                    if s["opportunity_level"] == opportunity_level
                ]

            scores = sorted(
                scores,
                key=lambda x: x.get("score", 0),
                reverse=True
            )

            if limit:
                scores = scores[:limit]

            for idx, score in enumerate(scores):
                score["rank_position"] = idx + 1

            return scores

        except Exception as e:
            logger.exception("Error obteniendo ranking")
            raise Exception(f"Error al obtener ranking: {str(e)}")

    async def compare_zones(
        self,
        zone_codes: List[str]
    ) -> ComparisonResult:
        comparator = ZoneComparator(self.db)
        return await comparator.compare(zone_codes)