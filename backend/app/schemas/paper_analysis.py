from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PaperAnalysisRequest(BaseModel):
    paper_ids: list[int] = Field(min_length=1)


class PaperAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    paper_id: int
    title: str
    purpose: str
    research_question: str
    value: str
    method: str
    keywords: str
    research_design: str
    findings: str
    logic: str
    variables: str
    application_value: str
    created_at: Optional[datetime] = None


class PaperAnalysisCleanupResponse(BaseModel):
    deleted_count: int
