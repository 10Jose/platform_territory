from app.services.base_client import BaseClient
import os


class ConfigurationClient(BaseClient):
    def __init__(self):
        base_url = os.getenv("CONFIGURATION_SERVICE_URL", "http://ms-configuration:8000")
        super().__init__(base_url)

    async def get_parameters(self):
        return await self.get("/config/parameters")

    async def update_parameters(self, data: dict):
        return await self.put("/config/parameters", data)
