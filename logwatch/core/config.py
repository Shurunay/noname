"""Настройки приложения.

Все значения читаются из переменных окружения (или файла .env) с префиксом
LOGWATCH_. В коде нет ни одного секрета — только значения по умолчанию
для безопасных параметров.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevelName = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Конфигурация LogWatch."""

    model_config = SettingsConfigDict(
        env_prefix="LOGWATCH_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Логирование самого приложения ---
    log_level: LogLevelName = "INFO"
    log_dir: Path = Path("logs")
    log_max_bytes: int = Field(default=1_000_000, gt=0)
    log_backup_count: int = Field(default=5, ge=0)

    # --- Алерты ---
    alert_error_threshold: int = Field(default=10, gt=0)
    alert_window_seconds: int = Field(default=60, gt=0)

    # --- Telegram (необязательно: без токена алерты пишутся только в консоль) ---
    telegram_bot_token: SecretStr | None = None
    telegram_chat_id: str | None = None

    # --- REST API ---
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, gt=0, lt=65536)

    @field_validator("telegram_bot_token", "telegram_chat_id", mode="before")
    @classmethod
    def _empty_to_none(cls, value: object) -> object:
        """Пустая строка в .env означает «не задано»."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def telegram_enabled(self) -> bool:
        """Telegram-алерты включены, только если заданы и токен, и chat_id."""
        return bool(self.telegram_bot_token and self.telegram_chat_id)


@lru_cache
def get_settings() -> Settings:
    """Вернуть настройки (создаются один раз и кэшируются)."""
    return Settings()
