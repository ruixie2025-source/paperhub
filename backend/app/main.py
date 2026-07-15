from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.chat import router as chat_router
from app.api.paper import router as paper_router
from app.api.paper import UPLOAD_DIR
from app.api.paper_analysis_record import router as paper_analysis_record_router
from app.api.paper_analysis import router as paper_analysis_router
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="PaperHub API", lifespan=lifespan)
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")
app.include_router(chat_router)
app.include_router(paper_analysis_record_router)
app.include_router(paper_analysis_router)
app.include_router(paper_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
