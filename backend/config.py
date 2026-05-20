from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    database_url: str = "sqlite:///./crypto_hub.db"
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_api_key: str = ""
    crawler_interval_minutes: int = 5
    cors_origins: str = "http://localhost:5173,http://localhost:4173,https://crypto-hub.cryptohubwork.workers.dev,https://crypto-hub-b3f.pages.dev,https://cryptohub.dpdns.org"
    jwt_secret: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    frontend_url: str = "http://localhost:5173"
    resend_api_key: str = ""
    app_url: str = "http://localhost:5173"
    bcrypt_rounds: int = 12
    login_rate_limit_per_minute: int = 10
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    @property
    def cors_origins_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
