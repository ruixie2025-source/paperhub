from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import Any
from unittest.mock import patch

import fitz
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.exceptions import AIServiceError, PDFParseError
from app.core.rate_limit import limiter
from app.main import app
from app.services.pdf_parser import parse_pdf


def slow_pdf_parser(pdf_path: str, result_queue: Any) -> None:
    sleep(2)


def test_ai_errors_are_sanitized() -> None:
    limiter.reset()
    with patch(
        "app.api.chat.ask_question",
        side_effect=AIServiceError("private upstream error"),
    ):
        response = TestClient(app, raise_server_exceptions=False).post(
            "/chat",
            json={"question": "test"},
        )

    assert response.status_code == 503
    assert response.json() == {"detail": "AI 服务暂时不可用，请稍后再试。"}


def test_chat_rate_limit() -> None:
    limiter.reset()
    with patch(
        "app.api.chat.ask_question",
        return_value={"answer": "ok", "sources": []},
    ):
        client = TestClient(app)
        responses = [
            client.post("/chat", json={"question": "test"}) for _ in range(31)
        ]

    assert responses[29].status_code == 200
    assert responses[30].status_code == 429


def test_upload_rate_limit() -> None:
    limiter.reset()
    with patch("app.api.paper.paper_service.get_paper", return_value=None):
        client = TestClient(app)
        responses = [
            client.post(
                "/papers/999/upload",
                files={"file": ("test.pdf", b"%PDF-1.4", "application/pdf")},
            )
            for _ in range(6)
        ]

    assert responses[4].status_code == 404
    assert responses[5].status_code == 429


def test_pdf_parser_extracts_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "paper.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "PaperHub parser verification")
    document.save(pdf_path)
    document.close()

    settings = get_settings()
    previous_retries = settings.pdf_parse_retries
    previous_timeout = settings.pdf_parse_timeout_seconds
    settings.pdf_parse_retries = 0
    settings.pdf_parse_timeout_seconds = 10
    try:
        content = parse_pdf(pdf_path)
    finally:
        settings.pdf_parse_retries = previous_retries
        settings.pdf_parse_timeout_seconds = previous_timeout

    assert "PaperHub parser verification" in content


def test_pdf_parser_times_out(tmp_path: Path) -> None:
    pdf_path = tmp_path / "slow.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    settings = get_settings()
    previous_retries = settings.pdf_parse_retries
    previous_timeout = settings.pdf_parse_timeout_seconds
    settings.pdf_parse_retries = 0
    settings.pdf_parse_timeout_seconds = 0.1
    try:
        with patch("app.services.pdf_parser._extract_pdf_text", slow_pdf_parser):
            try:
                parse_pdf(pdf_path)
            except PDFParseError as exc:
                assert "timed out" in str(exc)
            else:
                raise AssertionError("Expected PDFParseError")
    finally:
        settings.pdf_parse_retries = previous_retries
        settings.pdf_parse_timeout_seconds = previous_timeout


if __name__ == "__main__":
    test_ai_errors_are_sanitized()
    test_chat_rate_limit()
    test_upload_rate_limit()
    with TemporaryDirectory() as temporary_directory:
        temporary_path = Path(temporary_directory)
        test_pdf_parser_extracts_text(temporary_path)
        test_pdf_parser_times_out(temporary_path)
    print("Production hardening checks passed")
