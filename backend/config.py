from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./crypto_hub.db"
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_api_key: str = ""
    crawler_interval_minutes: int = 5
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:4173",
        "https://crypto-hub.cryptohubwork.workers.dev",
    ]
    jwt_secret: str = "cryptohub-dev-secret-key-change-in-prod"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
