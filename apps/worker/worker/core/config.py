from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    worker_env: str = "development"
    worker_log_level: str = "INFO"
    redis_url: str = "redis://127.0.0.1:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
