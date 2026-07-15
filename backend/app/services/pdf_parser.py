from __future__ import annotations

from pathlib import Path

import fitz


def parse_pdf(pdf_path: str | Path) -> str:
    path = Path(pdf_path)
    with fitz.open(path) as document:
        return "\n".join(page.get_text() for page in document).strip()
