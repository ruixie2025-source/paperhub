from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.chat import router as chat_router
from app.api.paper import router as paper_router
from app.api.paper_analysis_record import router as paper_analysis_record_router
from app.api.paper_analysis import router as paper_analysis_router
from app.core.config import get_settings
from app.core.exception_handlers import (
    ai_service_exception_handler,
    pdf_parse_exception_handler,
    unhandled_exception_handler,
)
from app.core.exceptions import AIServiceError, PDFParseError
from app.core.logging import configure_logging
from app.core.paths import UPLOAD_DIR
from app.core.rate_limit import limiter
from app.core.request_logging import RequestLoggingMiddleware
from app.db.init_db import init_db
from app.services.health_service import get_health_status


configure_logging()
logger = logging.getLogger("paperhub")
settings = get_settings()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    logger.info(
        "PaperHub started environment=%s version=%s",
        settings.app_environment,
        settings.app_version,
    )
    yield
    logger.info("PaperHub stopped")


app = FastAPI(title="PaperHub API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(AIServiceError, ai_service_exception_handler)
app.add_exception_handler(PDFParseError, pdf_parse_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_host_list,
)
if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")
app.include_router(chat_router)
app.include_router(paper_analysis_record_router)
app.include_router(paper_analysis_router)
app.include_router(paper_router)


@app.get("/health")
def health_check() -> JSONResponse:
    health_status, payload = get_health_status()
    status_code = 503 if health_status == "unhealthy" else 200
    return JSONResponse(status_code=status_code, content=payload)
