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
    
    # AI Service
    deepseek_api_key: Optional[str] = Field(default=None)
    
    # Crawler
    crawl_interval_minutes: int = Field(default=120)
    summary_concurrency: int = Field(default=3)
    
    # Logging
    log_level: str = Field(default="INFO")


@lru_cache()
def get_settings() -> Settings:
    return Settings()