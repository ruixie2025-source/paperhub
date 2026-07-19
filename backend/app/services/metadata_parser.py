from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel

from app.services.llm_service import generate_json


MAX_METADATA_CHARS = 6000
MIN_CHINESE_CHARACTERS = 20


class ExtractedMetadata(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[str] = None


def detect_primary_language(content: str) -> str:
    chinese_count = sum("\u4e00" <= character <= "\u9fff" for character in content)
    latin_count = sum(character.isascii() and character.isalpha() for character in content)
    if chinese_count >= MIN_CHINESE_CHARACTERS and chinese_count * 4 >= latin_count:
        return "Chinese"
    return "non-Chinese"


def extract_metadata(content: str) -> dict[str, Any]:
    source_text = content[:MAX_METADATA_CHARS]
    primary_language = detect_primary_language(source_text)
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
- The detected primary language is {primary_language}. Verify this against the PDF text.
- Preserve the original language and exact wording. Never translate metadata.
- For a Chinese paper, return the Chinese title, Chinese author names, Chinese journal,
  Chinese abstract, and Chinese keywords whenever those versions appear in the PDF.
- When both Chinese and English versions exist, prefer the version matching the paper's
  primary language.
- Never transliterate Chinese author names into Pinyin when Chinese names are available.

PDF text:
{source_text}
""".strip()

    metadata = ExtractedMetadata.model_validate(generate_json(prompt))
    return metadata.model_dump()
