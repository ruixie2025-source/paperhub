from __future__ import annotations

import json
import logging
from time import sleep
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import get_settings
from app.core.exceptions import AIServiceError


logger = logging.getLogger("paperhub.ai")


def get_ai_provider() -> str:
    return get_settings().ai_provider.strip().lower()


def get_deepseek_model() -> str:
    return get_settings().deepseek_model.strip()


def get_deepseek_base_url() -> str:
    return get_settings().deepseek_base_url.strip()


def ensure_deepseek_api_key() -> str:
    api_key = get_settings().get_deepseek_api_key()
    if not api_key:
        logger.error("DeepSeek API key is not configured")
        raise AIServiceError("AI service is not configured")
    return api_key


def perform_deepseek_request(request: Request) -> str:
    settings = get_settings()
    try:
        with urlopen(request, timeout=settings.deepseek_timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        logger.error(
            "DeepSeek HTTP error status=%s body=%s",
            exc.code,
            error_body,
        )
        raise
    except URLError as exc:
        logger.exception("DeepSeek network request failed: %s", exc.reason)
        raise

    try:
        data = json.loads(response_body)
        content = data["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            raise TypeError("DeepSeek content is not text")
        return content.strip()
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        logger.error("DeepSeek returned an invalid response body=%s", response_body)
        raise


def call_deepseek(prompt: str) -> str:
    settings = get_settings()
    api_key = ensure_deepseek_api_key()
    payload = {
        "model": get_deepseek_model(),
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0,
    }
    request = Request(
        get_deepseek_base_url(),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    for attempt in range(settings.deepseek_max_retries + 1):
        try:
            return perform_deepseek_request(request)
        except HTTPError as exc:
            retryable = exc.code == 429 or exc.code >= 500
            if not retryable or attempt >= settings.deepseek_max_retries:
                break
        except (
            URLError,
            TimeoutError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
        ):
            if attempt >= settings.deepseek_max_retries:
                break

        delay = settings.deepseek_retry_backoff_seconds * (2**attempt)
        logger.warning(
            "Retrying DeepSeek request attempt=%s delay_seconds=%s",
            attempt + 2,
            delay,
        )
        sleep(delay)

    logger.error(
        "DeepSeek request exhausted retries model=%s attempts=%s",
        get_deepseek_model(),
        settings.deepseek_max_retries + 1,
    )
    raise AIServiceError("AI provider request failed")


def generate_answer(prompt: str) -> str:
    provider = get_ai_provider()
    if provider != "deepseek":
        logger.error("Unsupported AI provider: %s", provider)
        raise AIServiceError("AI provider is not supported")

    return call_deepseek(prompt)


def parse_json_response(text: str) -> dict[str, Any]:
    cleaned_text = text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text.removeprefix("```json").removesuffix("```").strip()
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.removeprefix("```").removesuffix("```").strip()

    data = json.loads(cleaned_text)
    if not isinstance(data, dict):
        raise ValueError("LLM JSON response must be an object")
    return data


def generate_json(prompt: str) -> dict[str, Any]:
    json_prompt = f"""
{prompt}

Return only valid JSON. Do not return Markdown, explanations, or code fences.
""".strip()
    response = generate_answer(json_prompt)
    try:
        return parse_json_response(response)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("DeepSeek returned invalid JSON response=%s", response)
        raise AIServiceError("AI provider returned invalid JSON") from exc
