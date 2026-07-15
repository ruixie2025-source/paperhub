from collections.abc import Generator

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.paper_analysis import (
    PaperAnalysisCleanupResponse,
    PaperAnalysisRequest,
    PaperAnalysisResponse,
)
from app.services.paper_analysis_record_service import (
    cleanup_old_analysis_records,
    list_latest_analysis_records,
)


router = APIRouter(prefix="/paper-analyses", tags=["paper-analysis-records"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/latest", response_model=list[PaperAnalysisResponse])
def get_latest_analysis_records(
    request: PaperAnalysisRequest,
    db: Session = Depends(get_db),
) -> list[PaperAnalysisResponse]:
    return list_latest_analysis_records(db, request.paper_ids)


@router.delete("/cleanup", response_model=PaperAnalysisCleanupResponse)
def cleanup_analysis_records(
    days: int = 30,
    db: Session = Depends(get_db),
) -> PaperAnalysisCleanupResponse:
    deleted_count = cleanup_old_analysis_records(db, days=days)
    return PaperAnalysisCleanupResponse(deleted_count=deleted_count)
