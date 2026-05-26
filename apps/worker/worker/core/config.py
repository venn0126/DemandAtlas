from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    worker_env: str = "development"
    worker_log_level: str = "INFO"
    redis_url: str = "redis://127.0.0.1:6379/0"
    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/demand_atlas"
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "DemandAtlas/0.1"
    reddit_base_url: str = "https://oauth.reddit.com"
    reddit_token_url: str = "https://www.reddit.com/api/v1/access_token"
    reddit_fetch_limit_per_source: int = 12
    reddit_comment_limit_per_post: int = 12

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
