from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.paper_analysis import PaperAnalysisRecord
from app.schemas.paper_analysis import PaperAnalysisResponse


def create_analysis_record(
    db: Session,
    analysis: PaperAnalysisResponse,
) -> PaperAnalysisRecord:
    record = PaperAnalysisRecord(
        paper_id=analysis.paper_id,
        title=analysis.title,
        purpose=analysis.purpose,
        research_question=analysis.research_question,
        value=analysis.value,
        method=analysis.method,
        keywords=analysis.keywords,
        research_design=analysis.research_design,
        findings=analysis.findings,
        logic=analysis.logic,
        variables=analysis.variables,
        application_value=analysis.application_value,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_latest_analysis_records(
    db: Session,
    paper_ids: list[int] | None = None,
) -> list[PaperAnalysisRecord]:
    statement = select(PaperAnalysisRecord).order_by(
        PaperAnalysisRecord.paper_id,
        PaperAnalysisRecord.created_at.desc(),
    )
    if paper_ids:
        statement = statement.where(PaperAnalysisRecord.paper_id.in_(paper_ids))

    records = list(db.scalars(statement).all())
    latest_by_paper_id: dict[int, PaperAnalysisRecord] = {}
    for record in records:
        latest_by_paper_id.setdefault(record.paper_id, record)
    return list(latest_by_paper_id.values())


def cleanup_old_analysis_records(db: Session, days: int = 30) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    statement = delete(PaperAnalysisRecord).where(PaperAnalysisRecord.created_at < cutoff)
    result = db.execute(statement)
    db.commit()
    return int(result.rowcount or 0)


def delete_analysis_records_for_paper(db: Session, paper_id: int) -> int:
    statement = delete(PaperAnalysisRecord).where(PaperAnalysisRecord.paper_id == paper_id)
    result = db.execute(statement)
    db.commit()
    return int(result.rowcount or 0)
