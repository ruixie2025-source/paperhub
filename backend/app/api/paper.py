from __future__ import annotations

import logging
from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import PDFParseError
from app.core.paths import UPLOAD_DIR
from app.core.rate_limit import limiter
from app.db.session import SessionLocal
from app.schemas.paper import PaperCreate, PaperResponse, PaperUpdate
from app.services.metadata_parser import extract_metadata
from app.services.paper_analysis_record_service import delete_analysis_records_for_paper
from app.services.pdf_parser import parse_pdf
from app.services.vector_store import delete_paper_index, reindex_paper
from app.services import paper_service


router = APIRouter(prefix="/papers", tags=["papers"])
settings = get_settings()
logger = logging.getLogger("paperhub.upload")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

PDF_CHUNK_BYTES = 1024 * 1024
ALLOWED_PDF_CONTENT_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/octet-stream",
}


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
def create_paper(paper_data: PaperCreate, db: Session = Depends(get_db)) -> PaperResponse:
    return paper_service.create_paper(db, paper_data)


@router.get("", response_model=list[PaperResponse])
def list_papers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[PaperResponse]:
    return paper_service.list_papers(db, skip=skip, limit=limit)


@router.get("/search", response_model=list[PaperResponse])
def search_papers(
    keyword: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[PaperResponse]:
    if not keyword.strip():
        return paper_service.list_papers(db, skip=skip, limit=limit)
    return paper_service.search_papers(db, keyword=keyword.strip(), skip=skip, limit=limit)


def save_uploaded_pdf(file: UploadFile) -> tuple[Path, str]:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    if file.content_type and file.content_type not in ALLOWED_PDF_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must be a PDF",
        )

    filename = f"{uuid4()}.pdf"
    file_path = UPLOAD_DIR / filename

    total_bytes = 0
    try:
        with file_path.open("wb") as uploaded_file:
            while chunk := file.file.read(PDF_CHUNK_BYTES):
                if total_bytes == 0 and b"%PDF-" not in chunk[:1024]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="The uploaded file is not a valid PDF",
                    )

                total_bytes += len(chunk)
                if total_bytes > settings.upload_max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"PDF files must not exceed {settings.upload_max_mb} MB",
                    )
                uploaded_file.write(chunk)
    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    if total_bytes == 0:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF is empty",
        )

    logger.info("PDF saved filename=%s size_bytes=%s", filename, total_bytes)
    return file_path, filename


def delete_uploaded_pdf(pdf_path: str | None) -> None:
    if not pdf_path or not pdf_path.startswith("/files/"):
        return

    candidate = (UPLOAD_DIR / Path(pdf_path).name).resolve()
    if candidate.parent != UPLOAD_DIR.resolve():
        return
    candidate.unlink(missing_ok=True)


def parse_uploaded_pdf(file_path: Path) -> str:
    try:
        return parse_pdf(file_path)
    except PDFParseError:
        file_path.unlink(missing_ok=True)
        raise


def extract_pdf_metadata(content: str) -> dict[str, object]:
    try:
        return extract_metadata(content)
    except Exception as exc:
        logger.warning("Metadata extraction skipped error=%s", exc)
        return {}


def fallback_title(file: UploadFile) -> str:
    if file.filename:
        return Path(file.filename).stem or "Untitled paper"
    return "Untitled paper"


@router.post("/import", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.upload_rate_limit)
def import_paper_pdf(
    request: Request,
    file: UploadFile,
    db: Session = Depends(get_db),
) -> PaperResponse:
    file_path, filename = save_uploaded_pdf(file)
    content = parse_uploaded_pdf(file_path)
    metadata = extract_pdf_metadata(content)

    paper = paper_service.create_paper(
        db,
        PaperCreate(
            title="",
            authors="",
            journal="",
            keywords="",
            pdf_path=None,
        ),
    )
    paper = paper_service.update_paper_pdf_content(
        db,
        paper.id,
        f"/files/{filename}",
        content,
    )
    if paper is None:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create paper",
        )
    if metadata:
        paper = paper_service.update_empty_paper_metadata(db, paper.id, metadata) or paper
    if not paper.title.strip():
        paper = paper_service.update_paper(
            db,
            paper.id,
            PaperUpdate(title=fallback_title(file)),
        ) or paper
    reindex_paper(paper)
    logger.info("PDF imported paper_id=%s filename=%s", paper.id, filename)
    return paper


@router.get("/{paper_id}", response_model=PaperResponse)
def get_paper(paper_id: int, db: Session = Depends(get_db)) -> PaperResponse:
    paper = paper_service.get_paper(db, paper_id)
    if paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )
    return paper


@router.post("/{paper_id}/upload", response_model=PaperResponse)
@limiter.limit(settings.upload_rate_limit)
def upload_paper_pdf(
    request: Request,
    paper_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
) -> PaperResponse:
    existing_paper = paper_service.get_paper(db, paper_id)
    if existing_paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )
    previous_pdf_path = existing_paper.pdf_path

    file_path, filename = save_uploaded_pdf(file)
    content = parse_uploaded_pdf(file_path)
    metadata = extract_pdf_metadata(content)

    paper = paper_service.update_paper_pdf_content(
        db,
        paper_id,
        f"/files/{filename}",
        content,
    )
    if paper is None:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )
    if metadata:
        paper = paper_service.update_empty_paper_metadata(db, paper_id, metadata) or paper
    reindex_paper(paper)
    if previous_pdf_path != paper.pdf_path:
        delete_uploaded_pdf(previous_pdf_path)
    logger.info("PDF uploaded paper_id=%s filename=%s", paper.id, filename)
    return paper


@router.put("/{paper_id}", response_model=PaperResponse)
def update_paper(
    paper_id: int,
    paper_data: PaperUpdate,
    db: Session = Depends(get_db),
) -> PaperResponse:
    paper = paper_service.update_paper(db, paper_id, paper_data)
    if paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )
    return paper


@router.delete("/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paper(paper_id: int, db: Session = Depends(get_db)) -> Response:
    existing_paper = paper_service.get_paper(db, paper_id)
    if existing_paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )
    pdf_path = existing_paper.pdf_path

    delete_analysis_records_for_paper(db, paper_id)
    paper = paper_service.delete_paper(db, paper_id)
    if paper is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found",
        )

    delete_paper_index(paper_id)
    delete_uploaded_pdf(pdf_path)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
