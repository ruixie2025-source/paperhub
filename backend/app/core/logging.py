from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from app.core.config import get_settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    settings = get_settings()
    formatter = JsonFormatter()

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    try:
        log_dir = settings.resolve_path(settings.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                log_dir / "paperhub.log",
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
        )
    except OSError:
        pass

    for handler in handlers:
        handler.setFormatter(formatter)

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        handlers=handlers,
        force=True,
    )
