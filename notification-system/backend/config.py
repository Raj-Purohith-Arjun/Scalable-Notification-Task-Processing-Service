import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # db config
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@db:5432/taskdb",
    )
    SYNC_DATABASE_URL: str = os.getenv(
        "SYNC_DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/taskdb",
    )
    # redis config
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    REDIS_QUEUE: str = "task_queue"
    REDIS_CACHE_TTL: int = 300

    # app config
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
