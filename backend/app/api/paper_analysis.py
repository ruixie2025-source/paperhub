from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.paper_analysis import PaperAnalysisRequest, PaperAnalysisResponse
from app.services.paper_analysis_service import analyze_papers


router = APIRouter(prefix="/papers", tags=["paper-analysis"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/analyze", response_model=list[PaperAnalysisResponse])
def analyze_selected_papers(
    request: PaperAnalysisRequest,
    db: Session = Depends(get_db),
) -> list[PaperAnalysisResponse]:
    results = analyze_papers(db, request.paper_ids)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )
    return results
