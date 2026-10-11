"""Unit-test generator that consumes the formal specification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.common import extract_code_block, load_prompt, normalize_whitespace
from dataset.mbpp_loader import MBPPProblem
from llm.client import ChatMessage


@dataclass
class GeneratedUnitTests:
    code: str
    raw_response: str
    model: str


class UnitTestAgent:
    def __init__(self, *, client, model: str) -> None:
        self.client = client
        self.model = model

    def generate(
        self,
        problem: Any,
        *,
        implementation_code: str = "",
        requirements_summary: str = "",
    ) -> GeneratedUnitTests:
        prompt = load_prompt("unit_test_prompt.txt").format(
            task_text=getattr(problem, "text", getattr(problem, "prompt", str(problem))),
            entry_point=getattr(problem, "entry_point", None) or "solution",
            implementation_code=implementation_code or "",
            requirements_summary=requirements_summary or "",
        )
        response = self.client.chat(
            messages=[
                ChatMessage(role="system", content="You are a tester who writes independent unit tests."),
                ChatMessage(role="user", content=prompt),
            ],
            model=self.model,
            temperature=0.2,
            max_tokens=4096,
        )
        return GeneratedUnitTests(code=normalize_whitespace(extract_code_block(response)), raw_response=response, model=self.model)
