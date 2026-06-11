from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Railway автоматически задаёт DATABASE_URL для PostgreSQL
    # Локально падбэк на SQLite
    database_url: str = "sqlite+aiosqlite:///./optimai.db"
    secret_key: str = "supersecretkey-change-in-production-32chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    app_name: str = "OptimAI Platform"
    app_version: str = "1.0.0"
    debug: bool = False

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        # Railway даёт postgresql://, нужно postgresql+asyncpg://
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    class Config:
        env_file = ".env"


settings = Settings()
