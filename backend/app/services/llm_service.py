from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_AI_PROVIDER = "deepseek"
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com/chat/completions"


def get_ai_provider() -> str:
    return os.getenv("AI_PROVIDER", DEFAULT_AI_PROVIDER).strip().lower()


def get_deepseek_model() -> str:
    return os.getenv("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL).strip()


def get_deepseek_base_url() -> str:
    return os.getenv("DEEPSEEK_BASE_URL", DEFAULT_DEEPSEEK_BASE_URL).strip()


def ensure_deepseek_api_key() -> str:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is required")
    return api_key


def call_deepseek(prompt: str) -> str:
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

    try:
        with urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API error: {exc.code} {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"DeepSeek API request failed: {exc.reason}") from exc

    data = json.loads(response_body)
    return data["choices"][0]["message"]["content"].strip()


def generate_answer(prompt: str) -> str:
    provider = get_ai_provider()
    if provider != "deepseek":
        raise RuntimeError(f"Unsupported AI_PROVIDER: {provider}")

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
    return parse_json_response(generate_answer(json_prompt))
