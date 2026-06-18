from __future__ import annotations
import json
import os
import re
import time
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from .call_metrics import record_call_metrics

load_dotenv()

DEFAULT_MODEL = "deepseek-chat"
DEFAULT_BASE_URL = "https://api.deepseek.com"

_client: OpenAI | None = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("Missing DEEPSEEK_API_KEY. Set it in .env or environment variables.")
        _client = OpenAI(api_key=api_key, base_url=os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL))
    return _client

def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)

def chat_completion(
    system: str,
    user: str,
    *,
    json_mode: bool = False,
    temperature: float = 0.0,
) -> str:
    client = get_client()
    kwargs: dict[str, Any] = {
        "model": os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    start = time.perf_counter()
    response = client.chat.completions.create(**kwargs)
    latency_ms = int((time.perf_counter() - start) * 1000)

    usage = response.usage
    tokens = usage.total_tokens if usage else 0
    record_call_metrics(tokens, latency_ms)

    content = response.choices[0].message.content or ""
    return content.strip()

def chat_json(system: str, user: str, *, retries: int = 2) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            content = chat_completion(system, user, json_mode=True)
            return _extract_json(content)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            last_error = exc
            if attempt == retries:
                break
    raise RuntimeError(f"Failed to parse JSON from LLM after {retries + 1} attempts") from last_error
