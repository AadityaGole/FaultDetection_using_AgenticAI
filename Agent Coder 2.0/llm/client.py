"""Shared OpenAI-compatible LLM client abstraction for real Kilo usage."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import time
from typing import Any, Callable, Sequence

from openai import OpenAI

from config import AppConfig


class LLMClientError(RuntimeError):
    """Raised when the shared LLM client cannot complete a request."""


class LLMEmptyResponseError(LLMClientError):
    """Raised when the provider returns no message content after all retries."""


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


class OpenAICompatibleLLMClient:
    def __init__(self, *, api_key: str, base_url: str | None = None, request_timeout: float = 60.0):
        kwargs: dict[str, Any] = {"api_key": api_key, "timeout": request_timeout}
        if base_url:
            kwargs["base_url"] = base_url
        kwargs["max_retries"] = 0
        self._client = OpenAI(**kwargs)
        self.request_timeout = request_timeout

    def chat(
        self,
        *,
        messages: Sequence[ChatMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 4096,
        retries: int = 3,
        request_hook: Callable[[], None] | None = None,
    ) -> str:
        if retries < 1:
            raise ValueError("retries must be at least 1")

        for attempt in range(retries):
            try:
                if request_hook is not None:
                    request_hook()
                response = self._client.chat.completions.create(
                    model=model,
                    messages=[{"role": message.role, "content": message.content} for message in messages],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                choice = response.choices[0]
                content = choice.message.content or ""
                content = content.strip()
                if content:
                    return content
                # If empty response on free/shared model, retry once after short pause
                if attempt < retries - 1:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise LLMEmptyResponseError(
                    f"LLM request to model {model} returned empty content after {retries} attempts."
                )
            except Exception as exc:
                if isinstance(exc, LLMEmptyResponseError):
                    raise
                if attempt < retries - 1:
                    wait_time = self._retry_after_seconds(exc)
                    if wait_time is None:
                        wait_time = min(2.0 ** attempt, 8.0)
                    time.sleep(wait_time)
                else:
                    raise LLMClientError(f"LLM request to model {model} failed after {retries} retries: {exc}") from exc

        raise LLMClientError(f"LLM request to model {model} did not complete.")

    @staticmethod
    def _retry_after_seconds(exc: Exception) -> float | None:
        response = getattr(exc, "response", None)
        headers = getattr(response, "headers", None) or {}
        retry_after_ms = headers.get("retry-after-ms")
        if retry_after_ms is not None:
            try:
                return max(0.0, float(retry_after_ms) / 1000.0)
            except (TypeError, ValueError):
                pass

        retry_after = headers.get("retry-after")
        if retry_after is None:
            return None
        try:
            return max(0.0, float(retry_after))
        except (TypeError, ValueError):
            try:
                retry_at = parsedate_to_datetime(retry_after)
                if retry_at.tzinfo is None:
                    retry_at = retry_at.replace(tzinfo=timezone.utc)
                return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
            except (TypeError, ValueError, OverflowError):
                return None


def build_llm_client(config: AppConfig | None = None):
    config = config or AppConfig()
    provider = config.provider.lower()
    if provider == "mock":
        raise LLMClientError("Mock provider is disabled. Configure KILO_API_KEY and use the real Kilo provider.")
    if provider in {"kilo", "openai_compatible", "openai-compatible"}:
        if not config.kilo_api_key:
            raise LLMClientError("KILO_API_KEY is required for the configured provider.")
        timeout = getattr(config, "request_timeout_seconds", 45.0)
        return OpenAICompatibleLLMClient(api_key=config.kilo_api_key, base_url=config.kilo_base_url, request_timeout=timeout)
    raise LLMClientError(f"Unsupported LLM provider: {config.provider}")
