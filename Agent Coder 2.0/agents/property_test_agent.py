"""Property-based test generator driven by the formal specification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.common import extract_code_block, load_prompt, normalize_whitespace
from dataset.mbpp_loader import MBPPProblem
from llm.client import ChatMessage


@dataclass
class GeneratedPropertyTests:
    code: str
    raw_response: str
    model: str


class PropertyTestAgent:
    def __init__(self, *, client, model: str) -> None:
        self.client = client
        self.model = model

    def generate(self, problem: Any, formal_spec: dict[str, Any]) -> GeneratedPropertyTests:
        prompt = load_prompt("property_test_prompt.txt").format(
            task_text=getattr(problem, "text", getattr(problem, "prompt", str(problem))),
            entry_point=getattr(problem, "entry_point", None) or "solution",
            formal_spec=formal_spec,
        )
        response = self.client.chat(
            messages=[
                ChatMessage(role="system", content="You are a property-based tester using Hypothesis."),
                ChatMessage(role="user", content=prompt),
            ],
            model=self.model,
            temperature=0.2,
            max_tokens=4096,
        )
        return GeneratedPropertyTests(code=normalize_whitespace(extract_code_block(response)), raw_response=response, model=self.model)
