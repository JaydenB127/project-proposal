from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://expuser:exppass@localhost:5432/exptracker"
    sync_database_url: str = "postgresql+psycopg2://expuser:exppass@localhost:5432/exptracker"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "dev-secret-key"
    admin_api_key: str = "admin-dev-key"

    # App
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Rate Limiting
    rate_limit_per_minute: int = 100

    # Cache
    cache_ttl: int = 300

    # Retention
    max_runs_per_experiment: int = 100
    archive_after_days: int = 365

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
