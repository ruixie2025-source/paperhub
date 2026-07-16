from __future__ import annotations

import logging
import socket
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine
from app.services.vector_store import get_chroma_client


logger = logging.getLogger("paperhub.health")


def check_sqlite() -> dict[str, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        logger.exception("SQLite health check failed")
        return {"status": "error"}


def check_chroma() -> dict[str, str]:
    try:
        get_chroma_client().heartbeat()
        return {"status": "ok"}
    except Exception:
        logger.exception("ChromaDB health check failed")
        return {"status": "error"}


def check_deepseek() -> dict[str, str]:
    settings = get_settings()
    if not settings.get_deepseek_api_key():
        return {"status": "not_configured"}
    if not settings.healthcheck_deepseek_network:
        return {"status": "configured"}

    parsed_url = urlparse(settings.deepseek_base_url)
    host = parsed_url.hostname
    if not host:
        return {"status": "error"}

    port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
    try:
        with socket.create_connection(
            (host, port),
            timeout=settings.healthcheck_timeout_seconds,
        ):
            return {"status": "reachable"}
    except OSError:
        logger.warning("DeepSeek network health check failed host=%s port=%s", host, port)
        return {"status": "unreachable"}


def get_health_status() -> tuple[str, dict[str, Any]]:
    settings = get_settings()
    checks = {
        "sqlite": check_sqlite(),
        "chroma": check_chroma(),
        "deepseek": check_deepseek(),
    }

    local_failed = any(
        checks[name]["status"] == "error" for name in ("sqlite", "chroma")
    )
    deepseek_failed = checks["deepseek"]["status"] in {
        "error",
        "unreachable",
        "not_configured",
    }
    production = settings.app_environment.lower() == "production"

    if local_failed or (production and deepseek_failed):
        overall_status = "unhealthy"
    elif deepseek_failed:
        overall_status = "degraded"
    else:
        overall_status = "ok"

    return overall_status, {
        "status": overall_status,
        "version": settings.app_version,
        "checks": checks,
    }
