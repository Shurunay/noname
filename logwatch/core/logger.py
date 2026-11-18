"""Сквозное логирование самого приложения LogWatch.

Логи разделяются на два потока:
- logs/info.log  — штатные события (DEBUG/INFO/WARNING);
- logs/error.log — сбои (ERROR/CRITICAL).
Дополнительно все сообщения выводятся в консоль (stderr) — это нужно для
`docker logs`. Файлы ротируются по размеру (RotatingFileHandler).
"""

import logging
import sys
from logging.handlers import RotatingFileHandler

from logwatch.core.config import Settings

APP_LOGGER_NAME = "logwatch"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


class MaxLevelFilter(logging.Filter):
    """Пропускает только записи с уровнем строго ниже заданного."""

    def __init__(self, max_level: int) -> None:
        super().__init__()
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < self.max_level


def _file_handler(settings: Settings, filename: str) -> RotatingFileHandler:
    return RotatingFileHandler(
        settings.log_dir / filename,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )


def setup_logging(settings: Settings) -> logging.Logger:
    """Настроить логгер приложения: консоль + ротируемые файлы INFO и ERROR."""
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT)

    # Консоль: всё, начиная с уровня из настроек (stderr не мешает выводу CLI)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(settings.log_level)

    # Поток штатных событий: всё, что ниже ERROR
    info_handler = _file_handler(settings, "info.log")
    info_handler.setLevel(settings.log_level)
    info_handler.addFilter(MaxLevelFilter(logging.ERROR))

    # Поток сбоев: ERROR и CRITICAL
    error_handler = _file_handler(settings, "error.log")
    error_handler.setLevel(logging.ERROR)

    logger = logging.getLogger(APP_LOGGER_NAME)
    logger.setLevel(logging.DEBUG)  # фильтрацию выполняют обработчики
    logger.handlers.clear()  # защита от дублей при повторном вызове
    logger.propagate = False
    for handler in (console_handler, info_handler, error_handler):
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Вернуть дочерний логгер модуля, например logwatch.cli."""
    return logging.getLogger(f"{APP_LOGGER_NAME}.{name}")
