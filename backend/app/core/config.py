from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_DIR / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_environment: str = "development"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    log_dir: Path = BACKEND_DIR / "logs"

    database_path: Path = BACKEND_DIR / "paperhub.db"
    upload_dir: Path = BACKEND_DIR / "uploads"
    chroma_dir: Path = BACKEND_DIR / "chroma"
    model_cache_dir: Path = BACKEND_DIR / "model-cache"
    embedding_model: str = "BAAI/bge-m3"

    ai_provider: str = "deepseek"
    deepseek_api_key: Optional[SecretStr] = None
    deepseek_model: str = "deepseek-v4-flash"
    deepseek_base_url: str = "https://api.deepseek.com/chat/completions"
    deepseek_timeout_seconds: float = 60.0
    deepseek_max_retries: int = 2
    deepseek_retry_backoff_seconds: float = 1.0

    upload_max_mb: int = 50
    pdf_parse_timeout_seconds: float = 60.0
    pdf_parse_retries: int = 1

    upload_rate_limit: str = "5/minute"
    chat_rate_limit: str = "30/minute"
    analysis_rate_limit: str = "10/minute"
    rate_limit_storage_uri: str = "memory://"
    trust_proxy_headers: bool = False

    cors_origins: str = ""
    allowed_hosts: str = "localhost,127.0.0.1,testserver"
    healthcheck_deepseek_network: bool = False
    healthcheck_timeout_seconds: float = 3.0

    @property
    def upload_max_bytes(self) -> int:
        return self.upload_max_mb * 1024 * 1024

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def allowed_host_list(self) -> list[str]:
        return [item.strip() for item in self.allowed_hosts.split(",") if item.strip()]

    def resolve_path(self, path: Path) -> Path:
        expanded_path = path.expanduser()
        if not expanded_path.is_absolute():
            expanded_path = PROJECT_DIR / expanded_path
        return expanded_path.resolve()

    def get_deepseek_api_key(self) -> str:
        if self.deepseek_api_key is None:
            return ""
        return self.deepseek_api_key.get_secret_value().strip()


@lru_cache
def get_settings() -> Settings:
    return Settings()
