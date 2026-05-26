from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Demand Atlas API"
    app_env: str = "development"
    app_debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    redis_url: str = "redis://127.0.0.1:6379/0"
    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/demand_atlas"
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "DemandAtlas/0.1"
    reddit_base_url: str = "https://oauth.reddit.com"
    reddit_token_url: str = "https://www.reddit.com/api/v1/access_token"
    reddit_fetch_limit_per_source: int = 12
    reddit_comment_limit_per_post: int = 12
    one_click_cache_max_age_seconds: int = 6 * 60 * 60
    directed_cache_max_age_seconds: int = 6 * 60 * 60
    one_click_cache_allow_partial_success: bool = False
    directed_cache_allow_partial_success: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
