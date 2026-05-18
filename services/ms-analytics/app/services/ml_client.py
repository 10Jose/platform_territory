import httpx
import logging

logger = logging.getLogger(__name__)


class MLClient:

    def __init__(self):

        self.base_url = "http://ms-ml:8000"

    async def get_prediction(self, zone_code: str):

        try:

            async with httpx.AsyncClient(
                timeout=5.0
            ) as client:

                response = await client.get(
                    f"{self.base_url}/ml/predict/{zone_code}"
                )

                if response.status_code != 200:

                    logger.warning(
                        f"ML respondió {response.status_code}"
                    )

                    return {
                        "predicted_value": 0
                    }

                data = response.json()

                return {
                    "predicted_value": float(
                        data.get("predicted_value", 0)
                    )
                }

        except Exception as e:

            logger.warning(
                f"Error conectando ML: {e}"
            )

            return {
                "predicted_value": 0
            }