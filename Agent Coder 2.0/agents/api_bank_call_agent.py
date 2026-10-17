"""API-Bank call generation stage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.requirement_analyzer import RequirementAnalysis
from llm.client import ChatMessage


@dataclass
class GeneratedAPICall:
    raw_response: str
    model: str


class APIBankCallAgent:
    def __init__(self, *, client: Any, model: str) -> None:
        self.client = client
        self.model = model

    def generate(
        self,
        problem: Any,
        requirements: RequirementAnalysis,
    ) -> GeneratedAPICall:
        response = self.client.chat(
            messages=[
                ChatMessage(
                    role="system",
                    content=(
                        "You are an API-Bank tool-calling assistant. Return exactly one "
                        "API call requested by the task. Do not return Python source code, "
                        "tests, markdown, or an explanation."
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        f"{problem.prompt}\n\n"
                        "Requirement analysis:\n"
                        f"{requirements.summary}\n\n"
                        "Return the call using the dataset's exact format: "
                        "[ApiName(parameter='value')]."
                    ),
                ),
            ],
            model=self.model,
            temperature=0,
            max_tokens=512,
            retries=3,
        )
        return GeneratedAPICall(raw_response=response, model=self.model)
