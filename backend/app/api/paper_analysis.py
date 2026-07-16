from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.db.session import SessionLocal
from app.schemas.paper_analysis import PaperAnalysisRequest, PaperAnalysisResponse
from app.services.paper_analysis_service import analyze_papers


router = APIRouter(prefix="/papers", tags=["paper-analysis"])
settings = get_settings()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/analyze", response_model=list[PaperAnalysisResponse])
@limiter.limit(settings.analysis_rate_limit)
def analyze_selected_papers(
    request: Request,
    analysis_request: PaperAnalysisRequest,
    db: Session = Depends(get_db),
) -> list[PaperAnalysisResponse]:
    results = analyze_papers(db, analysis_request.paper_ids)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )
    return results
