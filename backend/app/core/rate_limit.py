from fastapi import Request
from slowapi import Limiter

from app.core.config import get_settings


def get_client_identifier(request: Request) -> str:
    settings = get_settings()
    if settings.trust_proxy_headers:
        forwarded_for = request.headers.get("x-forwarded-for", "")
        if forwarded_for:
            return forwarded_for.split(",", maxsplit=1)[0].strip()

    if request.client is None:
        return "unknown"
    return request.client.host


limiter = Limiter(
    key_func=get_client_identifier,
    storage_uri=get_settings().rate_limit_storage_uri,
)
