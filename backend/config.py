from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./crypto_hub.db"
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"
    coingecko_api_key: str = ""
    crawler_interval_minutes: int = 5
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:4173",
        "https://crypto-hub.pages.dev",
    ]
    jwt_secret: str = "cryptohub-dev-secret-key-change-in-prod"
    render_frontend_url: str = "https://crypto-hub.pages.dev"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
