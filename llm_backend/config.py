
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):

    host: str = Field(default="127.0.0.1", env="LLM_HOST")
    port: int = Field(default=8000, env="LLM_PORT")
    debug: bool = Field(default=False, env="LLM_DEBUG")

    llm_host: Optional[str] = Field(default=None, env="LLM_HOST")
    llm_port: Optional[int] = Field(default=None, env="LLM_PORT")
    llm_debug: Optional[bool] = Field(default=None, env="LLM_DEBUG")

    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_api_url: str = Field(
        default="https://api.openai.com/v1",
        env="OPENAI_API_URL"
    )
    openai_model: str = Field(default="gpt-3.5-turbo", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")

    # Ollama Configuration
    ollama_host: str = Field(default="localhost", env="OLLAMA_HOST")
    ollama_port: int = Field(default=11434, env="OLLAMA_PORT")
    ollama_model: str = Field(default="llama3.2", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(default=30, env="OLLAMA_TIMEOUT")
    ollama_max_tokens: int = Field(default=4000, env="OLLAMA_MAX_TOKENS")
    ollama_temperature: float = Field(default=0.7, env="OLLAMA_TEMPERATURE")

    rate_limit_requests_per_minute: int = Field(default=60, env="RATE_LIMIT_RPM")
    rate_limit_tokens_per_minute: int = Field(default=100000, env="RATE_LIMIT_TPM")

    rate_limit_rpm: Optional[int] = Field(default=None, env="RATE_LIMIT_RPM")
    rate_limit_tpm: Optional[int] = Field(default=None, env="RATE_LIMIT_TPM")

    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")

    database_url: str = Field(default="sqlite:///./llm_chat.db", env="DATABASE_URL")

    trading_config_path: str = Field(default="config.json", env="TRADING_CONFIG_PATH")

    alpha_vantage_api_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    news_api_key: Optional[str] = Field(default=None, env="NEWS_API_KEY")
    reddit_client_id: Optional[str] = Field(default=None, env="REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = Field(default=None, env="REDDIT_CLIENT_SECRET")

    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

def validate_required_settings():
    settings = get_settings()

    # OpenAI API key is now optional since we're using Ollama
    # if not settings.openai_api_key:
    #     raise ValueError("OPENAI_API_KEY environment variable is required")

    return True