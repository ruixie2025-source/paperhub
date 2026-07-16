from __future__ import annotations

import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import AIServiceError, PDFParseError


logger = logging.getLogger("paperhub.error")
AI_UNAVAILABLE_MESSAGE = "AI 服务暂时不可用，请稍后再试。"


async def ai_service_exception_handler(
    request: Request,
    exc: AIServiceError,
) -> JSONResponse:
    logger.error(
        "AI service failed method=%s path=%s error=%s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": AI_UNAVAILABLE_MESSAGE},
    )


async def pdf_parse_exception_handler(
    request: Request,
    exc: PDFParseError,
) -> JSONResponse:
    logger.error(
        "PDF parsing failed method=%s path=%s error=%s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "PDF 解析失败，请确认文件有效后重试。"},
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "Unhandled exception request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "服务器内部错误，请稍后再试。",
            "request_id": request_id,
        },
    )
