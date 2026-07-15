from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PaperAnalysisRecord(Base):
    __tablename__ = "paper_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    purpose: Mapped[str] = mapped_column(Text, nullable=False, default="")
    research_question: Mapped[str] = mapped_column(Text, nullable=False, default="")
    value: Mapped[str] = mapped_column(Text, nullable=False, default="")
    method: Mapped[str] = mapped_column(Text, nullable=False, default="")
    keywords: Mapped[str] = mapped_column(Text, nullable=False, default="")
    research_design: Mapped[str] = mapped_column(Text, nullable=False, default="")
    findings: Mapped[str] = mapped_column(Text, nullable=False, default="")
    logic: Mapped[str] = mapped_column(Text, nullable=False, default="")
    variables: Mapped[str] = mapped_column(Text, nullable=False, default="")
    application_value: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
