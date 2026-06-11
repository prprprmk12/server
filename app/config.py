from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./optimai.db"
    secret_key: str = "supersecretkey-change-in-production-32chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    app_name: str = "OptimAI Platform"
    app_version: str = "1.0.0"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
