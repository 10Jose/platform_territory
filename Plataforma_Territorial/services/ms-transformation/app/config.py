from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5433/db_transformation"
    ingestion_base_url: str = "http://localhost:8001"
    ingestion_latest_path: str = "/datasets/latest"
    ingestion_download_template: str = "/datasets/{dataset_id}/download"

    # Reglas versionadas para trazabilidad
    transformation_rules_version: str = "1.0.0"


settings = Settings()
