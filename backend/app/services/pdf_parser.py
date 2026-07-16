from __future__ import annotations

import logging
import multiprocessing
from queue import Empty
from pathlib import Path
from typing import Any

import fitz

from app.core.config import get_settings
from app.core.exceptions import PDFParseError


logger = logging.getLogger("paperhub.upload")


def _extract_pdf_text(pdf_path: str, result_queue: Any) -> None:
    try:
        with fitz.open(pdf_path) as document:
            content = "\n".join(page.get_text() for page in document).strip()
        result_queue.put((True, content))
    except Exception as exc:
        result_queue.put((False, repr(exc)))


def _parse_pdf_once(path: Path, timeout_seconds: float) -> str:
    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue(maxsize=1)
    process = context.Process(
        target=_extract_pdf_text,
        args=(str(path), result_queue),
        daemon=True,
    )
    process.start()

    try:
        succeeded, payload = result_queue.get(timeout=timeout_seconds)
    except Empty as exc:
        process.terminate()
        process.join(timeout=2)
        result_queue.cancel_join_thread()
        result_queue.close()
        raise PDFParseError(
            f"PDF parsing timed out after {timeout_seconds} seconds"
        ) from exc

    process.join(timeout=2)
    if process.is_alive():
        process.terminate()
        process.join(timeout=2)
    result_queue.close()

    if not succeeded:
        raise PDFParseError(f"PDF parsing failed: {payload}")
    return str(payload)


def parse_pdf(pdf_path: str | Path) -> str:
    settings = get_settings()
    path = Path(pdf_path).expanduser().resolve()
    if not path.is_file():
        raise PDFParseError("PDF file does not exist")

    for attempt in range(settings.pdf_parse_retries + 1):
        try:
            return _parse_pdf_once(path, settings.pdf_parse_timeout_seconds)
        except PDFParseError:
            logger.exception(
                "PDF parse attempt failed path=%s attempt=%s",
                path,
                attempt + 1,
            )
            if attempt >= settings.pdf_parse_retries:
                raise

    raise PDFParseError("PDF parsing failed")
