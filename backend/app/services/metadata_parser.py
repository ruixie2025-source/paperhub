from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel

from app.services.llm_service import generate_json


MAX_METADATA_CHARS = 6000


class ExtractedMetadata(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[str] = None


def extract_metadata(content: str) -> dict[str, Any]:
    source_text = content[:MAX_METADATA_CHARS]
    prompt = f"""
Extract paper metadata from the PDF text below.

Return only structured JSON. Do not return Markdown, explanations, or code fences.

Fields to extract:
- title
- authors
- journal
- year
- doi
- abstract
- keywords

Rules:
- Use null when a field cannot be found.
- Return authors as one string.
- Return keywords as one string.
- Return year as an integer when available.

PDF text:
{source_text}
""".strip()

    metadata = ExtractedMetadata.model_validate(generate_json(prompt))
    return metadata.model_dump()
