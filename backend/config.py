from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://scriptsense:scriptsense@localhost:5432/scriptsense"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    gcs_bucket_name: str = "scriptsense-exams"
    google_application_credentials: str = ""

    groq_api_key: str = ""
    anthropic_api_key: str = ""

    environment: str = "development"

    class Config:
        env_file = (".env", "../.env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
