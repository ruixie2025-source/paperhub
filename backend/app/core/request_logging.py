from __future__ import annotations

import logging
from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


logger = logging.getLogger("paperhub.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = request_id
        started_at = perf_counter()

        response = await call_next(request)
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%s client=%s",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            client_host,
        )
        response.headers["X-Request-ID"] = request_id
        return response
