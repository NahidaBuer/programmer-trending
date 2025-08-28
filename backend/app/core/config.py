from typing import Optional
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic v2 / pydantic-settings v2 配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    # Application
    app_name: str = Field(default="Programmer Trending Backend")
    app_version: str = Field(default="0.1.0")
    debug: bool = Field(default=False)

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./programmer_trending.db")

    # AI Service (Google Gemini)
    google_api_key: Optional[str] = Field(default=None)
    gemini_model: str = Field(default="gemini-2.5-flash")
    ai_summary_max_length: int = Field(default=200)
    ai_summary_max_retries: int = Field(default=3)

    # AI Rate Limiting
    ai_rate_limit_per_minute: int = Field(
        default=10
    )  # gemini-flash: 10, gemini-flash-lite: 15
    ai_rate_limit_per_day: int = Field(
        default=250
    )  # gemini-flash: 250, gemini-flash-lite: 1000
    ai_enable_rate_limiting: bool = Field(default=True)
    ai_rate_limit_retry_delay: int = Field(default=60)  # 达到限制后等待秒数

    # Summary Generator
    summary_concurrency: int = Field(
        default=1
    )  # 摘要生成并发度, 免费模型速率限制, 只能串行了

    # Crawler
    crawl_interval_minutes: int = Field(default=120)

    # Task Scheduler
    enable_crawl_scheduler: bool = Field(default=True)  # 是否启用定时爬虫任务
    enable_summary_scheduler: bool = Field(default=True)  # 是否启用定时AI摘要任务

    # CORS Configuration
    cors_allow_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173"
    )
    cors_allow_credentials: bool = Field(default=False)

    # Logging
    log_level: str = Field(default="DEBUG")
    
    # Security - HTTP Basic Auth
    admin_username: str = Field(default="admin")
    admin_password: str = Field(default="changeme")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
