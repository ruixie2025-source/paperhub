from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.paper import Paper
from app.schemas.paper import PaperCreate, PaperUpdate

METADATA_FIELDS = ("title", "authors", "journal", "year", "doi", "abstract", "keywords")


def create_paper(db: Session, paper_data: PaperCreate) -> Paper:
    paper = Paper(**paper_data.model_dump())
    db.add(paper)
    db.commit()
    db.refresh(paper)
    return paper


def get_paper(db: Session, paper_id: int) -> Paper | None:
    return db.get(Paper, paper_id)


def list_papers(db: Session, skip: int = 0, limit: int = 100) -> list[Paper]:
    statement = select(Paper).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def search_papers(db: Session, keyword: str, skip: int = 0, limit: int = 100) -> list[Paper]:
    pattern = f"%{keyword}%"
    statement = (
        select(Paper)
        .where(
            or_(
                Paper.title.like(pattern),
                Paper.authors.like(pattern),
                Paper.journal.like(pattern),
                Paper.keywords.like(pattern),
            )
        )
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())


def update_paper(db: Session, paper_id: int, paper_data: PaperUpdate) -> Paper | None:
    paper = get_paper(db, paper_id)
    if paper is None:
        return None

    for field, value in paper_data.model_dump(exclude_unset=True).items():
        setattr(paper, field, value)

    db.commit()
    db.refresh(paper)
    return paper


def update_paper_pdf_path(db: Session, paper_id: int, pdf_path: str) -> Paper | None:
    paper = get_paper(db, paper_id)
    if paper is None:
        return None

    paper.pdf_path = pdf_path
    db.commit()
    db.refresh(paper)
    return paper


def update_paper_pdf_content(
    db: Session,
    paper_id: int,
    pdf_path: str,
    content: str,
) -> Paper | None:
    paper = get_paper(db, paper_id)
    if paper is None:
        return None

    paper.pdf_path = pdf_path
    paper.content = content
    db.commit()
    db.refresh(paper)
    return paper


def update_empty_paper_metadata(
    db: Session,
    paper_id: int,
    metadata: dict[str, object],
) -> Paper | None:
    paper = get_paper(db, paper_id)
    if paper is None:
        return None

    for field in METADATA_FIELDS:
        value = metadata.get(field)
        if value is None:
            continue

        if isinstance(value, str):
            value = value.strip()
            if not value:
                continue

        current_value = getattr(paper, field)
        is_empty_text = isinstance(current_value, str) and not current_value.strip()
        if current_value is None or is_empty_text:
            setattr(paper, field, value)

    db.commit()
    db.refresh(paper)
    return paper


def replace_paper_metadata(
    db: Session,
    paper_id: int,
    metadata: dict[str, object],
) -> Paper | None:
    paper = get_paper(db, paper_id)
    if paper is None:
        return None

    for field in METADATA_FIELDS:
        value = metadata.get(field)
        if value is None:
            continue

        if isinstance(value, str):
            value = value.strip()
            if not value:
                continue

        setattr(paper, field, value)

    db.commit()
    db.refresh(paper)
    return paper


def delete_paper(db: Session, paper_id: int) -> Paper | None:
    paper = get_paper(db, paper_id)
    if paper is None:
        return None

    db.delete(paper)
    db.commit()
    return paper
