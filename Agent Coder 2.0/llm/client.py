"""Shared OpenAI-compatible LLM client abstraction for real Kilo usage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from openai import OpenAI

from config import AppConfig


class LLMClientError(RuntimeError):
    """Raised when the shared LLM client cannot complete a request."""


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


class OpenAICompatibleLLMClient:
    def __init__(self, *, api_key: str, base_url: str | None = None, request_timeout: float = 60.0):
        kwargs: dict[str, Any] = {"api_key": api_key, "timeout": request_timeout}
        if base_url:
            kwargs["base_url"] = base_url
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
    ) -> str:
        import time

        last_error = None
        for attempt in range(retries):
            try:
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
                return ""
            except Exception as exc:
                last_error = exc
                if attempt < retries - 1:
                    wait_time = min(2.0 ** attempt, 8.0)
                    time.sleep(wait_time)
                else:
                    raise LLMClientError(f"LLM request to model {model} failed after {retries} retries: {exc}") from exc

        return ""


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

